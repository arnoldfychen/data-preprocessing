"""
Created on Fri Aug 2 11:30:32 2019

@author: fychen
"""

import cv2
import os
import xml.etree.ElementTree as ET
import shutil

def process_draw_box(src_path,out_path):
    if not os.path.exists(out_path) :
        os.makedirs(out_path)
    filenames=os.listdir(src_path)
    filenames.sort()
    xml_files = []
    print(filenames)
    for file in filenames:
        tmp_file = os.path.join(src_path,file)
        if os.path.isdir(tmp_file):
           output_path = os.path.join(out_path,file+"_drawbox")
           process_draw_box(tmp_file,output_path)
 
        if os.path.isfile(tmp_file) and os.path.splitext(tmp_file)[1].lower()==".xml":
            xml_files.append(tmp_file)
    num = len(xml_files)
    print("There are %d xml files!" %num)
    if num<=0:
        return
        
    file_count=0
    for xml in xml_files:
        img_file = os.path.splitext(xml)[0]+".jpg"
        path,file = os.path.split(xml)
        xml_out = os.path.join(out_path, file)
        
        
        tree = ET.parse(xml)
        
        objs = tree.findall('object')
        non_diff_objs = [obj for obj in objs if int(obj.find('difficult').text) == 0]
        objs = non_diff_objs  
        
        num_objs = len(objs)
        print('num_objs == %d' %num_objs)
        if num_objs <= 0 :
            return
        
        shutil.copyfile(xml,xml_out)
        file_count += 1
        img = cv2.imread(img_file)
        for idx, obj in enumerate(objs):
            obj_name = obj.find('name')
            cls = obj_name.text.lower().strip()

            bbox = obj.find('bndbox')
            x_min = int(bbox.find('xmin').text)
            y_min = int(bbox.find('ymin').text)
            x_max = int(bbox.find('xmax').text)
            y_max = int(bbox.find('ymax').text)
            cv2.rectangle(img,(x_min,y_min),(x_max,y_max),(0,255,0),3)
            cv2.putText(img, obj_name.text,(x_min,y_min),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,255),1)
            
        path,file = os.path.split(img_file)    
        img_out =  os.path.join(out_path,file)
        cv2.imwrite(img_out,img)
        
        
        print("The #%d file is processed, generated new files to (%s,%s)" %(file_count,xml_out,img_out))


if __name__ == '__main__':
    input_path = "/mnt/data/test_data"
    output_path = "/mnt/data/test_data_drawbox"
    
    process_draw_box(input_path,output_path)