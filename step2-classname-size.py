# encoding: utf-8
import sys

import xml.etree.ElementTree as ET
import os
import pickle
import numpy as np
import cv2
import glob
import shutil


all_classes = ['face','face_mask','mask','nomask']
         
def change_classname(xmlfile,output_path):
    
    src_path,filename=os.path.split(xmlfile)
    src_path=src_path.replace("\\","/")

    xmlname=filename.split(".")[0]
    jpgfile=xmlname+".jpg"
    
    src_xmlfile=xmlfile
    dest_xmlfile=os.path.join(output_path,filename)
    src_imgfile=os.path.join(src_path,jpgfile)
    dest_imgfile=os.path.join(output_path,jpgfile)
    
    img = cv2.imdecode(np.fromfile(src_imgfile,dtype=np.uint8),cv2.IMREAD_COLOR)     
    im_shape = img.shape
    img_height = im_shape[0]
    img_width = im_shape[1]
    img_depth = im_shape[2]
    
    tree = ET.parse(src_xmlfile)
    root = tree.getroot()
    element_size = tree.find('size')
    element_none=False
    if element_size is None:
        element_none=True
        element_size = ET.Element('size')
        element_width = ET.SubElement(element_size,'width')
        element_height = ET.SubElement(element_size,'height')
        element_depth = ET.SubElement(element_size,'depth')
        element_width.text=str(img_width)
        element_height.text=str(img_height)
        element_depth.text=img_depth
        root.append(element_size)
        
    
    objs = tree.findall('object')
        
    num_objs = len(objs)
    print('num_objs == %d' %num_objs)
    # There is no object labeled in the picture, just do nothing. 
    if num_objs <= 0 :
        #os.remove(src_imgfile)
        #os.remove(src_xmlfile)
        if element_none:
            tree.write(src_xmlfile)
        return
  
    class_box_count=0
    bExist = False
    for obj in objs:
        cls = obj.find('name').text.lower().strip()
        # Filter out those classes that are not in the list all_classes.
        if cls in all_classes:
            class_box_count += 1
            
            if cls == 'nomask':
                obj.find('name').text = 'face'
            elif cls == 'mask':
                obj.find('name').text = 'face_mask'
            
            if cls == 'nomask' or cls == 'mask':
                bExist = True
                
        #else:
        #    objs.remove(obj)
            
    print('class_box_count == %d' %class_box_count)
    # No valid object that we care is found, just return.
    #if class_box_count == 0:
    #    return
    
    if element_none:
        tree.write(src_xmlfile)
                
    shutil.copyfile(src_imgfile,dest_imgfile)
    if bExist:
        tree.write(dest_xmlfile)
    else:
        shutil.copyfile(src_xmlfile,dest_xmlfile)    
    


if __name__ == '__main__':
    srcpath=r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset"
    destpath=r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset-cls"
    if not os.path.exists(destpath):
        os.makedirs(destpath)
    xmllist=glob.glob(srcpath+"/*.xml")
    print(len(xmllist))
    for xml in xmllist:
        change_classname(xml,destpath)  
 