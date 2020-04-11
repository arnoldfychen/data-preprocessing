# encoding: utf-8

import xml.etree.ElementTree as ET
import os
import pickle
import numpy as np
import cv2
import glob
import shutil



def reshape(xml,objpath):
    src_path,filename=os.path.split(xml)
    src_path=src_path.replace("\\","/")

    xmlname=filename.split(".")[0]
    jpgname=xmlname+".jpg"
    src_xmlfile=xml
    obj_xmlfile=os.path.join(objpath,filename)
    
    src_imgfile=os.path.join(src_path,jpgname)
    obj_imgfile=os.path.join(objpath,jpgname)
    
    if not os.path.exists(src_imgfile):
        print("no image file:{}".format(src_imgfile))
        return
    if os.path.exists(obj_xmlfile) and os.path.exists(obj_imgfile):
        print("{} exists!".format(obj_xmlfile))
        return

    img = cv2.imdecode(np.fromfile(src_imgfile,dtype=np.uint8),cv2.IMREAD_COLOR) 
    imgwidth=img.shape[1]
    imgheight=img.shape[0]
    ratio=float(max(imgwidth,imgheight))/511.0
    if ratio <=1.0 :
        shutil.copyfile(src_xmlfile,obj_xmlfile)
        shutil.copyfile(src_imgfile,obj_imgfile)
        return    

    imgwidth=int(round(imgwidth/ratio))
    imgheight=int(round(imgheight/ratio))
    
    res = cv2.resize(img,(imgwidth,imgheight), interpolation = cv2.INTER_CUBIC)
    cv2.imencode('.jpg', res)[1].tofile(obj_imgfile)
 
    #print(src_xmlfile)
    tree = ET.parse(src_xmlfile)
    element_size = tree.find('size')
    if element_size is not None:
            element_width  = element_size.find('width')
            element_height = element_size.find('height')
            element_width.text = str(imgwidth)
            element_height.text = str(imgheight)
    
    objects = tree.findall('object')
    for obj in objects:
        bndbox = obj.find('bndbox')
        bbox_xmin = bndbox.find('xmin')
        bbox_ymin = bndbox.find('ymin')
        bbox_xmax = bndbox.find('xmax')
        bbox_ymax = bndbox.find('ymax')
        bndxmin=int(bbox_xmin.text)
        bndymin=int(bbox_ymin.text)
        bndxmax=int(bbox_xmax.text) 
        bndymax=int(bbox_ymax.text)
        left=int(round(bndxmin/ratio))
        bottom=int(round(bndymin/ratio))
        right=int(round(bndxmax/ratio))
        top=int(round(bndymax/ratio))
        if left <=0: 
            left=1
        if left > imgwidth:
            left = imgwidth
        if right > imgwidth:
            right = imgwidth
        if bottom <=0:
            bottom =1
        if bottom > imgheight:
            bottom = imgheight
        if top <= 0:
            top =1
        if top > imgheight:
            top = imgheight
        bbox_xmin.text= str(left)
        bbox_ymin.text= str(bottom)
        bbox_xmax.text= str(right)
        bbox_ymax.text= str(top)
    tree.write(obj_xmlfile)
   
if __name__ == '__main__':
   srcpath=r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset-cropped"
   objpath=r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset-reshaped"
   if not os.path.exists(objpath):
       os.makedirs(objpath) 
   xmllist=glob.glob(srcpath+"/*.xml")
   print(len(xmllist))
   for xml in xmllist:
       reshape(xml,objpath)
 