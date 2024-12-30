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
                     version='process_events 0.1 2024-12-30',
                     help='print the version number and exit')
parser.add_argument ('--animation-directory', metavar='animation_directory',
                     help='write animation output image files ' +
                     'into the specified directory')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--events-file', metavar='events_file',
                     help='read event output from the traffic simulator')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_animation_output = False
animation_directory_name = ""
do_events_input = False
events_file_name = ""
verbosity_level = 1
error_counter = 0

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_file_name = arguments ['trace_file']
  trace_file = open (trace_file_name, 'wt')

if (arguments ['animation_directory'] != None):
  do_animation_output = True
  animation_directory_name = arguments ['animation_directory']

if (arguments ['events_file'] != None):
  do_events_input = True
  events_file_name = arguments ['events_file']

start_time = decimal.Decimal("0.000")
current_time = fractions.Fraction(start_time)
  

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
  
canvas=cv2.imread("background.png", cv2.IMREAD_UNCHANGED)
canvas_size = canvas.shape[:2]

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

# Given a lane and a color, choose the correct stoplight image
def choose_image (lane, color):
  match lane:
    case "A" | "E":
      root = "signal_llll"
      match color:
        case "Steady Left Arrow Red":
          return (root + "_Red.png")
        case "Flashing Left Arrow Yellow (lower)":
          return (root + "_Flashing_Yellow.png")
        case "Steady Left Arrow Green":
          return (root + "_Green.png")
        case "Steady Left Arrow Yellow (upper)":
          return (root + "_Yellow.png")     
        
    case "ps" | "pn":
      root = "MUTCD_Ped_Signal_-"
      match color:
        case "Don't Walk":
          return (root + "_Steady_hand.png")
        case "Walk":
          return (root + "_Walk.png")
        case "Walk with Countdown":
          return (root + "_Hand_with_timer.png")
                         
    case "B" | "F":
      root = "signal_ccu"
      match color:
        case "Steady Circular Red":
          return (root + "_Red.png")
        case "Steady Circular Yellow":
          return (root + "_Yellow.png")
        case "Steady Up Arrow Green":
          return (root + "_Green.png")
        
    case "C" | "D" | "G" :
      root = "signal_ccc"
      match color:
        case "Steady Circular Red":
          return (root + "_Red.png")
        case "Steady Circular Yellow":
          return (root + "_Yellow.png")
        case "Steady Circular Green":
          return (root + "_Green.png")

    case "H":
      root = "signal_cccl"
      match color:
        case "Steady Circular Red":
          return (root + "_Red.png")
        case "Steady Left Arrow Green and Steady Circular Green":
          return (root + "_Green.png")
        case "Steady Circular Yellow":
          return (root + "_Yellow.png")

    case "J":
      root = "signal_rrr"
      match color:
        case "Steady Right Arrow Red":
          return (root + "_Red.png")
        case "Steady Right Arrow Green":
          return (root + "_Green.png")
        case "Steady Right Arrow Yellow":
          return (root + "_Yellow.png")

  return (None)

# Find the location to display the signal for the given lane
def find_position(lane):
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
    
# Format the clock for display
def format_time(the_time):
  return (f'{the_time:07.3f}')

frame_number = 0
event_times = sorted(events.keys())
for event_time in event_times:
  events_list = events[event_time]
  for event in events_list:
    type = event["type"]
    match type:
      case "lamp":
        lane = event["lane name"]
        color = event["color"]
        image_name = choose_image (lane, color)
        image = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)
        image_height, image_width = image.shape[:2]
        small_image = cv2.resize(image, (int(image_width/25),
                                         int(image_height/25)),
                                 interpolation = cv2.INTER_AREA)
        x, y = find_position(lane)
        place_image (canvas, small_image, x, y)
      case "frame":
        the_time = event["time"]
        frame_number = frame_number + 1
        root_name = "frame_" + "{:06d}".format(frame_number)
        full_file_name = animation_directory_name + root_name + ".png"
        if (do_animation_output):
          cv2.imwrite (full_file_name, canvas)
    
if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file traffic_control_signals.py
