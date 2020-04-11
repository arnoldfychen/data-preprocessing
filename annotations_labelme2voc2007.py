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


labelme_path = r"D:/work/AI/znz_all_image/camera/"
saved_path = r"D:/work/AI/znz_all_image/dataset-xml/"

if not os.path.exists(saved_path):
    os.makedirs(saved_path)
    
files = glob(labelme_path + "*.json")
files = [i.split(os.path.sep)[-1].split(".json")[0] for i in files]


for json_file_ in files:
    print("json_file_", json_file_)
    json_filename = labelme_path + json_file_ + ".json"
    print("json_filename", json_filename)
    json_file = json.load(open(json_filename,"r"))

    img_file = labelme_path + json_file_ +".jpg"
    height, width, channels = cv2.imread(img_file).shape
    with codecs.open(saved_path +json_file_ + ".xml","w","utf-8") as xml:
        xml.write('<annotation>\n')
        xml.write('\t<folder>' + 'fire_data' + '</folder>\n')
        xml.write('\t<filename>' + json_file_ + ".jpg" + '</filename>\n')
        xml.write('\t<path>' +saved_path+ json_file_ + ".jpg" + '</path>\n')
        xml.write('\t<source>\n')
        xml.write('\t\t<database>fire-database</database>\n')
        xml.write('\t\t<annotation>fire-annotation</annotation>\n')
        xml.write('\t\t<image>flickr</image>\n')
        xml.write('\t\t<flickrid>NULL</flickrid>\n')
        xml.write('\t</source>\n')
        xml.write('\t<owner>\n')
        xml.write('\t\t<flickrid>NULL</flickrid>\n')
        xml.write('\t\t<name>XSRT Robot Tech Co. Ltd</name>\n')
        xml.write('\t</owner>\n')
        xml.write('\t<size>\n')
        xml.write('\t\t<width>'+ str(width) + '</width>\n')
        xml.write('\t\t<height>'+ str(height) + '</height>\n')
        xml.write('\t\t<depth>' + str(channels) + '</depth>\n')
        xml.write('\t</size>\n')
        xml.write('\t\t<segmented>0</segmented>\n')
        for multi in json_file["shapes"]:
            points = np.array(multi["points"])
            xmin = int(min(points[:,0]))
            xmax = int(max(points[:,0]))
            ymin = int(min(points[:,1]))
            ymax = int(max(points[:,1]))
            label = multi["label"]
            if xmax <= xmin:
                print("error1:"+json_file_ + ".json, xmax<=xmin:",str(xmax),"<=",str(xmin))
                assert(False)
            elif ymax <= ymin:
                print("error2:"+json_file_ + ".json,ymax<=ymin:",str(ymax),"<=",str(ymin))
                assert(False)
            elif xmax> width or xmin<0:
                print("error3:"+json_file_ + ".json,xmax or xmin is wrong! xmax:",str(xmax),",width:",str(width),",xmin:",str(xmin))
                assert(False)
            elif ymax> height or ymin<0:
                print("error4:"+json_file_ + ".json,ymax or ymin is wrong! ymax:",str(ymax),",height:",str(height),",ymin:",str(ymin))
                assert(False)
            else:
                xml.write('\t<object>\n')
                xml.write('\t\t<name>'+multi['label']+'</name>\n')
                xml.write('\t\t<pose>Unspecified</pose>\n')
                xml.write('\t\t<truncated>0</truncated>\n')
                xml.write('\t\t<difficult>0</difficult>\n')
                xml.write('\t\t<bndbox>\n')
                xml.write('\t\t\t<xmin>' + str(xmin) + '</xmin>\n')
                xml.write('\t\t\t<ymin>' + str(ymin) + '</ymin>\n')
                xml.write('\t\t\t<xmax>' + str(xmax) + '</xmax>\n')
                xml.write('\t\t\t<ymax>' + str(ymax) + '</ymax>\n')
                xml.write('\t\t</bndbox>\n')
                xml.write('\t</object>\n')
                #print(json_filename,xmin,ymin,xmax,ymax,label)
        xml.write('</annotation>')
    shutil.copy(img_file,saved_path)
