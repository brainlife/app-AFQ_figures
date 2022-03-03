#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 14:53:50 2017
Edited on Fri Feb 11 2022

@author: lindseykitchell
edited by Brad Caron (bacaron), Giulia Berto (gberto), and Anibal Solon
"""

import matplotlib
matplotlib.use('Agg')
import glob
import os
import json
import numpy as np
import nibabel as nib
from fury import window, actor,ui

from lib import record, close

# THIS IS IMPORTANT FOR RUNNING VIA DOCKER. UNCOMMENT WHEN TESTING WITH DOCKER CONTAINER
from xvfbwrapper import Xvfb

# start virtual display
print("starting Xvfb");
vdisplay = Xvfb()
vdisplay.start()

# read json file
with open('config.json') as config_json:
    config = json.load(config_json)

# make images directory
if not os.path.exists("images"):
    os.mkdir("images")

# set empty array for file_list
json_file = {}
file_list = []
all_bundles = []
all_colors = []

# load t1
print("loading t1")
t1 = nib.load(config['anat'])
t1_img = t1.get_fdata()

# find shape of t1
sz = np.shape(t1_img)

# set affine transform
print("setting affine transform")
affine = t1.affine

# compute mean and standard deviation of t1 for brigthness adjustment
print("setting brightness")
mean, std = t1_img[t1_img > 0].mean(), t1_img[t1_img > 0].std()

# if brightness minimum is set in config, use that; else, set as min=0.5, max=2
if config["img_min"] == "":
	img_min = 0.5
else:
	img_min = config["img_min"]

if config["img_max"] == "":
	img_max = 3
else:
	img_max = config["img_max"]

# set brightness range
value_range = (mean - img_min * std, mean + img_max * std)

# load tractogram
# print("loading tractogram")
# track = nib.streamlines.load(config["track"])

# # set stream actor for visualization
# print("loading streamlines into visualizer")
# stream_actor = actor.line(track.streamlines)

# set camera position
camera_pos = [[0, 0, 450], [-450, 0, 0], [0, -450, 0], [450, 0, 0]]
camera_flip = [2, False, 1, False]
focal_point = [(-8.92, -16.15, 4.47), (0, -14, 9), (-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47)]
view_up = [(0.00, 1.00, -0.21), (0.00, 0.00, 1.00), (0.00, 0.00, 0.05), (0.00, 0.00, 1.00)]

# set slice view names
views = ['axial', 'sagittal_left', 'coronal', 'sagittal_right']

# if slices are different from defaults, use those; else, compute midslices
if config['axial'] == "":
	axial_view = sz[1]/2
else:
	axial_view = config['axial']

if config['sagittal'] == "":
	sagittal_view = sz[0]/2
else:
	sagittal_view = config['sagittal']

if config['coronal'] == "":
	coronal_view = sz[2]/2
else:
	coronal_view = config['coronal']

slice_view = [axial_view,sagittal_view,coronal_view]



# HERE'S CODE FOR GENERATING JUST A SINGLE TRACK AT A TIME FOR QA PURPOSES
# file = config["AFQ"]+'/1.json'
# with open(file) as data_file:
#     tract = json.load(data_file)
# bundle = []
# min_x = 0
# min_y = 0
# min_z = 0
# if len(tract['coords']) == 1:
#     templine = np.zeros([len(tract['coords'][0][0]), 3])
#     templine[:, 0] = tract['coords'][0][0]
#     templine[:, 1] = tract['coords'][0][1]
#     templine[:, 2] = tract['coords'][0][2]
#     bundle.append(templine)
#     min_x = np.min(bundle[0])
#     min_y = np.min(bundle[1])
#     min_z = np.min(bundle[2])
# elif len(tract['coords']) == 0:
#     bundle = [[],[],[]]
# elif len(tract['coords']) > 1:
#     for i in range(len(tract['coords'])):
#         templine = np.zeros([len(tract['coords'][i][0][0]), 3])
#         templine[:, 0] = tract['coords'][i][0][0]
#         templine[:, 1] = tract['coords'][i][0][1]
#         templine[:, 2] = tract['coords'][i][0][2]
#         bundle.append(templine)
#         if np.min(bundle[i][0]) < min_x:
#             min_x = np.round(np.min(bundle[i][0]))
#         if np.min(bundle[i][1]) < min_y:
#             min_y = np.round(np.min(bundle[i][1]))
#         if np.min(bundle[i][2]) < min_z:
#             min_z = np.round(np.min(bundle[i][2]))
# #slice_view = [min_x,min_y,min_z]
# all_bundles.append(bundle)
# all_colors.append(tract['color'])
# split_name = tract['name'].split(' ')
# imagename = '_'.join(split_name)

# print(np.array(bundle).shape)

# for d in range(len(camera_pos)):  # directions: axial, sagittal, coronal
#     print(".. rendering tracts")
#     print(d)

#     renderer = window.Scene()
#     stream_actor = actor.streamtube(bundle, colors=tract['color'], linewidth=0.5)

#     renderer.add(stream_actor)
#     slice_actor = actor.slicer(t1_img, affine)
#     slice_actor.opacity(1)
#     if d == 0: # axial
#         slice_actor.display(z=int(slice_view[2]))
#     elif d == 2: # coronal
#         slice_actor.display(y=int(slice_view[1]))
#     else: # left/right sagittal
#         slice_actor.display(x=int(slice_view[0]))

#     renderer.add(slice_actor)
#     renderer.set_camera(position=camera_pos[d],
#                         focal_point=focal_point[d],
#                         view_up=view_up[d])
#     renderer.reset_clipping_range()

#     print(".. taking photo!");

#     # window.show(renderer,reset_camera=False)

#     window.record(renderer, out_path='images/'+imagename+'_'+views[d]+'.png', size=(800, 800))

#     if camera_flip[d] != False:

#         camera_pos[d][camera_flip[d]] *= -1

#         renderer.set_camera(position=camera_pos[d],
#                             focal_point=focal_point[d],
#                             view_up=view_up[d])
#         # window.show(renderer,reset_camera=False)
#         window.record(renderer, out_path='images/'+imagename+'_'+views[d]+'_flipped.png', size=(800, 800))

renderer = window.Scene()

# iterate through all tracts
#for file in sorted(glob.glob(config["AFQ"] + "/*.json")):
#    if file != config["AFQ"]+ '/tracts.json':

tract_paths = []
if config['tracts'] == "":
    for file in sorted(glob.glob(config["AFQ"] + "/*.json")):
        if file != config["AFQ"]+ '/tracts.json':
            tract_paths.append(file)
else:
    tract_names = config['tracts']
    with open(config["AFQ"]+ '/tracts.json') as data_file:
        all_tracts = json.load(data_file)
    for item in all_tracts:
        if item['name'] in tract_names:
            tract_paths.append(config["AFQ"] + "/" + item['filename'])

for file in tract_paths:
    print("loading %s" % file)
    with open(file) as data_file:
        tract = json.load(data_file)
    bundle = []
    min_x = 0
    min_y = 0
    min_z = 0

    if np.shape(tract['coords'])[0] == 1 & np.shape(tract['coords'])[1] == 1:
        templine = np.zeros([len(tract['coords'][0][0]), 3])
        templine[:, 0] = tract['coords'][0][0]
        templine[:, 1] = tract['coords'][0][1]
        templine[:, 2] = tract['coords'][0][2]
        bundle.append(templine)
        min_x = np.min(bundle[0])
        min_y = np.min(bundle[1])
        min_z = np.min(bundle[2])
    elif len(tract['coords']) == 0:
        bundle = [[],[],[]]
    elif np.shape(tract['coords'])[0] > 1 or np.shape(tract['coords'])[1] > 1:
        if np.shape(tract['coords'])[0] < np.shape(tract['coords'])[1]:
            tract['coords'] = np.array(tract['coords']).swapaxes(0,1)
        for i in range(len(tract['coords'])):
            templine = np.zeros([len(tract['coords'][i][0][0]), 3])
            templine[:, 0] = tract['coords'][i][0][0]
            templine[:, 1] = tract['coords'][i][0][1]
            templine[:, 2] = tract['coords'][i][0][2]
            bundle.append(templine)
            if np.min(bundle[i][0]) < min_x:
                min_x = np.round(np.min(bundle[i][0]))
            if np.min(bundle[i][1]) < min_y:
                min_y = np.round(np.min(bundle[i][1]))
            if np.min(bundle[i][2]) < min_z:
                min_z = np.round(np.min(bundle[i][2]))
    #slice_view = [min_x,min_y,min_z]
    all_bundles.append(bundle)
    all_colors.append(tract['color'])
    split_name = tract['name'].split(' ')
    imagename = '_'.join(split_name)

    print(np.array(bundle).shape)

    for d in range(len(camera_pos)):  # directions: axial, sagittal, coronal
        print(".. rendering tracts")
        print(d)

        # add image information to json structure
        temp_dict = {}
        temp_dict["filename"]='images/'+imagename+'_'+views[d]+'.png'
        temp_dict["name"]=imagename.replace('_', ' ')+' '+views[d].replace('_', ' ') + ' view'
        temp_dict["desc"]= 'This figure shows '+ imagename.replace('_', ' ')+' '+views[d].replace('_', ' ') + ' view'
        file_list.append(temp_dict)

        # add flipped image path
        if camera_flip[d] != False:
            temp_dict = {}
            temp_dict["filename"]='images'+imagename+'_'+views[d]+'_flipped.png'

            temp_dict["name"]=imagename.replace('_', ' ')+' '+views[d].replace('_', ' ') + ' flipped view'

            temp_dict["desc"]= 'This figure shows '+ imagename.replace('_', ' ')+' '+views[d].replace('_', ' ') + ' flipped view'
            file_list.append(temp_dict)

        stream_actor = actor.streamtube(bundle, colors=tract['color'], linewidth=0.5)

        renderer.add(stream_actor)
        slice_actor = actor.slicer(t1_img, affine)
        slice_actor.opacity(1)
        if d == 0: # axial
            slice_actor.display(z=int(slice_view[2]))
        elif d == 2: # coronal
            slice_actor.display(y=int(slice_view[1]))
        else: # left/right sagittal
            slice_actor.display(x=int(slice_view[0]))

        renderer.add(slice_actor)
        renderer.set_camera(position=camera_pos[d],
                            focal_point=focal_point[d],
                            view_up=view_up[d])
        renderer.reset_clipping_range()

        print(".. taking photo!");

        # window.show(renderer,reset_camera=False)

        record(renderer, out_path='images/'+imagename+'_'+views[d]+'.png', size=(800, 800))

        if camera_flip[d] != False:

            camera_pos[d][camera_flip[d]] *= -1

            renderer.set_camera(position=camera_pos[d],
                                focal_point=focal_point[d],
                                view_up=view_up[d])
            # window.show(renderer,reset_camera=False)
            record(renderer, out_path='images/'+imagename+'_'+views[d]+'_flipped.png', size=(800, 800))

        renderer.clear()

# print("processing all tracts") # THIS IS TO GENERATE IMAGE OF ALL TRACTS COMBINED TOGETHER
for d in range(len(camera_pos)):  # directions: axial, sagittal, coronal
    print(".. rendering tracts")
    print(d)

    # add image information to json structure
    temp_dict = {}
    temp_dict["filename"]='images/alltracts_'+views[d]+'.png'
    temp_dict["name"]='All Tracts '+views[d].replace('_', ' ') + ' view'
    temp_dict["desc"]= 'This figure shows All Tracts '+views[d].replace('_', ' ') + ' view'
    file_list.append(temp_dict)

    # add flipped image path
    if camera_flip[d] != False:
        temp_dict = {}
        temp_dict["filename"]='images/alltracts_'+views[d]+'_flipped.png'
        temp_dict["name"]='All Tracts '+views[d].replace('_', ' ') + ' flipped view'
        temp_dict["desc"]= 'This figure shows All Tracts '+views[d].replace('_', ' ') + ' flipped view'
        file_list.append(temp_dict)

    for z in range(len(all_bundles)):
        stream_actor = actor.streamtube(all_bundles[z], colors=all_colors[z],
                                        linewidth=.5)
        renderer.set_camera(position=camera_pos[d],
                            focal_point=focal_point[d],
                            view_up=view_up[d])

        renderer.add(stream_actor)

    slice_actor = actor.slicer(t1_img, affine, value_range)

    if d == 0:
        slice_actor.display(z=int(slice_view[0]))
    elif d == 2:
        slice_actor.display(y=int(slice_view[2]))
    else:
        slice_actor.display(x=int(slice_view[1]))

    renderer.add(slice_actor)

    # window.show(renderer,reset_camera=False)
    record(renderer, out_path='images/alltracts_'+'_'+views[d]+'.png', size=(800, 800))

    if camera_flip[d] != False:

        camera_pos[d][camera_flip[d]] *= -1

        renderer.set_camera(position=camera_pos[d],
                            focal_point=focal_point[d],
                            view_up=view_up[d])

        record(renderer, out_path='images/alltracts_'+'_'+views[d]+'_flipped.png', size=(800, 800))

# print("saving images.json")
json_file['images'] = file_list
with open('images.json', 'w') as f:
    f.write(json.dumps(json_file, indent=4))
print(len(file_list))

close()

# THIS IS IMPORTANT FOR USING IN DOCKER CONTAINER! UNCOMMENT THIS WHEN TESTING WITH DOCKER CONTAINER
vdisplay.stop()

print("all done");
