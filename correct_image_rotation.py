import xml.etree.ElementTree as ET
import os
import numpy as np
import cv2
import glob
import shutil


def pickup_wrong_rotation(src_path,dest_path):
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        
    #xmllist=glob.glob(src_path+os.path.sep+"*.xml")
    xmllist = glob.glob(r"../xunlianyangben/*/*/*.xml")
    for xml in xml_list:
        xmlfile = os.path.basename(xml)[:-4] + ".xml"
        imgfile = os.path.basename(xml)[:-4] + ".jpg"
    file_count=0
    num=0    
    for xml in xmllist:
        xmlname=os.path.basename(xml)
        filename=xmlname.split(".")[0]
        jpgname=filename+".jpg"
        
        xml_file_path=xml
        img_file_path=xml[:-4] + ".jpg"
        
        tree = ET.parse(xml_file_path)
        size = tree.find('size')
        xml_width = int(size.find("width").text)
        xml_height = int(size.find("height").text)
        if not os.path.exists(img_file_path):
            img_file_path=xml[:-4] + ".JPG"
            if not os.path.exists(img_file_path):
                continue
        img = cv2.imread(img_file_path)
        img_height = img.shape[0]
        img_width = img.shape[1]
        
        error_xml_file_path = os.path.join(dest_path,xmlname)
        error_img_file_path = os.path.join(dest_path,jpgname)
        
        if xml_width != img_width or xml_height != img_height :
            shutil.copyfile(xml_file_path,error_xml_file_path)
            shutil.copyfile(img_file_path,error_img_file_path)
            num += 1
        file_count += 1
        print("The #%d file is checked, %d files have the rotation error." %(file_count,num))
        

def correct_rotation(src_path,dest_path):
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    xmllist=glob.glob(src_path+os.path.sep+"*.xml")
    
    for xml in xmllist:
        xmlname=os.path.basename(xml)
        filename=xmlname.split(".")[0]
        jpgname=filename+".jpg"
        
        xml_file_path=os.path.join(src_path,xmlname)
        img_file_path=os.path.join(src_path,jpgname)
        
        tree = ET.parse(xml_file_path)
        objs = tree.findall('object')
        non_diff_objs = [obj for obj in objs if int(obj.find('difficult').text) == 0]
        objs = non_diff_objs  
        
        num_objs = len(objs)
        print('xml file %s,num_objs == %d' %(xml_file_path,num_objs))
        if num_objs <= 0 :
            continue
            
        size = tree.find('size')
        obj_width = size.find("width")
        obj_height = size.find("height")
        width = int(obj_width.text)
        height = int(obj_height.text)
        img = cv2.imread(img_file_path)
        
        im_shape = img.shape
        img_height = im_shape[0]
        img_width = im_shape[1]
        obj_width.text = str(img_width)
        obj_height.text = str(img_height)
        
        corrected_xml_file_path = os.path.join(dest_path,xmlname)
        corrected_img_file_path = os.path.join((dest_path,jpgname)
        #shutil.copyfile(xml_file_path,corrected_xml_file_path)
        #shutil.copyfile(img_file_path,corrected_img_file_path)
        
        img = cv2.imread(img_file_path)
        for idx, obj in enumerate(objs):
            obj_name = obj.find('name')
            cls = obj_name.text.lower().strip()

            bbox = obj.find('bndbox')
            obj_xmin = bbox.find('xmin')
            obj_ymin = bbox.find('ymin')
            obj_xmax = bbox.find('xmax')
            obj_ymax = bbox.find('ymax')
            
            x_min = int(obj_xmin.text)
            y_min = int(obj_ymin.text)
            
            if width>0 and height>0:
                tmp = y_min
                y_min = x_min
                x_min = tmp
                obj_xmin.text = str(x_min)
                obj_ymin.text = str(y_min)
            
            x_max = int(obj_xmax.text)
            y_max = int(obj_ymax.text)
            
            if width>0 and height>0:
                tmp = y_max
                y_max = x_max
                x_max = tmp
                obj_xmax.text = str(x_max)
                obj_ymax.text = str(y_max)
            
            cv2.rectangle(img,(x_min,y_min),(x_max,y_max),(0,255,0),3)
            cv2.putText(img, obj_name.text,(x_min,y_min),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,255),1)
        tree.write(corrected_xml_file_path)            
        cv2.imwrite(corrected_img_file_path,img)    
    
if __name__ == '__main__':
    src_path="./images"
    rotation_error_path="./rotation_error"
    rotation_corrected_path="./rotation_corrected"
    pickup_wrong_rotation(src_path,rotation_error_path)
    correct_rotation(rotation_error_path,rotation_corrected_path)