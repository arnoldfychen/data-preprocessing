import argparse
import collections
import datetime
import glob
import json
import os
import os.path as osp
import sys

import numpy as np
import PIL.Image

import labelme
import shutil

'''
fychen 10/2019
Usage:   python labelme2cocoinst.py --labels labels-file input_dir output_dir
example: python labelme2coco2014inst.py --labels fire-labels.txt dataset1 cocodataset1
example: python labelme2coco2014inst.py --labels fire-labels.txt candle-dataset candle-cocodataset
'''

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
            
try:
    import pycocotools.mask
except ImportError:
    print('Please install pycocotools:\n\n    pip install pycocotools\n')
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_dir', help='input annotated directory')
    parser.add_argument('output_dir', help='output dataset directory')
    parser.add_argument('--labels', help='labels file', required=True)
    args = parser.parse_args()

    if osp.exists(args.output_dir):
        print('Output directory already exists:', args.output_dir)
        sys.exit(1)
    os.makedirs(args.output_dir)
    #os.makedirs(osp.join(args.output_dir, 'JPEGImages'))
    anno_path = osp.join(args.output_dir, 'annotations')
    imgs_path = osp.join(args.output_dir, 'images','train2014')
    valimgs_path = osp.join(args.output_dir, 'images','val2014')
    print(imgs_path)
    os.makedirs(anno_path)
    os.makedirs(imgs_path)
    os.makedirs(valimgs_path)
    print('Creating dataset:', args.output_dir)

    now = datetime.datetime.now()

    data = dict(
        info=dict(
            description=None,
            url=None,
            version=None,
            year=now.year,
            contributor=None,
            date_created=now.strftime('%Y-%m-%d %H:%M:%S.%f'),
        ),
        licenses=[dict(
            url=None,
            id=0,
            name=None,
        )],
        images=[
            # license, url, file_name, height, width, date_captured, id
        ],
        type='instances',
        annotations=[
            # segmentation, area, iscrowd, image_id, bbox, category_id, id
        ],
        categories=[
            # supercategory, id, name
        ],
    )

    class_name_to_id = {}
    for i, line in enumerate(open(args.labels).readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        if class_id == -1:
            assert class_name == '__ignore__'
            continue
        class_name_to_id[class_name] = class_id
        data['categories'].append(dict(
            supercategory=None,
            id=class_id,
            name=class_name,
        ))

    #out_ann_file = osp.join(args.output_dir, 'annotations.json')
    out_ann_file = osp.join(args.output_dir,'annotations', 'instances_train2014.json')
    out_valann_file = osp.join(args.output_dir,'annotations', 'instances_minival2014.json')
    label_files = glob.glob(osp.join(args.input_dir, '*.json'))
    for image_id, label_file in enumerate(label_files):
        
        #Arnold
        file_name_str = os.path.basename(label_file)
        file_name_str = file_name_str.split(".")[0]
        if file_name_str.isdigit():
            image_id=int(file_name_str)
        
        print('Generating dataset from:', label_file)
        with open(label_file) as f:
            label_data = json.load(f)
        #base = osp.splitext(osp.basename(label_file))[0]
        image_id_str = "{0:0>12}".format(image_id) 
        base = 'COCO_train2014_'+ image_id_str
        out_img_file = osp.join(
            #args.output_dir, 'JPEGImages', base + '.jpg'
            imgs_path, base + '.jpg'
        )
        base_val = 'COCO_val2014_'+ image_id_str
        out_valimg_file = osp.join(
            valimgs_path, base_val + '.jpg'
        )

        img_file = osp.join(
            osp.dirname(label_file), label_data['imagePath']
        )
        img = np.asarray(PIL.Image.open(img_file))
        PIL.Image.fromarray(img).save(out_img_file)
        PIL.Image.fromarray(img).save(out_valimg_file)
        data['images'].append(dict(
            license=0,
            url=None,
            file_name=osp.relpath(out_img_file, osp.dirname(out_ann_file)).replace("\\","/"),  #Arnold
            height=img.shape[0],
            width=img.shape[1],
            date_captured=None,
            id=image_id,
        ))

        masks = {}                                     # for area
        segmentations = collections.defaultdict(list)  # for segmentation
        for shape in label_data['shapes']:
            points = shape['points']
            label = shape['label']
            shape_type = shape.get('shape_type', None)
            mask = labelme.utils.shape_to_mask(
                img.shape[:2], points, shape_type
            )

            if label in masks:
                masks[label] = masks[label] | mask
            else:
                masks[label] = mask

            points = np.asarray(points).flatten().tolist()
            segmentations[label].append(points)

        for label, mask in masks.items():
            cls_name = label.split('-')[0]
            if cls_name not in class_name_to_id:
                continue
            cls_id = class_name_to_id[cls_name]

            mask = np.asfortranarray(mask.astype(np.uint8))
            mask = pycocotools.mask.encode(mask)
            area = float(pycocotools.mask.area(mask))
            bbox = pycocotools.mask.toBbox(mask).flatten().tolist()

            data['annotations'].append(dict(
                id=len(data['annotations']),
                image_id=image_id,
                category_id=cls_id,
                segmentation=segmentations[label],
                area=area,
                bbox=bbox,
                iscrowd=0,
            ))

    with open(out_ann_file, 'w') as f:
        json_str = json.dumps(data,indent=4, cls=MyEncoder)
        f.write(json_str)
        
    shutil.copyfile(out_ann_file,out_valann_file)

if __name__ == '__main__':
    main()
