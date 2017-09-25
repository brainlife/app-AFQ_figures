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
vdisplay = Xvfb()
vdisplay.start()

# read json file
with open('config.json') as config_json:
    config = json.load(config_json)

pwd = os.getcwd()
os.mkdir(pwd + "/images")

camera_pos = [(-5.58, 84.98, 467.47), (-482.32, 3.58, -6.28),
              (-58.32, 454.83, -14.22), (455.46, 9.14, 95.68)]
focal_point = [(-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47),
               (-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47)]
view_up = [(0.05, 0.98, -0.21), (-0.02, -0.01, 1.00),
           (-0.01, 0.04, 1.00), (-0.20, 0.21, 0.96)]
views = ['axial', 'sagittal_left', 'coronal', 'sagittal_right']

# slice_view = [48, 74, 85]
slice_view = [config['axial'], config['sagittal'], config['coronal']]

img = nib.load(config['t1'])
data = img.get_data()
affine = img.affine
mean, std = data[data > 0].mean(), data[data > 0].std()
value_range = (mean - 2 * std, mean + 2 * std)

all_bundles = []
all_colors = []
print config["AFQ"]
for file in glob.glob(config["AFQ"] + "/*.json"):
# for file in glob.glob("tracts/*.json"):
    if file != config["AFQ"]+ '/tracts.json':
        with open(file) as data_file:
            tract = json.load(data_file)
        bundle = []
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
            renderer = window.Renderer()
            stream_actor = actor.streamtube(bundle, colors=tract['color'],
                                            linewidth=1)
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
    
    #        show_m = window.ShowManager(renderer, size=(800, 700))
    #        show_m.initialize()
    #        show_m.render()
    #        show_m.start()
    #        renderer.camera_info() #get location of camera
    
            window.snapshot(renderer,
                            fname='images/'+imagename+'_'+views[d]+'.png',
                            size=(800, 800), offscreen=True,
                            order_transparent=False)


for d in range(len(camera_pos)):  # directions: axial, sagittal, coronal
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

#        show_m = window.ShowManager(renderer, size=(800, 700))
#        show_m.initialize()
#        show_m.render()
#        show_m.start()
#        renderer.camera_info() #get location of camera

    window.snapshot(renderer,
                    fname='images/alltracts_'+views[d]+'.png',
                    size=(800, 800), offscreen=True,
                    order_transparent=False)


vdisplay.stop()
