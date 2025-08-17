#!/usr/bin/python3
# -*- coding: utf-8
#
# process_events.py renders the events output from the traffic signal
# simulator.

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
import pprint
import decimal
import fractions
import csv
import pathlib
import json
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Render the output of the traffic signal simulator.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='process_events 0.44 2025-08-11',
                     help='print the version number and exit')
parser.add_argument ('--animation-directory', metavar='animation_directory',
                     help='write animation output image files ' +
                     'into the specified directory')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--events-file', metavar='events_file',
                     help='read event output from the traffic simulator')
parser.add_argument ('--background-file', metavar='background_file',
                     help='the image to draw the animation upon')
parser.add_argument ('--intersection-file', metavar='intersection_file',
                     help='the locations and shapes of the signal faces')
parser.add_argument ('--start-time', type=decimal.Decimal,
                     metavar='start_time',
                     help='when in the simulation to start the animation')
parser.add_argument ('--start-frame', type=decimal.Decimal,
                     metavar='start_frame',
                     help='the first frame to render, default 1')
parser.add_argument ('--end-frame', type=decimal.Decimal,
                     metavar='end_frame',
                     help='the last frame to render, default unlimited')
parser.add_argument ('--duration', type=decimal.Decimal, metavar='duration',
                     help='how long to run the animation')
parser.add_argument('--FPS', type=decimal.Decimal, metavar='FPS',
                    help='number of frames per second in the animation, ' +
                    'default is 30')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_animation_output = False
animation_directory_name = ""
do_events_input = False
events_file_name = ""
do_background = False
background_file_name = ""
do_intersection = False
intersection_file_name = ""
start_time = decimal.Decimal("0.000")
start_frame = 0
end_frame = None
duration_time = None
verbosity_level = 1
error_counter = 0

ground_height = 143
lane_width  = 12

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_level = 1
  trace_file_name = arguments ['trace_file']
  trace_file_name = pathlib.Path(trace_file_name)
  trace_file = open (trace_file_name, 'wt')

if (arguments ['animation_directory'] != None):
  do_animation_output = True
  animation_directory_name = arguments ['animation_directory']
  animation_directory_name = pathlib.Path(animation_directory_name)

if (arguments ['events_file'] != None):
  do_events_input = True
  events_file_name = arguments ['events_file']
  events_file_name = pathlib.Path(events_file_name)

if (arguments ['background_file'] != None):
  do_background = True
  background_file_name = arguments ['background_file']
  background_file_name = pathlib.Path(background_file_name)

if (arguments ['intersection_file'] != None):
  do_intersection = True
  intersection_file_name = arguments ['intersection_file']
  intersection_file_name = pathlib.Path(intersection_file_name)

if (arguments ['start_time'] != None):
  start_time = arguments ['start_time']

if (arguments ['start_frame'] != None):
  start_frame = int(arguments ['start_frame'])

if (arguments ['end_frame'] != None):
  end_frame = int(arguments ['end_frame'])

if (arguments ['duration'] != None):
  duration_time = arguments ['duration']
  
if (arguments ['FPS'] != None):
  frames_per_second = int(arguments ['FPS'])
else:
  frames_per_second = 30
  
if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

# Subroutine to format the time for display.
def format_time(the_time):
  return (f'{the_time:07.3f}')

# Subroutine to format a ground position or distance for display.
def format_position(the_position):
  return (f'{the_position:07.3f}')

# Subroutine to format a screen position or distance for display.
def format_screen_position (the_position):
  return (f'{the_position:04.0f}')
  
start_time = fractions.Fraction(start_time)

if (duration_time != None):
  duration_time = fractions.Fraction(duration_time)

# Read the events file, if one was specified.

# The events dictionary is indexed by time.
# Each entry is a list of events that happen at that time.
events = dict()

latest_time = fractions.Fraction(0)

if (do_events_input):
  with open (events_file_name, 'r') as events_file:
    reader = csv.DictReader (events_file)
    for row in reader:

      if (do_trace):
        trace_file.write ("Reading a row from the CSV file:\n")
        pprint.pprint (row, trace_file)
        
      the_time = fractions.Fraction (row['time'])
      if (the_time > latest_time):
        latest_time = the_time
      if (the_time not in events):
        events[the_time] = list()
      events_list = events[the_time]
      the_lane_name = row['lane']
      the_type = row['type']
      the_color = row['color']
      the_name = row['name']
      position_x = row['position_x']
      if (position_x != None):
        position_x = fractions.Fraction(position_x)
      position_y = row['position_y']
      if (position_y != None):
        position_y = fractions.Fraction(position_y)
      destination_x = row['destination_x']
      if (destination_x != None):
        destination_x = fractions.Fraction(destination_x)
      destination_y = row['destination_y']
      if (destination_y != None):
        destination_y = fractions.Fraction(destination_y)
      orientation = row['orientation']
      if (orientation != None):
        orientation = float(fractions.Fraction(orientation))
      the_length = row['length']
      if (the_length != None):
        the_length = fractions.Fraction(the_length)
      the_speed = row['speed']
      if (the_speed != None):
        the_speed = fractions.Fraction(the_speed)
      the_travel_path_name = row['travel path']
      the_presence = row['present']
      match the_presence:
        case "True":
          the_presence = True
        case "False":
          the_presence = False

      the_event = dict()
      the_event["time"] = the_time
      the_event["name"] = the_name
      the_event["lane name"] = the_lane_name
      the_event["type"] = the_type
      the_event["color"] = the_color
      the_event["counter"] = None
      the_event["position x"] = position_x
      the_event["position y"] = position_y
      the_event["destination x"] = destination_x
      the_event["destination y"] = destination_y
      the_event["orientation"] = orientation
      the_event["length"] = the_length
      the_event["speed"] = the_speed
      the_event["travel path"] = the_travel_path_name
      the_event["present"] = the_presence
      the_event["source"] = "script"
      
      events_list.append(the_event)

# Run the animation for one second after the last event
# unless the duration is specified.
if (duration_time == None):
  duration_time = latest_time - start_time + 1
end_time = start_time + duration_time

# Read the intersection file, which has information about the
# signal faces.
if (do_intersection):
  intersection_file = open (intersection_file_name, 'r')
  intersection_info = json.load (intersection_file)
  intersection_file.close()
else:
  intersection_info = None

lanes_info = intersection_info["lanes info"]

signal_faces_list = intersection_info["signal faces"]
signal_faces_dict = dict()
for signal_face in signal_faces_list:
  signal_face_name = signal_face["name"]
  signal_faces_dict[signal_face_name] = signal_face

# Place markers in the timeline for where we will output a frame.
frame_interval = fractions.Fraction(1, frames_per_second)

event_time = start_time
while (event_time <= end_time):
  if (event_time not in events):
    events[event_time] = list()
  events_list = events[event_time]
  event = dict()
  event["type"] = "frame"
  event["time"] = event_time
  event["source"] = "framer"
  events_list.append(event)
  event_time = event_time + frame_interval

# Cause the flashing lights to flash.
# Make a list of flashing lights
current_flashers = dict()
completed_flashers = list()
event_times = sorted(events.keys())
for event_time in event_times:
  events_list = events[event_time]
  for event in events_list:
    type = event["type"]
    if (type == "lamp"):
      lane_name = event["lane name"]
      the_color = event["color"]
      # If we are changing the color of an existing flasher, we have found
      # the end time of the flashing.  Ignore flashers with 0 time.
      if (lane_name in current_flashers):
        flasher = current_flashers[lane_name]
        if (the_color != flasher["color"]):
          flasher["stop time"] = event_time
          if (flasher["stop time"] > flasher["start time"]):
            completed_flashers.append(flasher)
          del current_flashers[lane_name]
      if (do_trace):
        trace_file.write ("Time " + format_time(event_time) + " lane " +
                          lane_name + " color " + the_color + ".\n")
      if (the_color[0:8] == "Flashing"):
        if (do_trace):
          trace_file.write ("We have a flasher.\n")
        if (lane_name in current_flashers):
          if (do_trace):
            trace_file.write ("Duplicate flasher.\n")
        else:
          flasher = dict()
          flasher["start time"] = event_time
          flasher["lane name"] = lane_name
          flasher["color"] = the_color
          current_flashers[lane_name] = flasher
          
# Go through the list of flashing lights inserting color changes.

# The cycle time is between 55 and 60 flashes per minute.
# Split the difference and convert to seconds.
flash_cycle_time = (fractions.Fraction(60) /
                    ((fractions.Fraction(60) + fractions.Fraction(55)) /
                     fractions.Fraction(2)))
# The iluminated time is one half to two thirds of the cycle.  Split the
# difference.
flash_light_time = flash_cycle_time * ((fractions.Fraction(1, 2) +
                                        fractions.Fraction(2, 3)) /
                                       fractions.Fraction(2))

if (do_trace):
  trace_file.write ("Flashing: cycle " + format_time(flash_cycle_time) +
                    ", light " + format_time(flash_light_time) + "\n")
  pprint.pprint(completed_flashers, trace_file)

# The flashing light is iluminated at the start time.
# At the stop time the light is changed to a different color.  
for flasher in completed_flashers:
  flasher_start_time = flasher["start time"]
  flasher_stop_time = flasher["stop time"]
  event_time = flasher_start_time
  while (event_time < flasher_stop_time):
    if (do_trace):
      trace_file.write ("Top of flasher loop: now " +
                        format_time(event_time) + " start " +
                        format_time(flasher_start_time) + " stop " +
                        format_time(flasher_stop_time) + "\n")
    go_dark_time = event_time + flash_light_time
    if (go_dark_time >= flasher_stop_time):
      break
    # Make the lamp dark
    event = dict()
    event["type"] = "lamp"
    event["lane name"] = flasher["lane name"]
    event["color"] = "Dark"
    event["counter"] = None
    event["source"] = "flasher"
    event["time"] = go_dark_time
    if (go_dark_time not in events):
      events[go_dark_time] = list()
    events_list = events[go_dark_time]
    events_list.append(event)
    if (do_trace):
      trace_file.write ("Going dark: " + format_time(go_dark_time) + " lane " +
                        event["lane name"] + ".\n")
    # at the end of the interval, make it light again
    go_light_time = event_time + flash_cycle_time
    if (go_light_time >= flasher_stop_time):
      break
    event = dict()
    event["type"] = "lamp"
    event["lane name"] = flasher["lane name"]
    event["color"] = flasher["color"]
    event["counter"] = None
    event["source"] = "flasher"
    event["time"] = go_light_time
    if (go_light_time not in events):
      events[go_light_time] = list()
    events_list = events[go_light_time]
    events_list.append(event)
    if (do_trace):
      trace_file.write ("Going light: " + format_time(go_light_time) +
                        " lane " + event["lane name"] + ".\n")
    event_time = go_light_time

# Make the crosswalk count down to Don't Walk.
# Make a list of crosswalk signals.
current_crossers = dict()
completed_crossers = list()
event_times = sorted(events.keys())
for event_time in event_times:
  events_list = events[event_time]
  for event in events_list:
    type = event["type"]
    if (type == "lamp"):
      lane_name = event["lane name"]
      the_color = event["color"]
      # If we are changing the color of an existing crosser, we have found
      # the end time of the crosser.
      if (lane_name in current_crossers):
        crosser = current_crossers[lane_name]
        if (the_color != crosser["color"]):
          crosser["countdown stop time"] = event_time
          completed_crossers.append(crosser)
          del current_crossers[lane_name]
      if (do_trace):
        trace_file.write ("Time " + format_time(event_time) + " lane " +
                          lane_name + " color " + the_color + ".\n")
      if (the_color == "Walk with Countdown"):
        if (do_trace):
          trace_file.write ("We have a crosser.\n")
        crosser = dict()
        crosser["countdown start time"] = event_time
        crosser["lane name"] = lane_name
        crosser["color"] = the_color
        crosser["start event"] = event
        current_crossers[lane_name] = crosser
          
# Go through the list of counting down lights inserting the countdown value.

if (do_trace):
  trace_file.write ("Countdown signals:\n")
  pprint.pprint(completed_crossers, trace_file)

# Starting one second before the sign changes to Don't Walk,
# show the countdown to the sign change.
for crosser in completed_crossers:
  crosser_start_time = crosser["countdown start time"]
  crosser_stop_time = crosser["countdown stop time"]
  event_time = crosser_stop_time - 1
  counter = 1
  while (event_time > crosser_start_time):
    if (do_trace):
      trace_file.write ("Top of crosser loop: now " +
                        format_time(event_time) + " start " +
                        format_time(crosser_start_time) + " stop " +
                        format_time(crosser_stop_time) + "\n")
    event = dict()
    event["type"] = "lamp"
    event["lane name"] = crosser["lane name"]
    event["color"] = crosser["color"]
    event["counter"] = counter
    event["source"] = "crosser"
    event["time"] = event_time
    if (event_time not in events):
      events[event_time] = list()
    events_list = events[event_time]
    events_list.append(event)
    if (do_trace):
      trace_file.write ("Crossing: " + format_time(event_time) + " lane " +
                        event["lane name"] + ".\n")
    counter = counter + 1
    event_time = event_time - 1

  # Also fix up the initial event.  This display won't last a full second.
  event = crosser["start event"]
  event["counter"] = counter
    
if (do_trace):
  trace_file.write ("Events:\n")
  pprint.pprint (events, trace_file)
  trace_file.write ("\n")

# Read the background file.
if (do_background):
  background=cv2.imread(background_file_name, cv2.IMREAD_UNCHANGED)
else:
  screen_width = 3840
  screen_height = 2160
  color_gray = (40000, 40000, 40000)
  background = np.full (shape=(screen_height, screen_width, 3),
                        fill_value = color_gray).astype(np.uint16)
  
if (do_trace):
  trace_file.write ("background image:\n")
  pprint.pprint (background, trace_file)
  
canvas_size = background.shape[0:2]

# Subroutine to map ground locations to screen locations.
# The ground has its origin at the center of the intersection, which is also
# the center of the screen.  The screen has its origin at the upper left
# corner.
def map_location_ground_to_screen (y_feet, x_feet):
  global ground_height
  global background
  
  screen_height, screen_width = background.shape[0:2]

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
  global background

  screen_height, screen_width = background.shape[0:2]
  size_in_pixels = size_in_feet * (screen_height / ground_height)
  return (int(size_in_pixels))
          
# Subroutine to map screen locations to ground locations.
# The screen has its origin at the top left, while the ground has its origin
# in the center of the screen.
def map_location_screen_to_ground (y_pixels, x_pixels):
  global ground_height
  global background
  
  screen_height, screen_width = background.shape[0:2]
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
  global background

  screen_height, screen_width = background.shape[0::2]
  size_in_feet = size_in_pixels * (ground_height / screen_height)
  return (int(size_in_feet))

# Place a small image on a large image, removing what was below
# except for transparent areas.  The anchor point of the small image is placed
# at the indicated location on the large image.
small_image_cache = dict()

def place_image (name, canvas, image_info, target_orientation, x_feet, y_feet):
  global small_image_cache

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

  # If the image is cached we can save a lot of time.
  small_image_cache_key = (str(overlay_name) + " / " +
                           format_position(desired_height) +
                           " / " + format_position(desired_width) + " / " +
                           str(target_orientation) + " //.")
  if (do_trace):
    trace_file.write (" small image cache key: " + small_image_cache_key +
                      "\n")
                           
  if (small_image_cache_key in small_image_cache):
    image_dict = small_image_cache[small_image_cache_key]
    small_image = image_dict["small image"]
    height = image_dict["height"]
    width = image_dict["width"]
    anchor_x = image_dict["anchor x"]
    anchor_y = image_dict["anchor y"]
    x_min = image_dict["x min"]
    x_max = image_dict["x max"]
    y_min = image_dict["y min"]
    y_max = image_dict["y max"]
  else:
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
    
    rotated_image = cv2.warpAffine (padded_image, rotation_matrix,
                                  (padded_width, padded_height))
    rotated_height, rotated_width = rotated_image.shape[0:2]

    if (do_trace):
      trace_file.write (" rotated image: screen width: " +
                        format_screen_position(rotated_width) +
                        ", height: " + format_screen_position(rotated_height) +
                        ".\n")

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

    # Capture the information needed to place this image on the canvas.
    image_dict = dict()
    image_dict["small image"] = small_image
    image_dict["height"] = height
    image_dict["width"] = width
    image_dict["anchor x"] = anchor_x
    image_dict["anchor y"] = anchor_y
    image_dict["x min"] = x_min
    image_dict["x max"] = x_max
    image_dict["y min"] = y_min
    image_dict["y max"] = y_max

    small_image_cache[small_image_cache_key] = image_dict
  
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
  # show through.  This is imprecise because the pixel color values
  # are companded in sRGB, but it is close enough for our purposes,
  # and converting to linear to do the alpha blending properly would
  # be time-consuming.
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
  
# Subroutine to choose the correct stoplight image given its lane and color.
image_cache = dict()

def choose_lamp_image (lane):
  global image_cache
  global lane_width

  lane_name = lane["name"]
  lane_color = lane["color"]
  lane_counter = lane["counter"]

  signal_face = signal_faces_dict[lane_name]
  this_lane_info = lanes_info [lane_name]
  
  if (do_trace):
    trace_file.write ("Choosing an image for lane: " + lane_name +
                      ", color = " + lane_color + ".\n")
    pprint.pprint (lane, trace_file)
    pprint.pprint (this_lane_info, trace_file)
    pprint.pprint (signal_face, trace_file)
    trace_file.flush()
    
  root = this_lane_info["root signal face image"]
  image_name = "none found"
    
  if (root == "MUTCD_Ped_Signal_-"):
    match lane_color:
      case "Don't Walk":
        image_name = (root + "_Steady_hand.png")
      case "Walk":
        image_name = (root + "_Walk.png")
      case "Walk with Countdown":
        image_name = (root + f'_Hand_with_timer-{lane_counter:02d}.png')
                         
  else:
    match lane_color:
      case "Steady Circular Red" | "Steady Left Arrow Red" | \
           "Flashing Left Arrow Red" | "Steady Right Arrow Red" | \
           "Flashing Circular Red":
        image_name = (root + "_Red.png")
      case "Flashing Left Arrow Yellow (lower)":
        image_name = (root + "_Flashing_Yellow.png")
      case "Steady Circular Green" | "Steady Left Arrow Green" | \
           "Steady Left Arrow Green and Steady Circular Green":
        image_name = (root + "_Green.png")
      case "Steady Circular Yellow" | "Steady Left Arrow Yellow (upper)" | \
           "Flashing Left Arrow Yellow (upper)" | "Flashing Circular Yellow":
        image_name = (root + "_Yellow.png")
      case "Dark":
        if (len(root) == 10):
          image_name = "signal_Dark_3.png"
        else:
          image_name = "signal_Dark_4.png"
          
  if (do_trace):
    trace_file.write ("Image chosen is " + image_name + ".\n")

  if ((image_name == "none found") and (verbosity_level >= 1)):
    print ("No image chosen for root " + root + ", lane name " + lane_name +
           ", color " + lane_color + ".")
    
  image_path = pathlib.Path(image_name)
  if (image_path in image_cache):
    image = image_cache[image_path]
    image_height, image_width = image.shape[0:2]
  else:
    if (do_trace):
      trace_file.write ("Reading image " + str(image_path) + ".\n")
      
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if ((image is None) and (verbosity_level >= 1)):
      print ("Image name " + str(image_path) + " not found.")
      print (" root " + root + " lane name " + lane_name +
             " lane color " + lane_color + ",")
      
    image_height, image_width = image.shape[0:2]
    
    if (do_trace):
      trace_file.write (" width: " + str(image_width) + ", height: " +
                        str(image_height) + ".\n")
    image_cache[image_path] = image

  if (root == "MUTCD_Ped_Signal_-"):
    desired_width = lane_width
  else:
    desired_width = lane_width / 3.0
      
  desired_height = desired_width * (image_height / image_width)
  anchor_x = int (image_width / 2)
  anchor_y = 0
  
  image_info = (image_path, image, math.radians(0), desired_width,
                desired_height, anchor_x, anchor_y)
  return (image_info)
  
# Subroutine to choose the image for a moving object.
def choose_moving_object_image (object_type, orientation, length):
  global image_cache
  
  match object_type:
   case "car":
     image_name = "car-38800411-up.png"
     orientation = math.radians(0)
     expansion_factor = 1.0
         
   case "truck":
     image_name = "truck-51893967-up.png"
     orientation = math.radians(0)
     expansion_factor = 1.0
         
   case "pedestrian":
     image_name = "man_walking_right.png"
     orientation = math.radians(90)
     expansion_factor = 5.0

  image_path = pathlib.Path(image_name)

  if (image_path in image_cache):
    image = image_cache[image_path]
  else:
    if (do_trace):
      trace_file.write ("Reading image " + str(image_path) + ".\n")
      
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if (do_trace):
      trace_height, trace_width = image.shape[0:2]
      trace_file.write (" size (" + str(trace_width) + ", " +
                        str(trace_height) + ").\n")
    image_cache[image_path] = image
        
  image_height, image_width = image.shape[0:2]

  match object_type:
    case "car" | "truck":
      anchor_x = int (image_width / 2)
      anchor_y = 0

    case "pedestrian":
      anchor_x = int (image_width / 2)
      anchor_y = int (image_height / 2)
      
  shrink_factor = expansion_factor * (length / image_height)
        
  image_info = (image_path, image, orientation, image_width * shrink_factor,
                image_height * shrink_factor, anchor_x, anchor_y)
  return (image_info)


# Subroutine to find the starting location for a lane.  The traffic signal
# for this lane is placed at an offset from this location.
# This is the place where moving objects stop if they cannot
# enter the intersection and where moving objects leaving
# the intersection enter the lane.
# These locations are in the ground coordinate system, which has its origin
# in the center of the screen and in which distances are measured in feet.
def find_lane_position (lane_name):
  this_lane_info = lanes_info [lane_name]
  top_x = this_lane_info["top x"]
  top_y = this_lane_info["top y"]
  return (top_x, top_y)
    
# Subroutine to find the offset of the traffic signal relative to the
# origin of the lane.
def find_signal_offset (signal_face_name):
  signal_face = signal_faces_dict[signal_face_name]
  offset_x = signal_face["offset x"]
  offset_y = signal_face["offset y"]
  return (offset_x, offset_y)
  
# Create the lanes data structures which will record
# the changing state of the traffic control signal
# for that lane with the passage of time and hold
# information about the location and orientation
# of that lane.

lanes_dict = dict()
for lane_name in lanes_info:
  lane = dict()
  if (lane_name in signal_faces_dict):
    lane["name"] = lane_name
    lane["color"] = "Dark"
    lane["position x"], lane["position y"] = find_lane_position (lane_name)
    lane["signal offset"] = find_signal_offset(lane_name)
    lanes_dict[lane_name] = lane
  else:
    lane["name"] = lane_name
    lane["color"] = "Blank"
    lane["position x"], lane["position y"] = find_lane_position (lane_name)
    lanes_dict[lane_name] = lane

if (do_trace):
  trace_file.write ("Lanes:\n")
  pprint.pprint (lanes_dict, trace_file)
  
# Create a data structure to hold information about moving objects.
event_times = sorted(events.keys())
moving_objects_dict = dict()

for event_time in event_times:
  events_list = events[event_time]
  for event in events_list:
    type = event["type"]
    match type:
      case "car" | "truck" | "pedestrian":
        the_name = event["name"]
        if (the_name not in moving_objects_dict):
          moving_object = dict()
          moving_objects_dict[the_name] = moving_object
        moving_object = moving_objects_dict[the_name]
        moving_object["name"] = the_name
        moving_object["type"] = type
        moving_object["position x"] = event["position x"]
        moving_object["position y"] = event["position y"]
        moving_object["destination x"] = event["destination x"]
        moving_object["destination y"] = event["destination y"]
        moving_object["orientation"] = event["orientation"]
        moving_object["time at position"] = event_time
        moving_object["length"] = event["length"]
        moving_object["present"] = False
        moving_object["travel path"] = event["travel path"]
        moving_object["lane name"] = event["lane name"]

if (do_trace):
  trace_file.write ("Moving objects:\n")
  pprint.pprint(moving_objects_dict, trace_file)

# Subroutine to determine the present location of a moving object.
def find_moving_object_location (event_time, moving_object):

  if (do_trace):
    trace_file.write ("Finding the location of moving object:\n")
    pprint.pprint (moving_object, trace_file)
    
  position_x = moving_object["position x"]
  position_y = moving_object["position y"]

  # Allow for the object's movement since it left this position.
  position_time = moving_object["time at position"]
  delta_time = event_time - position_time
  distance_moved = delta_time * moving_object["speed"]
  destination_x = moving_object["destination x"]
  destination_y = moving_object["destination y"]
  distance_x = destination_x - position_x
  distance_y = destination_y - position_y
  distance_to_destination = math.sqrt((distance_x**2) + (distance_y**2))
  if (distance_to_destination == 0):
    x = destination_x
    y = destination_y
  else:
    if (distance_moved == 0):
      x = position_x
      y = position_y
    else:
      distance_fraction = distance_moved / distance_to_destination
      x = position_x + (distance_fraction * distance_x)
      y = position_y + (distance_fraction * distance_y)
  
  if (do_trace):
    trace_file.write ("found at " + format_position(x) + "," +
                      format_position(y) + ".\n")
    
  return (x, y)
  
# Update the states of the lamps and moving objeects,
# and generate the animation image frames.
frame_number = -1

if (do_trace):
  trace_file.write ("Start: " + format_time(start_time) +
                    " duration: " + format_time(duration_time) +
                    " end: " + format_time(end_time) + ".\n")

for event_time in event_times:
  events_list = events[event_time]
  for event in events_list:
    type = event["type"]
    match type:
      case "lamp":
        lane_name = event["lane name"]
        the_color = event["color"]
        lane = lanes_dict[lane_name]
        lane["color"] = the_color
        lane["counter"] = event["counter"]
        
        if (do_trace):
          trace_file.write ("Lamp: " + format_time(event_time) + " lane " +
                           lane_name + " color " + the_color + " " +
                            str(lane["counter"]) + ".\n")
        
      case "car" | "truck" | "pedestrian":
        moving_object_name = event["name"]
        moving_object = moving_objects_dict[moving_object_name]
        moving_object["lane name"] = event["lane name"]
        moving_object["position x"] = event["position x"]
        moving_object["position y"] = event["position y"]
        moving_object["destination x"] = event["destination x"]
        moving_object["destination y"] = event["destination y"]
        moving_object["orientation"] = event["orientation"]
        moving_object["speed"] = event["speed"]
        moving_object["time at position"] = event["time"]
        moving_object["present"] = event["present"]

        if (do_trace):
          trace_file.write ("Moving object updated:\n")
          pprint.pprint (moving_object, trace_file)
        
      case "frame":
        if (do_trace):
          trace_file.write ("Frame at " + format_time(event_time) + ":\n")
          trace_file.flush()

        # Don't start counting frames until we are within the animation time.
        if (event_time < start_time):
          continue
        if (event_time > end_time):
          continue

        frame_number = frame_number + 1
        
        # Render the frame only if we are within the frame limits.
        if (frame_number < start_frame):
          continue
        if ((end_frame != None) and (frame_number > end_frame)):
          continue
        
        if (do_trace):
            trace_file.write ("In time and frame range.\n")

        the_time = event["time"]
        frame_start_time = time.clock_gettime_ns (time.CLOCK_BOOTTIME)
        root_name = "frame_" + "{:06d}".format(frame_number) + ".png"
        file_path = pathlib.Path(animation_directory_name, root_name)
        canvas = background.copy()
        if (do_trace):
          trace_file.write ("Initial canvas for frame " + str(frame_number) +
                            ":\n")
          pprint.pprint (canvas, trace_file)
          
        # Draw the signals in their current state.
        for lane_name in lanes_dict:
          lane = lanes_dict[lane_name]
          color = lane["color"]
          if (color != "Blank"):
            image_info = choose_lamp_image (lane)
            x_feet = lane["position x"]
            y_feet = lane["position y"]
            x_feet = x_feet + lane["signal offset"][0]
            y_feet = y_feet + lane["signal offset"][1]
            place_image (lane_name, canvas, image_info, 0,
                         x_feet, y_feet)
              
        # Draw the moving objects: pedestrians and vehicles.
        for moving_object_name in moving_objects_dict:
          moving_object = moving_objects_dict[moving_object_name]
          if (moving_object["present"]):
            type = moving_object["type"]
            name = moving_object["name"]
            x_feet, y_feet = find_moving_object_location (event_time,
                                                          moving_object)
            y_pixels, x_pixels = map_location_ground_to_screen (y_feet,
                                                                x_feet)
            the_orientation = moving_object["orientation"]
            image_info = choose_moving_object_image (type, the_orientation,
                                                     moving_object["length"])
            place_image (name, canvas, image_info, the_orientation,
                         x_feet, y_feet)
              
        if (do_animation_output):
          if (do_trace):
            trace_file.write ("Writing frame " + str(file_path) + ".\n")
            pprint.pprint (canvas, trace_file)
          cv2.imwrite (file_path, canvas)

        frame_end_time = time.clock_gettime_ns (time.CLOCK_BOOTTIME)
        frame_process_time = frame_end_time - frame_start_time
        if (verbosity_level > 2):
          print ("Frame " + str(frame_number) + " created in " +
                 str(int(frame_process_time / 1e9)) + " seconds.")
        if (do_trace):
          trace_file.write (" frame processing time: " +
                            str(frame_process_time / 1e9) + " seconds.\n")

if (do_trace):
  trace_file.write ("Image cache:\n")
  pprint.pprint (image_cache, trace_file)
  trace_file.write ("Small image cache:\n")
  pprint.pprint (small_image_cache, trace_file)
  
if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file process_events.py
