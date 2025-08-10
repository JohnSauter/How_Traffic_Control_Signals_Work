#!/usr/bin/python3
# -*- coding: utf-8
#
# draw_background.py creates the background image for the renderer.

#   Copyright © 2025 by John Sauter <John_Sauter@systemeyescomputerstore.com>

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#   The author's contact information is as follows:
#     John Sauter
#     System Eyes Computer Store
#     20A Northwest Blvd.  Ste 345
#     Nashua, NH  03063-4066
#     telephone: (603) 424-1188
#     e-mail: John_Sauter@systemeyescomputerstore.com

import time
import numpy as np
import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2
import math
import json
import pprint
import decimal
import fractions
import csv
import pathlib
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Create the background image for the renderer.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='draw_background 0.42 2025-08-02',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--intersection-file', metavar='input_file',
                     help='read the intersection descrpption from this ' +
                     'JSON file.')
parser.add_argument ('--background-file', metavar='background_file',
                     help='write background image to the specified file')
parser.add_argument ('--screen-width', type=int, metavar='screen_width',
                     help='width of the background image')
parser.add_argument ('--screen-height', type=int, metavar='screen_height',
                     help='height of the background image')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

error_counter = 0
verbosity_level = 1
do_trace = False
trace_file_name = ""
do_intersection = False
do_background = False
screen_width = 3840
screen_height = 2160
background_file_name = ""

ground_height = 143

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_level = 1
  trace_file_name = arguments ['trace_file']
  trace_file_name = pathlib.Path(trace_file_name)
  trace_file = open (trace_file_name, 'wt')

if (arguments ['intersection_file'] != None):
  do_intersection = True
  intersection_file_name = arguments ['intersection_file']
  intersection_file_name = pathlib.Path(intersection_file_name)

if (arguments ['background_file'] != None):
  do_background = True
  background_file_name = arguments ['background_file']
  background_file_name = pathlib.Path(background_file_name)
  
if (arguments ['screen_width'] != None):
  screen_width = int(arguments ['screen_width'])

if (arguments ['screen_height'] != None):
  screen_height = int(arguments ['screen_height'])

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

# Subroutine to map ground locations to screen locations.
# The ground has its origin at the center of the intersection, which is also
# the center of the screen.  The screen has its origin at the upper left
# corner.
def map_location_ground_to_screen (y_feet, x_feet):
  global ground_height
  global screen_width
  global screen_height
  
  # The ground is the same shape as the screen, but is measured in feet.
  ground_width = ground_height * (screen_width / screen_height)
  
  ground_center_x = ground_width / 2
  ground_center_y = ground_height / 2
  screen_center_x = screen_width / 2
  screen_center_y = screen_height / 2
  x_from_center = x_feet
  y_from_center = y_feet
  x_from_center = x_from_center * (screen_width / ground_width)
  y_from_center = y_from_center * (screen_height / ground_height)
  x_pixels = x_from_center + screen_center_x
  y_pixels = y_from_center + screen_center_y

  return (int(y_pixels), int(x_pixels))

# Subroutine to convert a ground size to a screen size.
def convert_ground_size_to_screen_size (size_in_feet):
  global ground_height
  global screen_height
  global screen_width

  size_in_pixels = size_in_feet * (screen_height / ground_height)
  return (int(size_in_pixels))
          
# Subroutine to map screen locations to ground locations.
# The screen has its origin at the top left, while the ground has its origin
# in the center of the screen.
def map_location_screen_to_ground (y_pixels, x_pixels):
  global ground_height
  global screen_height
  global screen_width
  
  ground_width = ground_height * (screen_width / screen_height)
  ground_center_x = ground_width / 2
  ground_center_y = ground_height / 2
  screen_center_x = screen_width / 2
  screen_center_y = screen_height / 2
  x_from_center = x_pixels - screen_center_x
  y_from_center = y_pixels - screen_center_y
  x_from_center = x_from_center * (ground_width / screen_width)
  y_from_center = y_from_center * (ground_height / screen_height)
  x_feet = x_from_center + ground_center_x
  y_feet = y_from_center + ground_center_y
  
  return (y_feet, x_feet)

# Subroutine to convert a screen size to a ground size.
def convert_screen_size_to_ground_size (size_in_pixels):
  global ground_height
  global screen_height
  global screen_width

  size_in_feet = size_in_pixels * (ground_height / screen_height)
  return (int(size_in_feet))

# Draw a line from (x1, y1) to (x2, y2) with the specified color
# and line width.
def draw_line (the_image, x1, y1, x2, y2, line_color, line_width,
               with_arrowhead):
  
  screen_y1, screen_x1 = map_location_ground_to_screen (y1, x1)
  screen_y2, screen_x2 = map_location_ground_to_screen (y2, x2)

  # If the line as projected onto the screen has zero length,
  # don't draw anything.
  if ((screen_x1 == screen_x2) and (screen_y1 == screen_y2)):
    return

  screen_line_width = convert_ground_size_to_screen_size (line_width)
  
  if (with_arrowhead):
    line_length = math.sqrt (((screen_x2 - screen_x1)**2) +
                             ((screen_y2 - screen_y1)**2))
    if (do_trace):
      tracefile.write ("Line length: " + str(line_length) + ".\n")
      
    cv2.arrowedLine (the_image, (screen_x1, screen_y1), (screen_x2, screen_y2),
                     line_color, screen_line_width, cv2.LINE_AA,
                     tipLength = 25.0 / line_length)
  else:
    cv2.line (the_image, (screen_x1, screen_y1), (screen_x2, screen_y2),
              line_color, screen_line_width, cv2.LINE_AA)
  return

color_black = (0, 0, 0)
color_green = (0, 65535, 0)
color_light_blue = (50000, 30000, 30000)
color_gray = (40000, 40000, 40000)
color_dark_gray = (30000, 30000, 30000)
color_white = (65535, 65535, 65535)

if (do_intersection):
  intersection_file = open (intersection_file_name, 'r')
  intersection_info = json.load (intersection_file)
  intersection_file.close()
else:
  intersection_info = dict()

if (do_trace):
  trace_file.write ("intersection info:\n")
  pprint.pprint (intersection_info, trace_file)

lanes_info = intersection_info ["lanes info"]
travel_paths = intersection_info ["travel paths"]

# Create a grey background.
image = np.full (shape=(screen_height, screen_width, 3),
                 fill_value = color_gray).astype(np.uint16)

if (do_trace):
  trace_file.write ("blank image:\n")
  pprint.pprint (image, trace_file)

# Draw travel paths.
for travel_path_name in travel_paths:
  travel_path = travel_paths [travel_path_name]
  milestones = travel_path ["milestones"]
  previous_position = None
  for milestone in milestones:
    lane_name = milestone[0]
    if (lane_name in lanes_info):
      lane = lanes_info [lane_name]
      lane_width = float(lane["width"])
    x_position = milestone[1]
    y_position = milestone[2]
    if (previous_position != None):
      if (do_trace):
        trace_file.write ("travel path " + travel_path_name +
                          " lane " + lane_name + ":\n")
        pprint.pprint ((x_position, y_position), trace_file)
      draw_line (image, previous_position[0], previous_position[1],
                 x_position, y_position,  color_dark_gray, lane_width,
                 False)
    previous_position = (x_position, y_position)

# Outline each lane.
for lane_name in lanes_info:
  lane = lanes_info [lane_name]
  top_x = int(lane["top x"])
  top_y = int(lane["top y"])
  bottom_x = int(lane["bottom x"])
  bottom_y = int(lane["bottom y"])
  lane_width = float(lane["width"])

  # Find the edges of the lane.
  if (top_y != bottom_y):
    # lane goes up or down
    p1_x = top_x - (lane_width / 2)
    p1_y = top_y
    p2_x = p1_x
    p2_y = bottom_y
    p3_x = top_x + (lane_width / 2)
    p3_y = top_y
    p4_x = p3_x
    p4_y = p2_y
  else:
    # lane goes left or right
    p1_x = top_x
    p1_y = top_y - (lane_width / 2)
    p2_x = bottom_x
    p2_y = p1_y
    p3_x = p1_x
    p3_y = top_y + (lane_width / 2)
    p4_x = p2_x
    p4_y = p3_y

  draw_line (image, p1_x, p1_y, p2_x, p2_y, color_black, 0.5, False)
  draw_line (image, p3_x, p3_y, p4_x, p4_y, color_black, 0.5, False)
  
  if (do_trace):
    trace_file.write ("Line " + lane_name + ":\n")
    pprint.pprint ((top_x, top_y, bottom_x, bottom_y), trace_file)
    pprint.pprint ((p1_x, p1_y, p2_x, p2_y), trace_file)
    pprint.pprint ((p3_x, p3_y, p4_x, p4_y), trace_file)

# Place names on the lanes.
font_face = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 2
font_color = color_green
font_thickness = 3

for lane_name in lanes_info:
  lane = lanes_info [lane_name]
  top_x = int(lane["top x"])
  top_y = int(lane["top y"])
  screen_y, screen_x = map_location_ground_to_screen (top_y, top_x)
  textsize = cv2.getTextSize (lane_name, font_face, font_scale,
                              font_thickness)[0]
  text_x = int(screen_x - (textsize[0] / 2))
  text_y = int(screen_y + (textsize[1] / 2))
  
  if (do_trace):
    trace_file.write ("Lane " + lane_name + " at (" + str(screen_x) + ", " +
                      str(screen_y) + ") displayed at (" +
                      str(text_x) + ", " + str(text_y) + ").\n")
    
  cv2.putText (image, lane_name, (text_x, text_y),
               font_face, font_scale, font_color, font_thickness)
  
if (do_background):
  cv2.imwrite (background_file_name, image)

if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file draw_background.py
