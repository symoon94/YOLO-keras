#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, argparse
import numpy as np
import xml.etree.ElementTree as ET
from collections import OrderedDict
import glob


sets=[('2020', 'train')]
classes = ["can_s", "vinyl_s"]

class_count = {}

def convert_annotation(dataset_path, year, class_name, image_id, list_file, include_difficult):
    in_file = open('%s/WASTE%s/Annotations/%s/%s.xml'%(dataset_path, year, class_name, image_id))
    tree=ET.parse(in_file)
    root = tree.getroot()

    for obj in root.iter('object'):
        difficult = obj.find('difficult')
        if difficult is None:
            difficult = '0'
        else:
            difficult = difficult.text
        cls = obj.find('name').text
        if cls not in classes:
            continue
        if not include_difficult and int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))
        class_count[cls] = class_count[cls] + 1


parser = argparse.ArgumentParser(description='convert PascalVOC dataset annotation to txt annotation file')
parser.add_argument('--dataset_path', type=str, help='path to custom dataset, default is ../../custom_data', default=os.getcwd()+'/../../custom_data')
parser.add_argument('--year', type=str, help='subset path of year (2020), default will cover 2020', default=None)
parser.add_argument('--set', type=str, help='convert data set, default will cover train, val and test', default=None)
parser.add_argument('--output_path', type=str,  help='output path for generated annotation txt files, default is ./', default='./')
# parser.add_argument('--classes_path', type=str, required=False, help='path to class definitions')
parser.add_argument('--include_difficult', action="store_true", help='to include difficult object', default=False)
parser.add_argument('--include_no_obj', action="store_true", help='to include no object image', default=False)
args = parser.parse_args()

# get real path for dataset
dataset_realpath = os.path.realpath(args.dataset_path)

# create output path
os.makedirs(args.output_path, exist_ok=True)

# get specific sets to convert
if args.year is not None:
    sets = [item for item in sets if item[0] == args.year]
if args.set is not None:
    sets = [item for item in sets if item[1] == args.set]

for year, image_set in sets:
    # count class item number in each set
    class_count = OrderedDict([(item, 0) for item in classes])

    list_file = open('%s/%s_%s.txt'%(args.output_path, year, image_set), 'w')
    path = dataset_realpath + f"/WASTE{year}/Images/"
    files = [f for f in glob.glob(path + "**/*.png", recursive=True)]
    for file_string in files:
        list_file.write(file_string)
        file_path_split = file_string.split("/")
        class_name = file_path_split[-2]
        image_id = file_path_split[-1].rstrip(".png")
        convert_annotation(dataset_realpath, year, class_name, image_id, list_file, args.include_difficult)
        list_file.write('\n')

    list_file.close()

    # print out item number statistic
    print('\nDone for %s_%s.txt. classes number statistic'%(year, image_set))
    print('Image number: %d'%(len(files)))
    print('Object class number:')
    for (class_name, number) in class_count.items():
        print('%s: %d' % (class_name, number))
    print('total object number:', np.sum(list(class_count.values())))

