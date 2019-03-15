#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 14:53:50 2017

@author: lindseykitchell
"""


import matplotlib
matplotlib.use('Agg')
import glob
import os
import json
import numpy as np
import nibabel as nib
from dipy.viz import window, actor
from xvfbwrapper import Xvfb

# start virtual display
print("starting Xvfb");
vdisplay = Xvfb(width=800, height=800)
vdisplay.start()

# read json file
with open('config.json') as config_json:
    config = json.load(config_json)

if not os.path.exists("images"):
    os.mkdir("images")

camera_pos = [(-5.58, 84.98, 467.47), (-482.32, 3.58, -6.28),
              (-58.32, 454.83, -14.22), (455.46, 9.14, 95.68)]
focal_point = [(-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47),
               (-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47)]
#view_up = [(0.05, 0.98, -0.21), (-0.02, -0.01, 1.00),
#           (-0.01, 0.04, 1.00), (-0.20, 0.21, 0.96)]
view_up = [(0.00, 1.00, -0.21), (0.00, 0.00, 1.00),
              (0.00, 0.00, 0.05), (0.00, 0.00, 1.00)]
views = ['axial', 'sagittal_left', 'coronal', 'sagittal_right']

# slice_view = [48, 74, 85]
slice_view = [config['axial'], config['sagittal'], config['coronal']]

print("loading t1");
img = nib.load(config['t1'])
data = img.get_data()
affine = img.affine
mean, std = data[data > 0].mean(), data[data > 0].std()

if 'img_min' in config:
    value_range = (mean+ config['img_min'] * std, mean + config['img_max'] * std)
else: 
    value_range = (mean - 0.5 * std, mean + 2 * std)

json_file = {}
file_list = []
all_bundles = []
all_colors = []
for file in glob.glob(config["AFQ"] + "/*.json"):
    if file != config["AFQ"]+ '/tracts.json':
        print("loading %s" % file)
        with open(file) as data_file:
            tract = json.load(data_file)
        bundle = []
        if len(tract['coords']) == 1:
            templine = np.zeros([len(tract['coords'][0][0]), 3])
            templine[:, 0] = tract['coords'][0][0]
            templine[:, 1] = tract['coords'][0][1]
            templine[:, 2] = tract['coords'][0][2]
            bundle.append(templine)
        elif len(tract['coords']) == 0:
            bundle = [[],[],[]]
        elif len(tract['coords']) > 1:
            for i in range(len(tract['coords'])):
                templine = np.zeros([len(tract['coords'][i][0][0]), 3])
                templine[:, 0] = tract['coords'][i][0][0]
                templine[:, 1] = tract['coords'][i][0][1]
                templine[:, 2] = tract['coords'][i][0][2]
                bundle.append(templine)
        all_bundles.append(bundle)
        all_colors.append(tract['color'])
        split_name = tract['name'].split(' ')
        imagename = '_'.join(split_name)

        for d in range(len(camera_pos)):  # directions: axial, sagittal, coronal
            print(".. rendering tracts")
            print(d)
            renderer = window.Renderer()
            stream_actor = actor.streamtube(bundle, colors=tract['color'], linewidth=1)
            renderer.set_camera(position=camera_pos[d],
                                focal_point=focal_point[d],
                                view_up=view_up[d])
    
            renderer.add(stream_actor)
            slice_actor = actor.slicer(data, affine, value_range)
            if d == 0:
                slice_actor.display(z=int(slice_view[0]))
            elif d == 2:
                slice_actor.display(y=int(slice_view[2]))
            else:
                slice_actor.display(x=int(slice_view[1]))
            renderer.add(slice_actor)
    
            print(".. taking photo!");
            #window.snapshot(renderer, fname='images/'+imagename+'_'+views[d]+'.png', size=(800, 800), offscreen=True)#, order_transparent=False)
            #window.snapshot(renderer, fname='images/'+imagename+'_'+views[d]+'.png')
            window.record(renderer, out_path='images/'+imagename+'_'+views[d]+'.png', size=(800, 800))
            temp_dict = {}
            temp_dict["filename"]='images/'+imagename+'_'+views[d]+'.png'
            temp_dict["name"]=imagename.replace('_', ' ')+' '+views[d].replace('_', ' ') + ' view'
            temp_dict["desc"]= 'This figure shows '+ imagename.replace('_', ' ')+' '+views[d].replace('_', ' ') + ' view'
            file_list.append(temp_dict)


print("processing all tracts")
for d in range(len(camera_pos)):  # directions: axial, sagittal, coronal
    print(".. rendering tracts")
    print(d)
    renderer = window.Renderer()
    for z in range(len(all_bundles)):
        stream_actor = actor.streamtube(all_bundles[z], colors=all_colors[z],
                                        linewidth=.5)
        renderer.set_camera(position=camera_pos[d],
                            focal_point=focal_point[d],
                            view_up=view_up[d])

        renderer.add(stream_actor)
    slice_actor = actor.slicer(data, affine, value_range)
    if d == 0:
        slice_actor.display(z=int(slice_view[0]))
    elif d == 2:
        slice_actor.display(y=int(slice_view[2]))
    else:
        slice_actor.display(x=int(slice_view[1]))
    renderer.add(slice_actor)

    print(".. taking group photo")
    window.record(renderer, out_path='images/alltracts_'+views[d]+'.png', size=(800,800))
    #window.snapshot(renderer, fname='images/alltracts_'+views[d]+'.png', size=(800, 800), offscreen=True, order_transparent=False)
    temp_dict = {}
    temp_dict["filename"]='images/alltracts_'+views[d]+'.png'
    temp_dict["name"]='All Tracts '+views[d].replace('_', ' ') + ' view'
    temp_dict["desc"]= 'This figure shows All Tracts '+views[d].replace('_', ' ') + ' view'
    file_list.append(temp_dict)

print("saving images.json")
json_file['images'] = file_list
with open('images.json', 'w') as f:
    f.write(json.dumps(json_file, indent=4))
print(len(file_list))

vdisplay.stop()

print("all done");
