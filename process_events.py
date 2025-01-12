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
                     version='process_events 0.11 2025-01-12',
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

shrink_factor = 30
ground_height = 143

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
  
if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

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
      
      events_list.append(the_event)

# Place markers in the timeline for where we will output a frame.
current_time = fractions.Fraction(1, 30)
end_time = fractions.Fraction(latest_time) + fractions.Fraction(1)
               
while (current_time <= end_time):
  if (current_time not in events):
    events[current_time] = list()
  events_list = events[current_time]
  event = dict()
  event["type"] = "frame"
  event["time"] = current_time
  events_list.append(event)
  
  current_time = current_time + fractions.Fraction(1, 30)

if (do_trace):
  trace_file.write ("Events:\n")
  pprint.pprint (events, trace_file)
  trace_file.write ("\n")
  
background=cv2.imread("background.png")
canvas_size = background.shape[0:2]

# Place a small image on a large image, removing what was below
# except for transparent areas.  The center of the small image is placed
# at the indicated location on the large image.
def place_image(name, canvas, overlay, x_position, y_position):

  overlay_height, overlay_width = overlay.shape[:2]

  if (do_trace):
    trace_file.write ("Placing image of " + name + " at (" +
                      str(x_position) + ":" +
                      str(x_position + overlay_width) +
                      "," +
                      str(y_position) + ":" +
                      str(y_position + overlay_height) +
                      "):\n")

  # Calculate the area in the large image that will be replaced
  # by the small image.
  x_center = x_position
  y_center = y_position
  x_size = overlay_width
  y_size = overlay_height
  x_min = x_center - int(x_size/2)
  y_min = y_center - int(y_size/2)
  x_max = x_min + x_size
  y_max = y_min + y_size
  
  # if the any part of the overlay is off the canvas, do nothing.
  canvas_height, canvas_width = canvas.shape[:2]
  if ((x_min < 0) or (x_max >= canvas_width)):
    
    if (do_trace):
      trace_file.write ("Image not placed: x out of range.\n")
      pprint.pprint ((canvas, overlay, x_position, y_position), trace_file)
      
    return
  if ((y_min < 0) or (y_max >= canvas_height)):

    if (do_trace):
      trace_file.write ("Image not placed: y out of range.\n")
      pprint.pprint ((canvas, overlay, x_position, y_position), trace_file)
    return

  # Replace the pixels in the area overlapped by the image being placed
  # by the pixels in the image being placed.  However, if there is
  # transparency in the image being placed, let the previous contents
  # show through.  This is imprecise because the pixel color values
  # are companded in sRGB, but it is close enough for our purposes,
  # and converting to linear to do the alpha blending properly would
  # be time-consuming.
  # The large image is assumed not to have an alpha channel.
  for y in range(y_size):
    for x in range(x_size):
      
      # Elements 0 to 2 are the color channels
      overlay_color = overlay[y, x, 0:3]

      # Element 3 is the alpha channel, 0 to 255, where 0 means transparent
      # and 255 means opaque.  Values inbetween are semi-transparent.
      # We convert the alpha value to the range 0 to 1.
      overlay_alpha = overlay[y, x, 3] / 255

      # Get the color from the corresponding pixel in the canvas.
      canvas_color = canvas[y + y_min, x + x_min]

      # Compute the desired color by combining the new image with
      # the old, taking into account the transparency.
      composite_color = (canvas_color * (1.0 - overlay_alpha) +
                         (overlay_color * overlay_alpha))

      # Store the new color in the appropriate place in the canvas.
      canvas[y + y_min, x + x_min] = composite_color
      
  if (do_trace):
    trace_file.write ("Image placed.\n")
    
  return
  
# Given a lane and a color, choose the correct stoplight image.
image_cache = dict()
def choose_lamp_image (lane, color, shrink_factor):
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
      root = "signal_ccu"
      match color:
        case "Steady Circular Red":
          image_name = (root + "_Red.png")
        case "Steady Circular Yellow":
          image_name = (root + "_Yellow.png")
        case "Steady Up Arrow Green":
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
    return image_cache[image_path]

  image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
  image_height, image_width = image.shape[:2]
  small_image = cv2.resize(image, (int(image_width/shrink_factor),
                                   int(image_height/shrink_factor)),
                           interpolation = cv2.INTER_AREA)
  image_cache[image_path] = small_image
  return (small_image)

# Given a type, choose the image for a moving object.
def choose_moving_object_image (object_type, shrink_factor):
  global image_cache
  
  match object_type:
   case "car":
     image_name = "car-2897.png"
   case "truck":
     image_name = "truck-1058.png"
   case "pedestrian":
     image_name = "man_walking_right.png"

  image_path = pathlib.Path(image_name)

  if (image_path in image_cache):
    return image_cache[image_path]

  image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
  image_height, image_width = image.shape[:2]
  small_image = cv2.resize(image, (int(image_width/shrink_factor),
                                   int(image_height/shrink_factor)),
                           interpolation = cv2.INTER_AREA)
  image_cache[image_path] = small_image
  return (small_image)

# Map ground locations to screen locations
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

  return (x_pixels, y_pixels)

# map screen locations to ground locations.
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

# Find the starting location for a lane.  The traffic signal
# for this lane is placed here.
def find_lane_position (lane):
  global canvas_size
  
  center_y = canvas_size[0] / 2
  center_x = canvas_size[1] / 2

  center_x, center_y = map_screen_to_ground (center_x, center_y)
  
  lane_width = 12

  match lane:
    case "1":
      return (center_x - (2.0 * lane_width), center_y + (2.5 * lane_width))
    case "2":
      return (center_x - (1.0 * lane_width), center_y + (2.5 * lane_width))
    case "A":
      return (center_x - (0.0 * lane_width), center_y + (2.5 * lane_width))
    case "B":
      return (center_x + (1.0 * lane_width), center_y + (2.5 * lane_width))
    case "C":
      return (center_x + (2.0 * lane_width), center_y + (2.5 * lane_width))
    case "3":
      return (center_x + (3.5 * lane_width), center_y - (2.0 * lane_width))
    case "D":
      return (center_x + (3.5 * lane_width), center_y - (0.5 * lane_width))
    case "4":
      return (center_x + (2.0 * lane_width), center_y - (2.5 * lane_width))
    case "5":
      return (center_x + (1.0 * lane_width), center_y - (2.5 * lane_width))
    case "E":
      return (center_x + (0.0 * lane_width), center_y - (2.5 * lane_width))
    case "F":
      return (center_x - (1.0 * lane_width), center_y - (2.5 * lane_width))
    case "G":
      return (center_x - (2.0 * lane_width), center_y - (2.5 * lane_width))
    case "6":
      return (center_x - (3.5 * lane_width), center_y - (1.0 * lane_width))
    case "H":
      return (center_x - (3.5 * lane_width), center_y + (0.0 * lane_width))
    case "J":
      return (center_x - (3.5 * lane_width), center_y + (1.5 * lane_width))
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
    
# Subroutine to format the clock for display.
def format_time(the_time):
  return (f'{the_time:07.3f}')

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

# Determine the present location of a moving object.
def find_moving_object_location (event_time, moving_object):
  global lanes_dict

  if (do_trace):
    trace_file.write ("Finding the location of:\n")
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
    trace_file.write ("found at " + str(x) + "," + str(y) + ".\n")
    
  return (x, y)
  
# Update the states of the lamps and moving objeects,
# and generate the animation image frames.
frame_number = 0
if (duration_time == None):
  duration_time = latest_time - start_time

if (do_trace):
  trace_file.write ("Start: " + format_time(start_time) +
                    " duration: " + format_time(duration_time) + ".\n")

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
          
        if ((event_time > start_time) and
            (event_time <= (start_time + duration_time))):
          if (do_trace):
            trace_file.write ("In time range.\n")
          the_time = event["time"]
          frame_number = frame_number + 1
          root_name = "frame_" + "{:06d}".format(frame_number) + ".png"
          file_path = pathlib.Path(animation_directory_name, root_name)
          canvas = background.copy()
          for lane_name in lanes_dict:
            lane = lanes_dict[lane_name]
            color = lane["color"]
            if (color != "Blank"):
              image = choose_lamp_image (lane_name, color, shrink_factor)
              x_feet, y_feet = lane["position"]
              x_pixels, y_pixels = map_ground_to_screen (x_feet, y_feet)
              place_image (lane_name, canvas, image, int(x_pixels),
                           int(y_pixels))
          for moving_object_name in moving_objects_dict:
            moving_object = moving_objects_dict[moving_object_name]
            if (moving_object["present"]):
              type = moving_object["type"]
              name = moving_object["name"]
              x_feet, y_feet = find_moving_object_location (event_time,
                                                            moving_object)
              x_pixels, y_pixels = map_ground_to_screen (x_feet, y_feet)
              image = choose_moving_object_image (type, shrink_factor)
              place_image (name, canvas, image, int(x_pixels), int(y_pixels))
              
          if (do_animation_output):
            if (do_trace):
              trace_file.write ("writing frame " + str(file_path) + ".\n")
            cv2.imwrite (file_path, canvas)

if (do_trace):
  trace_file.write ("Image cache:\n")
  pprint.pprint (image_cache, trace_file)
  
if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file process_events.py
