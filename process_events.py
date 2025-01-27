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

#import sys
#import re
#import hashlib
#import datetime
#from jdcal import gcal2jd, jd2gcal
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
                     version='process_events 0.13 2025-01-26',
                     help='print the version number and exit')
parser.add_argument ('--animation-directory', metavar='animation_directory',
                     help='write animation output image files ' +
                     'into the specified directory')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--events-file', metavar='events_file',
                     help='read event output from the traffic simulator')
parser.add_argument ('--start', type=decimal.Decimal, metavar='start',
                     help='when in the simulation to start the animation')
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
start_time = decimal.Decimal("0.000")
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

if (arguments ['start'] != None):
  start_time = arguments ['start']

if (arguments ['duration'] != None):
  duration_time = arguments ['duration']
  
if (arguments ['FPS'] != None):
  frames_per_second = arguments ['FPS']
else:
  frames_per_second = 30
  
if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

# Subroutine to format the time for display.
def format_time(the_time):
  return (f'{the_time:07.3f}')

# Subroutine to format a position or distance for display.
def format_position(the_position):
  return (f'{the_position:07.3f}')
  
start_time = fractions.Fraction(start_time)
if (duration_time != None):
  duration_time = fractions.Fraction(duration_time)

# Read the events file, if one was specified.

# The events dictionary is indexed by time.
# Each entry is a list of events that happen at that time.
events = dict()

latest_time = fractions.Fraction(0)

if (do_events_input):
  with open (events_file_name, 'rt') as events_file:
    reader = csv.DictReader (events_file)
    for row in reader:
      the_time = fractions.Fraction (row['time'])
      if (the_time > latest_time):
        latest_time = the_time
      if (the_time not in events):
        events[the_time] = list()
      events_list = events[the_time]
      the_name = row['name']
      the_lane_name = row['lane']
      the_type = row['type']
      the_position = row['position']
      if (the_position != ""):
        the_position = fractions.Fraction(the_position)
      the_length = row['length']
      if (the_length != ""):
        the_length = fractions.Fraction(the_length)
      the_speed = row['speed']
      if (the_speed != ""):
        the_speed = fractions.Fraction(the_speed)
      the_travel_path_name = row['travel path']
      the_presence = row['present']
      match the_presence:
        case "True":
          the_presence = True
        case "False":
          the_presence = False
      the_color = row['color']

      the_event = dict()
      the_event["time"] = the_time
      the_event["lane name"] = the_lane_name
      the_event["type"] = the_type
      the_event["name"] = the_name
      the_event["position"] = the_position
      the_event["length"] = the_length
      the_event["speed"] = the_speed
      the_event["travel path"] = the_travel_path_name
      the_event["present"] = the_presence
      the_event["color"] = the_color
      the_event["source"] = "script"
      
      events_list.append(the_event)

# Run the animation for one second after the last event
# unless the duraiton is specified.
if (duration_time == None):
  duration_time = latest_time - start_time + 1
end_time = start_time + duration_time

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
      # the end time of the flashing.
      if (lane_name in current_flashers):
        flasher = current_flashers[lane_name]
        if (the_color != flasher["color"]):
          flasher["stop time"] = event_time
          completed_flashers.append(flasher)
          del current_flashers[lane_name]
      if (do_trace):
        trace_file.write ("Time " + format_time(event_time) + " lane " +
                          lane_name + " color " + the_color + ".\n")
      if (the_color[0:8] == "Flashing"):
        if (do_trace):
          trace_file.write ("We have a flasher.\n")
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
                    ", liggt " + format_time(flash_light_time) + "\n")
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

if (do_trace):
  trace_file.write ("Events:\n")
  pprint.pprint (events, trace_file)
  trace_file.write ("\n")
  
background=cv2.imread("background.png")
canvas_size = background.shape[0:2]

# Subroutine to map ground locations and sizes to screen locations and sizes.
def map_ground_to_screen (x_feet, y_feet):
  global ground_height
  global background
  
  screen_height, screen_width = background.shape[:2]

  # The ground is the same shape as the screen, but is measured in feet.
  ground_width = ground_height * (screen_width / screen_height)
  
  ground_center_x = ground_width / 2
  ground_center_y = ground_height / 2
  screen_center_x = screen_width / 2
  screen_center_y = screen_height / 2
  x_from_center = x_feet - ground_center_x
  y_from_center = y_feet - ground_center_y
  x_from_center = x_from_center * (screen_width / ground_width)
  y_from_center = y_from_center * (screen_height / ground_height)
  x_pixels = x_from_center + screen_center_x
  y_pixels = y_from_center + screen_center_y

  return (int(x_pixels), int(y_pixels))

# Subroutine to map screen locations and sizes to ground locations and sizes.
def map_screen_to_ground (x_pixels, y_pixels):
  global ground_height
  global background
  
  screen_height, screen_width = background.shape[:2]
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
  
  return (x_feet, y_feet)


# Place a small image on a large image, removing what was below
# except for transparent areas.  The anchor point of the small image is placed
# at the indicated location on the large image.
def place_image(name, canvas, image_info, orientation, x_feet, y_feet):

  overlay_name, overlay_image, desired_width, desired_height = image_info

  if (do_trace):
    trace_file.write ("Placing image " + str(overlay_name) + " size (" +
                      format_position(desired_width) + ", " +
                      format_position(desired_height) + ") at (" +
                      format_position(x_feet) + ", " +
                      format_position(y_feet) + ").\n")

  # re-size the overlay image to the desired size in pixels
  original_height, original_width = overlay_image.shape[0:2]
  target_width, target_height = map_ground_to_screen (desired_width,
                                                      desired_height)
  small_image = cv2.resize(overlay_image, (int(target_width),
                                           int(target_height)),
                           interpolation=cv2.INTER_AREA)
  if (do_trace):
    trace_y_size = small_image.shape[0]
    trace_x_size = small_image.shape[1]
    trace_file.write (" reduced from (" + str(original_width) + ", " +
                      str(original_height) + ") to (" + str(trace_x_size) +
                      ", " + str(trace_y_size) + ").\n")
                    
  # Calculate the area in the large image that will be replaced.
  
  match orientation:
    case "center":
      anchor_x = int(target_width / 2)
      anchor_y = int(target_height / 2)
    case "up":
      anchor_x = int(target_width / 2)
      anchor_y = 0
    case "down":
      anchor_x = int(target_width / 2)
      anchor_y = target_height
    case "left":
      anchor_x = 0
      anchor_y = int(target_height / 2)
    case "right":
      anchor_x = int(target_width)
      anchor_y = int(target_height / 2)
    case _:
      anchor_x = int(target_width / 2)
      anchor_y = int(target_height / 2)

  x_position, y_position = map_ground_to_screen (x_feet, y_feet)
  
  x_min = x_position - anchor_x
  y_min = y_position - anchor_y
  x_max = x_min + target_width
  y_max = y_min + target_height

  if (do_trace):
    trace_file.write (" anchor at (" + str(x_position) + ", " +
                      str(y_position) + ").\n")
    trace_file.write (" extent (" + str(x_min) + ", " + str(y_min) + ") to (" +
                      str(x_max) + ", " + str(y_max) + ").\n")
    
  pixel_changed = False
  pixel_off_canvas = False
  canvas_height, canvas_width = canvas.shape[:2]

  # Replace the pixels in the area overlapped by the image being placed
  # by the pixels in the image being placed.  However, if there is
  # transparency in the image being placed, let the previous contents
  # show through.  This is imprecise because the pixel color values
  # are companded in sRGB, but it is close enough for our purposes,
  # and converting to linear to do the alpha blending properly would
  # be time-consuming.
  # The large image is assumed not to have an alpha channel.
  # Don't write any pixels that are off the canvas.
  
  for y in range(target_height):
    if (((y + y_min) >= 0) and ((y + y_min) < canvas_height)):
      for x in range(target_width):
        if (((x + x_min) >= 0) and ((x + x_min) < canvas_width)):
      
          # Elements 0 to 2 are the color channels
          overlay_blue = small_image[y, x, 0]
          overlay_green = small_image[y, x, 1]
          overlay_red = small_image[y, x, 2]

          # Element 3 is the alpha channel, 0 to 255, where 0 means transparent
          # and 255 means opaque.  Values inbetween are semi-transparent.
          # We convert the alpha value to the range 0 to 1.
          overlay_alpha = small_image[y, x, 3] / 255.0
          overlay_beta = 1.0 - overlay_alpha
      
          # Compute the desired color by combining the new color with
          # the old, taking into account the transparency.
          
          canvas_blue = canvas[y + y_min, x + x_min, 0]
          canvas_green = canvas[y + y_min, x + x_min, 1]
          canvas_red = canvas[y + y_min, x + x_min, 2]
          composite_blue = ((canvas_blue * overlay_beta) +
                            (overlay_blue * overlay_alpha))
          composite_green = ((canvas_green * overlay_beta) +
                             (overlay_green * overlay_alpha))

          composite_red = ((canvas_red * overlay_beta) +
                           (overlay_red * overlay_alpha))

          # Store the new color in the appropriate place in the canvas.
          canvas[y + y_min, x + x_min, 0] = composite_blue
          canvas[y + y_min, x + x_min, 1] = composite_green
          canvas[y + y_min, x + x_min, 2] = composite_red
          pixel_changed = True
        else:
          pixel_off_canvas = True
    else:
      pixel_off_canvas = True

  if (do_trace):
    if (pixel_changed):
      if (pixel_off_canvas):
        trace_file.write (" Image partly placed.\n")
      else:
        trace_file.write (" Image fully placed.\n")
    else:
      trace_file.write (" Image not placed.\n")
    
  return
  
# Subroutine to choose the correct stoplight image given its lane and color.
image_cache = dict()

def choose_lamp_image (lane, color):
  global image_cache

  if (color == "Dark"):
    match lane:
      case "A" | "E" | "H" :
        image_name = ("signal_Dark_4.png")
      case "B" | "C" | "D" | "F" | "G" | "J":
        image_name = ("signal_Dark_3.png")
      case "ps" | "pn":
        image_name = ("MUTCD_Ped_Signal_-_Steady_hand.png")
        
  match lane:
    case "A" | "E":
      root = "signal_llll"
      match color:
        case "Steady Left Arrow Red":
          image_name = (root + "_Red.png")
        case "Flashing Left Arrow Yellow (lower)":
          image_name = (root + "_Flashing_Yellow.png")
        case "Steady Left Arrow Green":
          image_name = (root + "_Green.png")
        case "Steady Left Arrow Yellow (upper)":
          image_name = (root + "_Yellow.png")     
        
    case "ps" | "pn":
      root = "MUTCD_Ped_Signal_-"
      match color:
        case "Don't Walk":
          image_name = (root + "_Steady_hand.png")
        case "Walk":
          image_name = (root + "_Walk.png")
        case "Walk with Countdown":
          image_name = (root + "_Hand_with_timer.png")
                         
    case "B" | "F":
      root = "signal_ccc"
      match color:
        case "Steady Circular Red":
          image_name = (root + "_Red.png")
        case "Steady Circular Yellow":
          image_name = (root + "_Yellow.png")
        case "Steady Circular Green":
          image_name = (root + "_Green.png")
        
    case "C" | "D" | "G" :
      root = "signal_ccc"
      match color:
        case "Steady Circular Red":
          image_name = (root + "_Red.png")
        case "Steady Circular Yellow":
          image_name = (root + "_Yellow.png")
        case "Steady Circular Green":
          image_name = (root + "_Green.png")

    case "H":
      root = "signal_cccl"
      match color:
        case "Steady Circular Red":
          image_name = (root + "_Red.png")
        case "Steady Left Arrow Green and Steady Circular Green":
          image_name = (root + "_Green.png")
        case "Steady Circular Yellow":
          image_name = (root + "_Yellow.png")

    case "J":
      root = "signal_rrr"
      match color:
        case "Steady Right Arrow Red":
          image_name = (root + "_Red.png")
        case "Steady Right Arrow Green":
          image_name = (root + "_Green.png")
        case "Steady Right Arrow Yellow":
          image_name = (root + "_Yellow.png")

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
  match lane:
    case "ps" | "pn":
      desired_width = lane_width
    case _:
      desired_width = lane_width / 3
      
  desired_height = desired_width * (image_height / image_width)
  return (image_path, image, desired_width, desired_height)
  
# SUbroutine to choose the image for a moving object.
def choose_moving_object_image (object_type, orientation, length):
  global image_cache
  
  match object_type:
   case "car":
     match orientation:
       case "right"| "left":
         image_name = "car-38800411-right.png"
       case "up" | "down" | "unknown":
         image_name = "car-38800411-up.png"
         
   case "truck":
     match orientation:
       case "right" | "left":
         image_name = "truck-51893967-right.png"
       case "up" | "down" | "unknown":
         image_name = "truck-51893967-up.png"
         
   case "pedestrian":
     image_name = "man_walking_right.png"

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

  match orientation:
    case "left":
      flipped_image = cv2.flip (image, 1)
    case "down":
      flipped_image = cv2.flip (image, 0)
    case _:
      flipped_image = image
        
  image_height, image_width = flipped_image.shape[0:2]
  match orientation:
    case "left" | "right":
      shrink_factor = length / image_width
    case "up" | "down":
      shrink_factor = length / image_height
    case "unknown":
      shrink_factor = fractions.Fraction (1, 30)
        
  return (image_path, flipped_image, image_width * shrink_factor,
          image_height * shrink_factor)


# Subroutine to find the starting location for a lane.  The traffic signal
# for this lane is placed at an offset from this location.
# This is the place where moving objects stop if they cannot
# enter the intersection and where moving objects leaving
# the intersection enter the lane.
def find_lane_position (lane):
  global canvas_size
  global lane_width
  
  center_y = canvas_size[0] / 2
  center_x = canvas_size[1] / 2

  center_x, center_y = map_screen_to_ground (center_x, center_y)
  
  match lane:
    case "1":
      return (center_x - (2.0 * lane_width), center_y + (4.0 * lane_width))
    case "2":
      return (center_x - (1.0 * lane_width), center_y + (4.0 * lane_width))
    case "A":
      return (center_x - (0.0 * lane_width), center_y + (4.0 * lane_width))
    case "B":
      return (center_x + (1.0 * lane_width), center_y + (4.0 * lane_width))
    case "C":
      return (center_x + (2.0 * lane_width), center_y + (4.0 * lane_width))
    case "3":
      return (center_x + (2.0 * lane_width), center_y + (0.5 * lane_width))
    case "D":
      return (center_x + (5.0 * lane_width), center_y - (0.5 * lane_width))
    case "4":
      return (center_x + (2.0 * lane_width), center_y - (4.0 * lane_width))
    case "5":
      return (center_x + (1.0 * lane_width), center_y - (4.0 * lane_width))
    case "E":
      return (center_x + (0.0 * lane_width), center_y - (4.0 * lane_width))
    case "F":
      return (center_x - (1.0 * lane_width), center_y - (4.0 * lane_width))
    case "G":
      return (center_x - (2.0 * lane_width), center_y - (4.0 * lane_width))
    case "6":
      return (center_x - (5.0 * lane_width), center_y - (1.0 * lane_width))
    case "H":
      return (center_x - (5.0 * lane_width), center_y + (0.0 * lane_width))
    case "J":
      return (center_x - (5.0 * lane_width), center_y + (1.5 * lane_width))
    case "ps":
      return (center_x + (4.0 * lane_width), center_y + (3.5 * lane_width))
    case "pn":
      return (center_x - (4.0 * lane_width), center_y - (3.5 * lane_width))
    
  return None
    
# Find the direction of a lane.
# Moving objects with a positive speed in this lane proceed
# in this direction to or from the lane's origin.
def find_lane_direction (lane):
  match lane:
    case "1" | "2" | "E" | "F" | "G":
      return (0, 1) # down
    case "3" | "H" | "J" | "ps":
      return (1, 0) # right
    case "A" | "B" | "C" | "4" | "5":
      return (0, -1) # up
    case "pn" | "D" | "6":
      return (-1, 0) # left
    
  return None

# Subroutine to find the offset of the traffic signal relative to the
# origin of the lane.
def find_signal_offset (lane):
  match lane:
    case "A" | "B" | "C":
      return (0, -lane_width * 2.0)
    case "D":
      return (-lane_width, -lane_width * 0.5)
    case "E" | "F" | "G":
      return (0, lane_width * 1.0)
    case "H" | "J":
      return (lane_width * 1.5, -lane_width * 0.5)
    case "pn":
      return (-lane_width, -lane_width * 0.5)
    case "ps":
      return (lane_width, -lane_width * 0.5)
    
  return None
  
# Create the lanes data structures which will record
# the changing state of the traffic control signal
# for that lane with the passage of time and hold
# information about the location and orientation
# of that lane.

lanes_dict = dict()
for lane_name in ("A", "ps", "B", "C", "D", "E", "pn", "F", "G", "H", "J"):
  lane = dict()
  lane["name"] = lane_name
  lane["color"] = "Dark"
  lane["position"] = find_lane_position(lane_name)
  lane["signal offset"] = find_signal_offset(lane_name)
  lane["direction"] = find_lane_direction(lane_name)
  lanes_dict[lane_name] = lane

  for lane_name in ("1", "2", "3", "4", "5", "6"):
    lane = dict()
    lane["name"] = lane_name
    lane["color"] = "Blank"
    lane["position"] = find_lane_position(lane_name)
    lane["direction"] = find_lane_direction(lane_name)
    lanes_dict[lane_name] = lane
    
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
        moving_object["position"] = event["position"]
        moving_object["time at position"] = event_time
        moving_object["length"] = event["length"]
        moving_object["present"] = False
        moving_object["travel path"] = event["travel path"]
        moving_object["lane name"] = event["lane name"]

if (do_trace):
  trace_file.write ("moving objects:\n")
  pprint.pprint(moving_objects_dict, trace_file)

# Subroutine to determine the present location of a moving object.
def find_moving_object_location (event_time, moving_object):
  global lanes_dict

  if (do_trace):
    trace_file.write ("Finding the location of moving object:\n")
    pprint.pprint (moving_object, trace_file)
    
  lane_name = moving_object["lane name"]
  travel_path = moving_object["travel path"]

  # If the moving object is in the intersection, it is moving
  # towards its destination lane.  If it is in the crosswalk
  # it is in its lane, either ps or pn.
  match lane_name:
    case "intersection":
      lane_name = travel_path[1]
    case "crosswalk":
      lane_name = travel_path
          
  lane = lanes_dict[lane_name]
  anchor_x, anchor_y = lane["position"]
  the_position = moving_object["position"]

  # Allow for the object's movement since it left this position.
  position_time = moving_object["time at position"]
  delta_time = event_time - position_time
  distance_moved = delta_time * moving_object["speed"]
  the_position = the_position + distance_moved
  
  direction_x, direction_y = lane["direction"]
  x = anchor_x + (direction_x * the_position)
  y = anchor_y + (direction_y * the_position)

  if (do_trace):
    trace_file.write ("found at " + format_position(x) + "," +
                      format_position(y) + ".\n")
    
  return (x, y)

# Subroutine to determine the orientation of a moving object.
def find_moving_object_orientation (moving_object):
  global lanes_dict
  lane_name = moving_object["lane name"]
  match lane_name:
    case "intersection":
      travel_path = moving_object["travel path"]
      lane_name = travel_path[1]
    case "crosswalk":
      return "unknown"
  
  lane = lanes_dict[lane_name]
  match lane["direction"]:
    case (1, 0):
      return "right"
    case (-1, 0):
      return "left"
    case (0, 1):
      return "down"
    case (0, -1):
      return "up"
    case _:
      return "unknown"
  return
  
# Update the states of the lamps and moving objeects,
# and generate the animation image frames.
frame_number = 0

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
        if (do_trace):
          trace_file.write ("Lamp: " + format_time(event_time) + " lane " +
                           lane_name + " color " + the_color + ".\n")
        
      case "car" | "truck" | "pedestrian":
        moving_object_name = event["name"]
        moving_object = moving_objects_dict[moving_object_name]
        moving_object["lane name"] = event["lane name"]
        moving_object["position"] = event["position"]
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
          
        if ((event_time >= start_time) and (event_time <= end_time)):
          if (do_trace):
            trace_file.write ("In time range.\n")
          the_time = event["time"]
          frame_number = frame_number + 1
          root_name = "frame_" + "{:06d}".format(frame_number) + ".png"
          file_path = pathlib.Path(animation_directory_name, root_name)
          canvas = background.copy()
          
          # Draw the signals in their current state.
          for lane_name in lanes_dict:
            lane = lanes_dict[lane_name]
            color = lane["color"]
            if (color != "Blank"):
              image_info = choose_lamp_image (lane_name, color)
              x_feet, y_feet = lane["position"]
              x_feet = x_feet + lane["signal offset"][0]
              y_feet = y_feet + lane["signal offset"][1]
              place_image (lane_name, canvas, image_info, "up",
                           x_feet, y_feet)
              
          # Draw the moving objects: pedestrians and vehicles.
          for moving_object_name in moving_objects_dict:
            moving_object = moving_objects_dict[moving_object_name]
            if (moving_object["present"]):
              type = moving_object["type"]
              name = moving_object["name"]
              x_feet, y_feet = find_moving_object_location (event_time,
                                                            moving_object)
              x_pixels, y_pixels = map_ground_to_screen (x_feet, y_feet)
              the_orientation = find_moving_object_orientation(moving_object)
              image_info = choose_moving_object_image (type, the_orientation,
                                                  moving_object["length"])
              place_image (name, canvas, image_info, the_orientation,
                           x_feet, y_feet)
              
          if (do_animation_output):
            if (do_trace):
              trace_file.write ("Writing frame " + str(file_path) + ".\n")
            cv2.imwrite (file_path, canvas)

if (do_trace):
  trace_file.write ("Image cache:\n")
  pprint.pprint (image_cache, trace_file)
  
if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file process_events.py
