﻿# encoding: utf-8

import os
import json
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import shutil
 
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
             
def _isArrayLike(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__len__')
 
 
class voc2coco:
    def __init__(self, src_path, coco_dataset_dir,year=None):
        self.classes = ('__background__',  
                        #'aeroplane', 'bicycle', 'bird', 'boat',
                        #'bottle', 'bus', 'car', 'cat', 'chair',
                        #'cow', 'diningtable', 'dog', 'horse',
                        #'motorbike', 'person', 'pottedplant',
                        #'sheep', 'sofa', 'train', 'tvmonitor'
                        'face',
                        'face_mask'
                        )
 
        self.num_classes = len(self.classes)
        self.data_path = src_path
        self.annotaions_path = os.path.join(self.data_path, 'Annotations')
        self.image_set_path = os.path.join(self.data_path, 'ImageSets')
        self.images_path = os.path.join(self.data_path, 'JPEGImages')
        self.year = year
        self.categories_to_ids_map = self._get_categories_to_ids_map()
        self.categories_msg = self._categories_msg_generator()
        
        self.save_path = os.path.join(os.path.dirname(self.data_path), coco_dataset_dir)
        self.save_anno_path = os.path.join(self.save_path, 'annotations')
        self.save_train_path = os.path.join(self.save_path, 'train2017')
        self.save_val_path = os.path.join(self.save_path, 'val2017')
        if not os.path.exists(self.save_anno_path):
            os.makedirs(self.save_anno_path)
        if not os.path.exists(self.save_train_path):
            os.makedirs(self.save_train_path)
        if not os.path.exists(self.save_val_path):
            os.makedirs(self.save_val_path)
 
    def _load_annotation(self, ids=[],img_set='train'):
        ids = ids if _isArrayLike(ids) else [ids]
        image_msg = []
        annotation_msg = []
        annotation_id = 1

        index = 0
        for filename in ids:
            index += 1
            json_file = os.path.join(self.data_path, 'Segmentation_json', filename + '.json')
            if os.path.exists(json_file):
                img_file = os.path.join(self.data_path, 'JPEGImages', filename + '.jpg')
                im = cv2.imread(img_file)
                width = im.shape[1]
                height = im.shape[0]
                seg_data = json.load(open(json_file, 'r'))
                assert type(seg_data) == type(dict()), 'annotation file format {} not supported'.format(type(seg_data))
                for shape in seg_data['shapes']:
                    seg_msg = []
                    for point in shape['points']:
                        seg_msg += point
                    one_ann_msg = {"segmentation": [seg_msg],
                                   "area": self._area_computer(shape['points']),
                                   "iscrowd": 0,
                                   "image_id": int(index),
                                   "bbox": self._points_to_mbr(shape['points']),
                                   "category_id": self.categories_to_ids_map[shape['label']],
                                   "id": annotation_id,
                                   "ignore": 0
                                   }
                    annotation_msg.append(one_ann_msg)
                    annotation_id += 1
            else:
                xml_file = os.path.join(self.annotaions_path, filename + '.xml')
                tree = ET.parse(xml_file)
                objs = tree.findall('object')          
                size = tree.find('size')
                if size is not None:
                    width = size.find('width').text
                    height = size.find('height').text
                else:
                    img_file = os.path.join(self.data_path, 'JPEGImages', filename + '.jpg')
                    im = cv2.imdecode(np.fromfile(img_file,dtype=np.uint8),cv2.IMREAD_COLOR)
                    width = im.shape[1]
                    height = im.shape[0]
                for obj in objs:
                    bndbox = obj.find('bndbox')
                    [xmin, xmax, ymin, ymax] \
                        = [int(bndbox.find('xmin').text) - 1, int(bndbox.find('xmax').text),
                           int(bndbox.find('ymin').text) - 1, int(bndbox.find('ymax').text)]
                    if xmin < 0:
                        xmin = 0
                    if ymin < 0:
                        ymin = 0
                    bbox = [xmin, xmax, ymin, ymax]
                    one_ann_msg = {"segmentation": self._bbox_to_mask(bbox),
                                   "area": self._bbox_area_computer(bbox),
                                   "iscrowd": 0,
                                   "image_id": int(index),
                                   "bbox": [xmin, ymin, xmax - xmin, ymax - ymin],
                                   "category_id": self.categories_to_ids_map[obj.find('name').text],
                                   "id": annotation_id,
                                   "ignore": 0
                                   }
                    annotation_msg.append(one_ann_msg)
                    annotation_id += 1
            one_image_msg = {"file_name": filename + ".jpg",
                             "height": int(height),
                             "width": int(width),
                             "id": int(index)
                             }
            image_msg.append(one_image_msg)
            
            img_file = os.path.join(self.images_path, filename + '.jpg')
            if img_set == 'train':
                dest_file = os.path.join(self.save_train_path,filename + '.jpg')
            else:
                dest_file = os.path.join(self.save_val_path,filename + '.jpg')
            shutil.copyfile(img_file,dest_file)
            
        return image_msg, annotation_msg
    
    def _bbox_to_mask(self, bbox):
        assert len(bbox) == 4, 'Wrong bndbox!'
        mask = [bbox[0], bbox[2], bbox[0], bbox[3], bbox[1], bbox[3], bbox[1], bbox[2]]
        return [mask]
    
    def _bbox_area_computer(self, bbox):
        width = bbox[1] - bbox[0]
        height = bbox[3] - bbox[2]
        return width * height
    
    def _save_json_file(self, filename=None, data=None):
        if not filename.endswith('.json'):
            filename += '.json'
        assert type(data) == type(dict()), 'data format {} not supported'.format(type(data))
        with open(os.path.join(self.save_anno_path, filename), 'w') as f:
            f.write(json.dumps(data,indent=4, cls=MyEncoder))
            
    def _get_categories_to_ids_map(self):
        return dict(zip(self.classes, range(self.num_classes)))
    
    def _get_all_indexs(self):
        ids = []
        for root, dirs, files in os.walk(self.annotaions_path, topdown=False):
            for f in files:
                if str(f).endswith('.xml'):
                    id = int(str(f).strip('.xml'))
                    ids.append(id)
        assert ids is not None, 'There is none xml file in {}'.format(self.annotaions_path)
        return ids
    
    def _get_indexs_by_image_set(self, image_set=None):
        if image_set is None:
            return self._get_all_indexs()
        else:
            image_set_path = os.path.join(self.image_set_path, 'Main', image_set + '.txt')
            assert os.path.exists(image_set_path), 'Path does not exist: {}'.format(image_set_path)
            with open(image_set_path) as f:
                ids = [x.strip() for x in f.readlines()]
            return ids
    
    def _points_to_mbr(self, points):
        assert _isArrayLike(points), 'Points should be array like!'
        x = [point[0] for point in points]
        y = [point[1] for point in points]
        assert len(x) == len(y), 'Wrong point quantity'
        xmin, xmax, ymin, ymax = min(x), max(x), min(y), max(y)
        height = ymax - ymin
        width = xmax - xmin
        return [xmin, ymin, width, height]
    
    def _categories_msg_generator(self):
        categories_msg = []
        for category in self.classes:
            if category == '__background__':
                continue
            one_categories_msg = {"supercategory": "none",
                                  "id": self.categories_to_ids_map[category],
                                  "name": category
                                  }
            categories_msg.append(one_categories_msg)
        return categories_msg
    
    def _area_computer(self, points):
        assert _isArrayLike(points), 'Points should be array like!'
        tmp_contour = []
        for point in points:
            tmp_contour.append([point])
        contour = np.array(tmp_contour, dtype=np.int32)
        area = cv2.contourArea(contour)
        return area
    
    def voc_to_coco_converter(self):
        img_sets = ['train', 'val']
        for img_set in img_sets:
            ids = self._get_indexs_by_image_set(img_set)
            img_msg, ann_msg = self._load_annotation(ids,img_set)
            result_json = {"images": img_msg,
                           "type": "instances",
                           "annotations": ann_msg,
                           "categories": self.categories_msg}
            self._save_json_file('instances_' + img_set+'2017', result_json)

def gen_voc2coco():
    
    converter = voc2coco('D:/work/AI/口罩识别/人脸口罩检测数据集/VOC2007-facemask-dataset','coco2017-facemask-dataset' ,'2007')
    converter.voc_to_coco_converter()
    
if __name__ == "__main__":
    gen_voc2coco()