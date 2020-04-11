# encoding: utf-8
import os
import glob
import shutil
import sys
import uuid
import json

file_count=0
            
def rename_uuid_s2d(src_path,dest_path):
    file_pattern = os.path.join(src_path,"*.jpg")
    print("file_pattern",file_pattern)
    jpgfiles = glob.glob(file_pattern)
    
    print("size",len(jpgfiles))
    for jpgfile in jpgfiles:
        path,filename = os.path.split(jpgfile)
        fname = filename.split(".")[0]
        uid = str(uuid.uuid1())
        name = ''.join(uid.split('-'))
        img_filename = name + ".jpg"
        xml_filename = name + ".xml"
        dest_imgfile = os.path.join(dest_path,img_filename)
        src_xmlfile = os.path.join(path,fname+".xml")
        dest_xmlfile = os.path.join(dest_path,xml_filename)
        if os.path.exists(dest_imgfile):
           print("error! ",dest_imgfile," exists!")
           sys.exit(1)
        
        shutil.move(jpgfile,dest_imgfile)
        shutil.move(src_xmlfile,dest_xmlfile)
        
    file_pattern = os.path.join(src_path,"*.jpg")
    print("file_pattern",file_pattern)         
    jpgfiles = glob.glob(file_pattern)       
    for jpgfile in jpgfiles:
        path,filename = os.path.split(jpgfile)
        fname = filename.split(".")[0]
           
        global file_count   
        file_count += 1
        name = "{0:0>8}".format(file_count)        
        img_filename = name + ".jpg"
        xml_filename = name + ".xml"
        dest_imgfile = os.path.join(dest_path,img_filename)
        src_xmlfile = os.path.join(path,fname+".xml")
        dest_xmlfile = os.path.join(dest_path,xml_filename)
        if os.path.exists(dest_imgfile):
           print("error! ",dest_imgfile," exists!")
           sys.exit(1)
            
        shutil.move(jpgfile,dest_imgfile)
        shutil.move(src_xmlfile,dest_xmlfile)
        
        print(" The #%d jpg file is renamed" %file_count)
    

if __name__ == '__main__':
    src_path= r"D:\work\AI\口罩识别\人脸口罩检测数据集\facemask_dataset"
    dest_path = src_path
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    file_count = 3406
    
    rename_uuid_s2d(src_path,dest_path)