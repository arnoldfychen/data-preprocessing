# encoding: utf-8

import os
import numpy as np
import codecs
import json
from glob import glob
import cv2
import shutil

# Arnold Chen:
# You may need to upgrade your sklearn as the default vesion 0.17.0-4 has no model-selection, (python-sklearn/scikit-learn >=0.18 has the module) 
# otherwise, the sklearn.model_selection may not exist!
# sudo pip install --upgrade scikit-learn==0.18 --default-timeout=3600
# or sudo apt-get install --upgrade python-sklearn
from sklearn.model_selection import train_test_split



src_path = r"D:/work/AI/口罩识别/人脸口罩检测数据集/facemask_dataset-reshaped/"              #做完了crop和resize的数据所在路径
dest_path = r"D:/work/AI/口罩识别/人脸口罩检测数据集/VOC2007-facemask-dataset/"              #VOC2007数据存放路径

if not os.path.exists(dest_path + "Annotations"):
    os.makedirs(dest_path + "Annotations")
if not os.path.exists(dest_path + "JPEGImages/"):
    os.makedirs(dest_path + "JPEGImages/")
if not os.path.exists(dest_path + "ImageSets/Main/"):
    os.makedirs(dest_path + "ImageSets/Main/")
    
files = glob(src_path + "*.xml")
files = [i.split(os.path.sep)[-1].split(".xml")[0] for i in files]

for xml_file_ in files:
    print(xml_file_)
    xml_file = src_path + xml_file_ + ".xml"
    img_file = src_path + xml_file_ +".jpg"
    shutil.copy(xml_file,dest_path +"Annotations/")
    shutil.copy(img_file,dest_path +"JPEGImages/")


txtsavepath = dest_path + "ImageSets/Main/"
ftrainval = open(txtsavepath+'/trainval.txt', 'w')
ftrain = open(txtsavepath+'/train.txt', 'w')
fval = open(txtsavepath+'/val.txt', 'w')

total_files = glob(dest_path+"Annotations/*.xml")
total_files = [i.split(os.path.sep)[-1].split(".xml")[0] for i in total_files]

for file in total_files:
    ftrainval.write(file + "\n")

#split
train_files,val_files = train_test_split(total_files,test_size=0.25,random_state=42)

#train
for file in train_files:
    ftrain.write(file + "\n")
#val
for file in val_files:
    fval.write(file + "\n")

ftrainval.close()
ftrain.close()
fval.close()

