# encoding: utf-8
import sys
import xml.etree.ElementTree as ET
import os
import pickle
import numpy as np
import cv2
import glob
import shutil
import numpy as np

all_classes = ['face','face_mask']


# For internal call
def get_optimized_contour(img_height,img_width,roi_height,roi_width,x_min,y_min,x_max,y_max):
    x_center = x_min + int((x_max - x_min)/2)
    y_center = y_min + int((y_max - y_min)/2)
    half_roi_height = int(roi_height/2)
    half_roi_width = int(roi_width/2)
    
    crop_x_min = max(0,x_center - half_roi_width)
    crop_y_min = max(0, y_center - half_roi_height)
    crop_x_max = min(img_width,x_center + half_roi_width)
    crop_y_max = min(img_height,y_center + half_roi_height)
    
    return crop_x_min,crop_y_min,crop_x_max,crop_y_max
         

# For external call
def crop_image_or_roi(xml,output_path,roi_height,roi_width):
    src_path,filename=os.path.split(xml)
    src_path=src_path.replace("\\","/")
    xmlname=filename.split(".")[0]
    jpgname=xmlname+".jpg"
    srcfile=xml
    objpath = output_path
    #print objpath
    if not os.path.exists(objpath):
        os.makedirs(objpath) 

    objfile=os.path.join(objpath,filename)
    img_file_path=os.path.join(src_path,jpgname)
    if not os.path.exists(img_file_path):
        return

    tree = ET.parse(srcfile)
    

 
    file_name = jpgname
    file_name_cropped = "cropped-" + file_name
    img_file_path_cropped = os.path.join(objpath, file_name_cropped)
    
    error_list_file = os.path.join(objpath, "error-file-list.txt")

    file_name = xmlname+".xml"
    ann_file_name_cropped = "cropped-" + file_name
    annotation_file_path_cropped = os.path.join(objpath, ann_file_name_cropped)
    print(img_file_path)
    img = cv2.imdecode(np.fromfile(img_file_path,dtype=np.uint8),cv2.IMREAD_COLOR)
       
    im_shape = img.shape
    img_height = im_shape[0]
    img_width = im_shape[1]
    
    print('roi_height = %d, roi_width = %d  VS  img_height = %d, img_width = %d ' %(roi_height,roi_width,img_height,img_width))
    
    # Do nothing if the original size of the picture is smaller than the size of ROI that we specifies.
    if img_height <= roi_height and img_width <= roi_width :
        return

    objs = tree.findall('object')
    root = tree.getroot()
    element_size = tree.find('size')
    
    non_diff_objs = [obj for obj in objs if int(obj.find('difficult').text) == 0]
    objs = non_diff_objs  
        
    num_objs = len(objs)
    print('num_objs == %d' %num_objs)
    # There is no object labeled in the picture, just do nothing. 
    if num_objs <= 0 :
        return

   
    class_box_count=0
    for obj in objs:
        cls = obj.find('name').text.lower().strip()
        # Filter out those classes that are not in the list all_classes.
        if cls in all_classes:
            class_box_count += 1
        else:
            objs.remove(obj)
            
    print('class_box_count == %d' %class_box_count)
    # No valid object that we care is found, just return.
    if class_box_count == 0:
        return
    
    
            
    # boxes = np.zeros((class_box_count, 4), dtype=np.uint16)
    # roi_classes = []
    
    # To get the minimal size of the rectangle that can embrace all the boxes.
    x_min = img_width
    x_max = 0
    y_min = img_height
    y_max = 0

    
    for idx, obj in enumerate(objs):
        obj_name = obj.find('name')
        cls = obj_name.text.lower().strip()
        # roi_classes.append(cls)
            
        bbox = obj.find('bndbox')
        x1 = int(bbox.find('xmin').text)
        y1 = int(bbox.find('ymin').text)
        x2 = int(bbox.find('xmax').text)
        y2 = int(bbox.find('ymax').text)
        # boxes[idx, :] = [x1, y1, x2, y2]
        x_min = min(x_min, x1)
        y_min = min(y_min, y1)
        x_max = max(x_max, x2)
        y_max = max(y_max, y2)


    embrace_rect_width = x_max - x_min
    embrace_rect_height = y_max - y_min
    
    distance_to_left = x_min
    distance_to_right = img_width - x_max
    distance_to_top = y_min
    distance_to_bottom = img_height - y_max
    
    # Change this coefficient according to your requirement:
    # delta_coeff = 2
    
    obj_img_file_name = root.find('filename')
    obj_img_file_path = root.find('path')
    # Crop all the boxes as a whole, and generate new (annotation, image) files with the name format : (cropped-*.jpg, cropped-*.xml)   
    if embrace_rect_height <= roi_height and embrace_rect_width <= roi_width :
        
        #crop_x_min = max(0, x_min - int(distance_to_left/delta_coeff))
        #crop_y_min = max(0, y_min - int(distance_to_top/delta_coeff))
        #crop_x_max = min(img_width, x_max + int(distance_to_right/delta_coeff))
        #crop_y_max = min(img_height, y_max + int(distance_to_bottom/delta_coeff))
        crop_x_min,crop_y_min,crop_x_max,crop_y_max = get_optimized_contour(img_height,img_width,roi_height,roi_width,x_min,y_min,x_max,y_max)

        print("crop_x_min=%d,crop_y_min=%d, crop_x_max=%d,crop_y_max=%d" %(crop_x_min,crop_y_min,crop_x_max,crop_y_max))
        crop_img = img[crop_y_min : crop_y_max, crop_x_min : crop_x_max]
        
        if os.path.exists(img_file_path_cropped):
            os.remove(img_file_path_cropped)
        if os.path.exists(annotation_file_path_cropped):
            os.remove(annotation_file_path_cropped)
        if crop_y_min >= crop_y_max or crop_x_min >= crop_x_max :
            f = open(error_list_file,"a")
            f.write(xml+"\n")
            f.close()
            print("error file %s,img_height %d,img_width %d" %(xml,img_height,img_width))
            return
        #cv2.imwrite(img_file_path_cropped,crop_img)
        cv2.imencode('.jpg', crop_img)[1].tofile(img_file_path_cropped)
        
        if element_size is not None:
            element_width  = element_size.find('width')
            element_height = element_size.find('height')
            element_width.text = str(crop_x_max - crop_x_min)
            element_height.text = str(crop_y_max - crop_y_min)
        
        for obj in objs:          
            # Update the coordinations of the boxes that we care:
            bbox = obj.find('bndbox')
            xmin_obj = bbox.find('xmin')
            ymin_obj = bbox.find('ymin')
            xmax_obj = bbox.find('xmax')
            ymax_obj = bbox.find('ymax')
            x1 = int(xmin_obj.text)
            y1 = int(ymin_obj.text)
            x2 = int(xmax_obj.text)
            y2 = int(ymax_obj.text)
            xmin_obj.text = str(x1 - crop_x_min)
            ymin_obj.text = str(y1 - crop_y_min)
            xmax_obj.text = str(x2 - crop_x_min)
            ymax_obj.text = str(y2 - crop_y_min)
        
        if obj_img_file_name is not None:        
            obj_img_file_name.text = file_name_cropped
        if obj_img_file_path is not None:
            obj_img_file_path.text = img_file_path_cropped
        
        
        print("Crop as a whole: write annotation data into the xml file: %s" %annotation_file_path_cropped)
        tree.write(annotation_file_path_cropped)
    
    # Crop box by box, and generate new (annotation, image) files with the name format : (cropped-*-n.jpg, cropped-*-n.xml), n is the index of object    
    else:
        # objs and roi_classes have the same size
        # num_objs = len(objs)
        
        # Change this coefficient according to your requirement:
        delta_coeff_simple_crop = 3
        
        crop_x_min = 0
        crop_y_min = 0
        crop_x_max = 0
        crop_y_max = 0
                
        for idx, obj in enumerate(objs):
            cls = obj.find('name').text.lower().strip()
            # Update the coordinations of the boxes that we care:
            bbox = obj.find('bndbox')
            xmin_obj = bbox.find('xmin')
            ymin_obj = bbox.find('ymin')
            xmax_obj = bbox.find('xmax')
            ymax_obj = bbox.find('ymax')
            x1 = int(xmin_obj.text)
            y1 = int(ymin_obj.text)
            x2 = int(xmax_obj.text)
            y2 = int(ymax_obj.text)
            

            if x2 - x1 < roi_width and y2 - y1 < roi_height:
                crop_x_min,crop_y_min,crop_x_max,crop_y_max = get_optimized_contour(img_height,img_width,roi_height,roi_width,x1,y1,x2,y2)
            else:
                distance_to_left = x1
                distance_to_right = img_width - x2
                distance_to_top = y1
                distance_to_bottom = img_height - y2
            
                crop_x_min = max(0, x1 - int(distance_to_left/delta_coeff_simple_crop))
                crop_y_min = max(0, y1 - int(distance_to_top/delta_coeff_simple_crop))
                crop_x_max = min(img_width, x2 + int(distance_to_right/delta_coeff_simple_crop))
                crop_y_max = min(img_height, y2 + int(distance_to_bottom/delta_coeff_simple_crop))


            crop_img = img[crop_y_min:crop_y_max, crop_x_min:crop_x_max]
            
            file_name_cropped_idx = os.path.splitext(file_name_cropped)[0]+"-"+str(idx)+".jpg"
            img_file_path_cropped_idx = os.path.join(objpath, file_name_cropped_idx)
            annotation_file_path_cropped_idx = os.path.join(objpath, os.path.splitext(ann_file_name_cropped)[0]+"-"+str(idx)+".xml")
            
            if os.path.exists(img_file_path_cropped_idx):
                os.remove(img_file_path_cropped_idx)
            if os.path.exists(annotation_file_path_cropped_idx):
                os.remove(annotation_file_path_cropped_idx)
            if crop_y_min >= crop_y_max or crop_x_min >= crop_x_max :
                f = open(error_list_file,"a")
                f.write(xml+"\n")
                f.close()
                print("error file %s,img_height %d,img_width %d" %(xml,img_height,img_width))
                return

            #cv2.imwrite(img_file_path_cropped_idx,crop_img)
            cv2.imencode('.jpg', crop_img)[1].tofile(img_file_path_cropped_idx)
            
            if element_size is not None:
                element_width  = element_size.find('width')
                element_height = element_size.find('height')
                element_width.text = str(crop_x_max - crop_x_min)
                element_height.text = str(crop_y_max - crop_y_min)
            
            xmin_obj.text = str(x1 - crop_x_min)
            ymin_obj.text = str(y1 - crop_y_min)
            xmax_obj.text = str(x2 - crop_x_min)
            ymax_obj.text = str(y2 - crop_y_min)
            
            # Add a subelement 'croppped' to mark this object
            cropped_obj = ET.SubElement(obj, 'cropped')
            cropped_obj.text = 'yes'
            
            if obj_img_file_name is not None:    
                obj_img_file_name.text = file_name_cropped_idx
            if obj_img_file_path is not None:
                obj_img_file_path.text = img_file_path_cropped_idx
            
            
            tree.write(annotation_file_path_cropped_idx)
            root.remove(obj)
            # Read the new annotation file and delete all other objects
            tmp_tree = ET.parse(annotation_file_path_cropped_idx)
            tmp_root = tmp_tree.getroot()
            tmp_objs = tmp_tree.findall('object')
            for tmp_obj in tmp_objs:
                tmp_cropped = tmp_obj.find('cropped')
                if tmp_cropped is None:
                    # Delete all other objects
                    tmp_root.remove(tmp_obj)
                else:
                    tmp_obj.remove(tmp_cropped)
            
            # OK,save back
            
            print("Crop box by box, box[%d]: write annotation data into the xml file: %s" %(idx,annotation_file_path_cropped_idx))
            tmp_tree.write(annotation_file_path_cropped_idx) 
               


if __name__ == '__main__':
    crop_roi_height = 512
    crop_roi_width = 512
    srcpath=r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset"
    objpath=r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset-cropped"
 
    xmllist=glob.glob(srcpath+"/*.xml")
    print(len(xmllist))
    for xml in xmllist:
        crop_image_or_roi(xml,objpath,crop_roi_height,crop_roi_width)  
 