#!/usr/bin/python3
# -*- coding: utf-8
#
# process_events.py renders the events output from the traffic signal
# simulator.

#   Copyright © 2024 by John Sauter <John_Sauter@systemeyescomputerstore.com>

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
  epilog=('Copyright © 2024 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='process_events 0.1 2024-12-31',
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
      the_lane_name = row['lane']
      the_type = row['type']
      the_position = row['position']
      if (the_position != ""):
        the_position = fractions.Fraction(the_position)
      the_speed = row['speed']
      if (the_speed != ""):
        the_speed = fractions.Fraction(the_speed)
      the_travel_path_name = row['travel path']
      the_color = row['color']

      the_event = dict()
      the_event["time"] = the_time
      the_event["lane name"] = the_lane_name
      the_event["type"] = the_type
      the_event["position"] = the_position
      the_event["speed"] = the_speed
      the_event["travel path"] = the_travel_path_name
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
  
background=cv2.imread("background.png", cv2.IMREAD_UNCHANGED)
canvas_size = background.shape[:2]

def place_image(canvas, overlay, x_position, y_position):
  overlay_height, overlay_width = overlay.shape[:2]
  region_of_interest = canvas[y_position:y_position + overlay_height,
                              x_position:x_position + overlay_width]

  overlay_gray = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
  _, mask = cv2.threshold(overlay_gray, 10, 255, cv2.THRESH_BINARY)
  mask_inv = cv2.bitwise_not(mask)
  
  background_bg = cv2.bitwise_and(region_of_interest,
                                  region_of_interest, mask=mask_inv)
  overlay_fg = cv2.bitwise_and(overlay, overlay, mask=mask)
  dst = cv2.add(background_bg, overlay_fg)
  canvas[y_position:y_position + overlay_height,
         x_position:x_position + overlay_width] = dst
  return

# Given a lane and a color, choose the correct stoplight image.
image_cache = dict()
def choose_lamp_image (lane, color):

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
  small_image = cv2.resize(image, (int(image_width/25),
                                   int(image_height/25)),
                           interpolation = cv2.INTER_AREA)
  image_cache[image_path] = small_image
  return (small_image)

# Find the location to display the signal for the given lane.
def find_lamp_position(lane):
  row_01 = 100
  row_02 = 700
  match lane:
    case "A":
      return (100, row_01)
    case "B":
      return (200, row_01)
    case "C":
      return (300, row_01)
    case "D":
      return (400, row_01)
    case "E":
      return (500, row_01)
    case "F":
      return (600, row_01)
    case "G":
      return (700, row_01)
    case "H":
      return (800, row_01)
    case "J":
      return (900, row_01)
    case "ps":
      return (500, row_02)
    case "pn":
      return (700, row_02)
  return
    
# Subroutine to format the clock for display.
def format_time(the_time):
  return (f'{the_time:07.3f}')

# Create the lamps data structures which will record
# the changing state of the traffic control signals
# with the passage of time.

lamps_dict = dict()
for lamp_name in ("A", "ps", "B", "C", "D", "E", "pn", "F", "G", "H", "J"):
  lamp = dict()
  lamp["name"] = lamp_name
  lamp["color"] = "Dark"
  lamp["position"] = find_lamp_position(lamp_name)
  lamps_dict[lamp_name] = lamp
  
# Generate the animation image frames.
frame_number = 0
event_times = sorted(events.keys())
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
        lane = event["lane name"]
        color = event["color"]
        lamp = lamps_dict[lane]
        lamp["color"] = color
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
          for lamp_name in lamps_dict:
            lamp = lamps_dict[lamp_name]
            color = lamp["color"]
            image = choose_lamp_image (lamp_name, color)
            x, y = lamp["position"]
            place_image (canvas, image, x, y)
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
