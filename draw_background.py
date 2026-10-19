#!/usr/bin/python3
# -*- coding: utf-8
#
# draw_background.py creates the background image for the renderer.

#   Copyright © 2026 by John Sauter <John_Sauter@systemeyescomputerstore.com>

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
  epilog=('Copyright © 2026 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='draw_background 0.76 2026-10-17',
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
parser.add_argument ('--show-waypoints', action='store_true',
                     help='Draw the waypoints on the background')
parser.add_argument ('--pavement-markings-directory', metavar='pavement_dir',
                     help='read the pavement markings images from ' +
                     'this directory.')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

error_counter = 0
verbosity_level = 1
do_trace = False
trace_file_name = ""
do_intersection = False
do_background = False
do_pavement_markings = False
screen_width = 3840
screen_height = 2160
show_waypoints = False
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

if (arguments ['show_waypoints'] != None):
  show_waypoints = arguments ['show_waypoints']

if (arguments ['pavement_markings_directory'] != None):
  do_pavement_markings = True
  pavement_markings_directory = arguments ['pavement_markings_directory']
  pavement_markings_directory = pathlib.Path(pavement_markings_directory)

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

# Subroutine to format a ground position or distance for display.
def format_position(the_position):
  return (f'{the_position:07.3f}')

# Subroutine to format a screen position or distance for display.
def format_screen_position (the_position):
  return (f'{the_position:04.0f}')
  

# Subroutine to draw a line from (x1, y1) to (x2, y2) with the specified color
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

# Subroutine to draw a spot at (x1, y1) with specified radius and color.
def draw_spot (the_image, x1, y1, the_radius, the_color):

  screen_y1, screen_x1 = map_location_ground_to_screen (y1, x1)
  screen_radius = convert_ground_size_to_screen_size (the_radius)
  cv2.circle(the_image, (screen_x1, screen_y1), screen_radius, the_color, -1)
  return

# Subroutine to place a small image on a large image, removing what was below
# except for transparent areas.  The anchor point of the small image is placed
# at the indicated location on the large image.

def place_image (name, canvas, image_info, target_orientation, x_feet, y_feet):

  # Calculate the area in the large image that will be replaced.
  # The ground position passed is where the anchor goes.
  
  y_position, x_position = map_location_ground_to_screen (y_feet, x_feet)

  (overlay_name, overlay_image, original_orientation, desired_width,
   desired_height, anchor_x, anchor_y) = image_info

  original_height, original_width = overlay_image.shape[0:2]
  target_height = convert_ground_size_to_screen_size (desired_height)
  target_width = convert_ground_size_to_screen_size (desired_width)

  if (do_trace):
    trace_file.write ("Placing image " + str(overlay_name) +
                      "\n original orientation " + str(original_orientation) +
                      " \n desired ground width: " +
                      format_position(desired_width) + ", height: " +
                      format_position(desired_height) +
                      " \n target orientation: " + str(target_orientation) +
                      "\n at ground location (" +
                      format_position(x_feet) + ", " +
                      format_position(y_feet) + ").\n")

    trace_file.write (" target screen width: " +
                      format_screen_position(target_width) +
                      ", height: " + format_screen_position(target_height) +
                      ".\n")
    trace_file.write (" anchor x: " +
                      format_screen_position(anchor_x) +
                      ", y: " + format_screen_position(anchor_y) +
                      ".\n")

  # Rotate and shrink the image
  
  # Pad the original image with transparency so it has room to rotate
  # without being cropped.
  pad_size = max (original_height, original_width) + 1
  padded_image = cv2.copyMakeBorder (overlay_image, top=pad_size,
                                     bottom=pad_size, left=pad_size,
                                     right=pad_size,
                                     borderType=cv2.BORDER_CONSTANT,
                                     value=(0, 0, 0, 0))
  padded_height, padded_width = padded_image.shape[0:2]
  
  # Adjust the anchor coordinates and target height and width
  # to take the padding into account.
  anchor_x = anchor_x + pad_size
  anchor_y = anchor_y + pad_size
  target_width = int((target_width / original_width) * padded_width)
  target_height = int ((target_height / original_height) * padded_height)

  padded_height, padded_width = padded_image.shape[0:2]

  # If a right-pointing image is to be pointed left, or a left-pointing
  # image is to be pointed right, flip it before rotating it.
  if (((original_orientation > 0) and (target_orientation < 0)) or
      ((original_orientation < 0) and (target_orientation > 0))):
    padded_image = cv2.flip (padded_image, 1)
    target_orientation = -target_orientation
  
  rotation_amount = target_orientation - original_orientation
  
  if (do_trace):
    trace_file.write (" padded anchor x: " +
                      format_screen_position(anchor_x) +
                      ", y: " + format_screen_position(anchor_y) +
                      ".\n")
    trace_file.write (" overlay image screen width: " +
                      format_screen_position(original_width) +
                      ", height: " +
                      format_screen_position(original_height) + ".\n")
    trace_file.write (" padded image screen width: " +
                      format_screen_position(padded_width) +
                      ", height: " +
                      format_screen_position(padded_height) + ".\n")
    trace_file.write (" target screen width: " +
                      format_screen_position(target_width) +
                      ", height: " +
                      format_screen_position(target_height) + ".\n")
    trace_file.write (" rotation amount: " + str(rotation_amount) + ".\n")

  rotation_matrix = cv2.getRotationMatrix2D ((anchor_x, anchor_y),
                                             -math.degrees(rotation_amount),
                                             1)

  if (do_trace):
    trace_file.write (" rotation matrix:\n")
    pprint.pprint (rotation_matrix, trace_file)
    trace_file.write (" padded image:\n")
    pprint.pprint (padded_image, trace_file)
    trace_file.write ("\n")
    
  rotated_image = cv2.warpAffine (padded_image, rotation_matrix,
                                  (padded_width, padded_height))
  rotated_height, rotated_width = rotated_image.shape[0:2]

  if (do_trace):
    trace_file.write (" rotated image: screen width: " +
                      format_screen_position(rotated_width) +
                      ", height: " + format_screen_position(rotated_height) +
                      ".\n")
    pprint.pprint (rotated_image, trace_file)
    trace_file.write ("\n")

  small_image = cv2.resize(rotated_image, (target_width, target_height),
                           interpolation=cv2.INTER_AREA)
  small_height, small_width = small_image.shape[0:2]
  anchor_x = int(anchor_x * (small_width / padded_width))
  anchor_y = int(anchor_y * (small_height / padded_height))
  
  if (do_trace):
    trace_file.write (" reduced from (" +
                      format_screen_position(padded_width) + ", " +
                      format_screen_position(padded_height) + ") to (" +
                      format_screen_position(small_width) +
                      ", " + format_screen_position(small_height) + ").\n")
    trace_file.write (" new anchor x: " + format_screen_position(anchor_x) +
                      " y: " + format_screen_position(anchor_y) + ".\n")
    pprint.pprint (small_image, trace_file)
    trace_file.write ("\n")
    
  eightbit = small_image.astype (np.uint8)
  grey_image = cv2.cvtColor (eightbit, cv2.COLOR_BGR2GRAY)
  thresholded_image = cv2.threshold (grey_image,226,255,cv2.THRESH_BINARY)[1]
  inverted_image = cv2.bitwise_not (thresholded_image)
  x_min, y_min, width, height = cv2.boundingRect(inverted_image)
  x_max = x_min + width
  y_max = y_min + height

  if (do_trace):
    trace_file.write (" anchor placed on screen at (" +
                      format_screen_position(x_position) +
                      ", " + format_screen_position(y_position) + ").\n")
    trace_file.write (" small image enclosing rectangle width: " +
                      format_screen_position(width) +
                      ", height: " + format_screen_position(height) + ".\n")
    trace_file.write (" extent (" + format_screen_position(x_min) + ", " +
                      format_screen_position(y_min) + ") to (" +
                      format_screen_position(x_max) + ", " +
                      format_screen_position(y_max) + ").\n")

  canvas_height, canvas_width = canvas.shape[0:2]

  if (do_trace):
    trace_file.write (" canvas width: " +
                      format_screen_position(canvas_width) +
                      ", height: " +
                      format_screen_position(canvas_height) + ".\n")
  
  pixel_off_canvas = False
  pixels_changed = 0
  pixels_left_unchanged = 0
 
  # Replace the pixels in the area overlapped by the image being placed
  # by the pixels in the image being placed.  However, if there is
  # transparency in the image being placed, let the previous contents
  # show through.
  # The large image is assumed not to have an alpha channel.
  # Don't write any pixels that are off the canvas.

  for y in range(height):
    overlay_y = y + y_min
    canvas_y = overlay_y + y_position - anchor_y
    if ((canvas_y >= 0) and (canvas_y < canvas_height)):
      for x in range(width):
        overlay_x = x + x_min
        canvas_x = overlay_x + x_position - anchor_x
        if ((canvas_x >= 0) and (canvas_x < canvas_width)):
      
          # Elements 0 to 2 are the color channels.
          overlay_blue = small_image[overlay_y, overlay_x, 0]
          overlay_green = small_image[overlay_y, overlay_x, 1]
          overlay_red = small_image[overlay_y, overlay_x, 2]

          # Element 3 is the alpha channel, 0 to 65535, where 0 means
          # transparent and 65535 means opaque.  Values in between are
          # semi-transparent.
          # We convert the alpha value to the range 0 to 1.
          overlay_alpha = small_image[overlay_y, overlay_x, 3] / 65535.0
          overlay_beta = 1.0 - overlay_alpha
      
          if (do_trace and (trace_level > 1)):
            trace_file.write (" Overlay pixel at (" +
                              format_screen_position(overlay_x) + ", " +
                              format_screen_position(overlay_y) + "): (" +
                              format_screen_position(overlay_blue) + ", " +
                              format_screen_position(overlay_green) + ", " +
                              format_screen_position(overlay_red) + ", " +
                              format_screen_position(overlay_alpha) + ").\n")

          # Compute the desired color by combining the new color with
          # the old, taking into account the transparency.  If the overlay
          # pixel is fully transparent we need do nothing.

          if (overlay_alpha > 0):        
            canvas_blue = canvas[canvas_y, canvas_x, 0]
            canvas_green = canvas[canvas_y, canvas_x, 1]
            canvas_red = canvas[canvas_y, canvas_x, 2]
                      
            composite_blue = ((canvas_blue * overlay_beta) +
                              (overlay_blue * overlay_alpha))
            composite_green = ((canvas_green * overlay_beta) +
                               (overlay_green * overlay_alpha))
            composite_red = ((canvas_red * overlay_beta) +
                             (overlay_red * overlay_alpha))

            # Store the new color in the appropriate place in the canvas.
            canvas[canvas_y, canvas_x, 0] = composite_blue
            canvas[canvas_y, canvas_x, 1] = composite_green
            canvas[canvas_y, canvas_x, 2] = composite_red

            pixels_changed = pixels_changed + 1

            if (do_trace and (trace_level > 1)):
              trace_file.write ("Pixel at (" +
                                format_screen_position(canvas_x) + ", " +
                                format_screen_position(canvas_y) +
                                ") changed from (" +
                                format_screen_position(canvas_blue) + ", " +
                                format_screen_position(canvas_green) + ", " +
                                str(canvas_red) + ") to (" +
                                str(composite_blue) + ", " +
                                str(composite_green) + ", " +
                                str(composite_red) + ".\n")
          else:
            pixels_left_unchanged = pixels_left_unchanged + 1
            
        else:
          pixel_off_canvas = True
    else:
      pixel_off_canvas = True

  if (do_trace):
    if ((pixels_changed + pixels_left_unchanged) > 0):
      if (pixel_off_canvas):
        trace_file.write (" Image partly placed: " + str(pixels_changed) +
                          " pixels changed and " + str(pixels_left_unchanged) +
                          " left unchanged.\n")
      else:
        trace_file.write (" Image fully placed: " + str(pixels_changed) +
                          " pixels changed and " + str(pixels_left_unchanged) +
                          " left unchanged.\n")
    else:
      trace_file.write (" Image not placed.\n")
    
  return
  
# The colors
color_black = (0, 0, 0)
color_green = (0, 65535, 0)
color_light_blue = (50000, 30000, 30000)
color_light_red = (30000, 30000, 50000)
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

# Draw pavement markings if a directory holding the images was specified.
if (do_pavement_markings):
  for lane_name in lanes_info:
    lane = lanes_info [lane_name]
    top_x = int(lane["top x"])
    top_y = int(lane["top y"])
    lane_width = float(lane["width"])
    for pavement_marking in lane["pavement markings"]:
      file_name = pavement_marking["file name"]
      file_name = pathlib.Path(file_name)
      offset_x, offset_y = pavement_marking["offset"]
      target_orientation = pavement_marking ["orientation"]
      target_width = pavement_marking["width"]
      
      if (do_trace):
        trace_file.write ("Lane " + lane_name + " pavement marking " +
                          "at offset (" +
                          str(offset_x) + ", " + str(offset_y) + ") " +
                          "orientation: " + str(target_orientation) + "\n" +
                          " width: " + str(target_width) +
                          " file name: " + file_name + ".\n")

      pavement_image_path = pavement_markings_directory / file_name
      
      if (do_trace):
        trace_file.write ("Reading pavement image " +
                          str(pavement_image_path) + ".\n")
      
      pavement_image = cv2.imread(pavement_image_path, cv2.IMREAD_UNCHANGED)
      if ((pavement_image is None) and (verbosity_level >= 1)):
        print ("Image name " + str(pavement_image_path) + " not found.")
      
      pavement_image_height, pavement_image_width = pavement_image.shape[0:2]
    
      if (do_trace):
        trace_file.write (" width: " + str(pavement_image_width) +
                          ", height: " +
                          str(pavement_image_height) + ".\n")
      
      desired_width = target_width  
      desired_height = (desired_width *
                        (pavement_image_height / pavement_image_width))
      anchor_x = int (pavement_image_width / 2)
      anchor_y = 0
  
      pavement_image_info = (pavement_image_path, pavement_image,
                             math.radians(0), desired_width, desired_height,
                             anchor_x, anchor_y)
      place_image (lane_name, image, pavement_image_info,
                   target_orientation, top_x + offset_x, top_y + offset_y)
      
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
    trace_file.write ("Info for lane " + lane_name + ":\n")
    pprint.pprint ((top_x, top_y, bottom_x, bottom_y), trace_file)
    pprint.pprint ((p1_x, p1_y, p2_x, p2_y), trace_file)
    pprint.pprint ((p3_x, p3_y, p4_x, p4_y), trace_file)

# Draw each lane's center line.
for travel_path_name in travel_paths:
  travel_path = travel_paths [travel_path_name]
  milestones = travel_path ["milestones"]
  previous_milestone = None
  for this_milestone in milestones:
    if (previous_milestone != None):
      previous_x = previous_milestone[1]
      previous_y = previous_milestone[2]
      this_x = this_milestone[1]
      this_y = this_milestone[2]
      draw_line (image, previous_x, previous_y, this_x, this_y,
                 color_light_blue, 0.25, False)
    previous_milestone = this_milestone
      
# Mark each waypoint if requested.
if (show_waypoints):
  for travel_path_name in travel_paths:
    travel_path = travel_paths [travel_path_name]
    milestones = travel_path ["milestones"]
    for milestone in milestones:
      x_position = milestone[1]
      y_position = milestone[2]
      draw_spot (image, x_position, y_position, 0.25, color_light_red)
  
# Place names on the lanes.
font_face = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 2
font_color = color_white
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
