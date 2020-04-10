#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 2020

@author: bacaron
-adapted from code written by Lindsey Kitchell (github.com/lkitchell/app-AFQ_figures/blob/v2.1/main.py)
"""

import matplotlib
matplotlib.use('Agg')
import os
import json
import numpy as np
import nibabel as nib
from dipy.viz import window, actor
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

# load tractogram
print("loading tractogram")
track = nib.streamlines.load(config["track"])

# set stream actor for visualization
print("loading streamlines into visualizer")
stream_actor = actor.line(track.streamlines)

# set camera position
camera_pos = [(-5.58, 84.98, 467.47), (-482.32, 3.58, -6.28),
              (-58.32, 454.83, -14.22), (455.46, 9.14, 95.68)]
focal_point = [(-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47),
               (-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47)]
view_up = [(0.00, 1.00, -0.21), (0.00, 0.00, 1.00),
              (0.00, 0.00, 0.05), (0.00, 0.00, 1.00)]

# set slice view names
views = ['axial', 'sagittal_left', 'coronal', 'sagittal_right']

# set renderer window
renderer = window.Renderer()

# add streamlines to renderer
renderer.add(stream_actor)

# for loops through views
for v in range(len(views)):
	print("creating image with %s orientation" %views[v])

	# set camera view
	renderer.set_camera(position=camera_pos[v],
		focal_point=focal_point[v],
		view_up=view_up[v])

	# save pngs
	print("Creating tractogram png of view %s" %views[v])
	out_name = '/images/tractogram_'+views[v]+'.png'
	window.record(renderer,out_path=out_name,size=(800,800),reset_camera=False)

	# append information for file list for json output
	temp_dict = {}
	temp_dict["filename"]='images/tractogram_'+views[v]+'.png'
	temp_dict["name"]='Tractogram '+views[v].replace('_', ' ') + ' view'
	temp_dict["desc"]= 'This figure shows the '+views[v].replace('_', ' ') + ' view of the tractogram'
	file_list.append(temp_dict)

	print("%s orientation complete" %views[v])

# save images.json
print("saving images.json")
json_file['images'] = file_list
with open('images.json', 'w') as f:
    f.write(json.dumps(json_file, indent=4))
print(len(file_list))

vdisplay.stop()

print("complete")



