#!/usr/bin/python3
# -*- coding: utf-8
#
# define_four_corners.py defines a simple intersection for the
# traffic simulator.

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

import math
import pprint
import fractions
import pathlib
import json
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Define a simple traffic intersection.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='define_four_corners 0.65 2025-12-24',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--input-file', metavar='input_file',
                     help='read the toggle and times names from the ' +
                     'specified file as JSON')
parser.add_argument ('--output-file', metavar='output_file',
                     help='write intersection to the specified file as JSON')
parser.add_argument ('--waiting-limit', type=int, metavar='waiting_limit',
                     help='max wait time before getting green preference ' +
                     'for turning green; default 60 seconds.')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_input = False
input_file_name = ""
do_output = False
output_file_name = ""
waiting_limit = 60
verbosity_level = 1
error_counter = 0

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_file_name = arguments ['trace_file']
  trace_file_name = pathlib.Path(trace_file_name)
  trace_file = open (trace_file_name, 'w')

if (arguments ['input_file'] != None):
  do_input = True
  input_file_name = arguments ['input_file']
  input_file_name = pathlib.Path(input_file_name)

if (arguments ['output_file'] != None):
  do_output = True
  output_file_name = arguments ['output_file']
  output_file_name = pathlib.Path(output_file_name)

if (arguments ['waiting_limit'] != None):
  waiting_limit = arguments ['waiting_limit']

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

# The conversion factor from miles per hour to feet per second:
mph_to_fps = fractions.Fraction(5280, 60*60)

# Read the finite state machine to get the timer and toggle names.

if (do_input):
    input_file = open (input_file_name, 'r')
    finite_state_machine = json.load (input_file)
    input_file.close()
    toggle_names = finite_state_machine["toggles"]
    timer_names = finite_state_machine["timer names"]
else:
    finite_state_machine = dict()
    toggle_names = list()
    timer_names = list()
    
# Build the finite state machines for the signal faces:

signal_face_names = ( "A", "B", "C", "D" )

# Set the duration of each timer in each signal face.

timer_durations = dict()

for signal_face_name in ("A", "B", "C", "D"):
  timer_full_name = signal_face_name + "/" + "Red Limit"
  timer_durations[timer_full_name] = ("inf",)
  timer_full_name = signal_face_name + "/" + "Maximum Green"
  timer_durations[timer_full_name] = ("30.000",)
  timer_full_name = signal_face_name + "/" + "Minimum Green"
  timer_durations[timer_full_name] = ("12.000",)
  timer_full_name = signal_face_name + "/" + "Passage"
  timer_durations[timer_full_name] = ("3.500", ("1.000", "Maximum Green",
                                                "20.000", "15.000"))
  timer_full_name = signal_face_name + "/" + "Red Clearance"
  timer_durations[timer_full_name] = ("1.000",)
  timer_full_name = signal_face_name + "/" + "Green Limit"
  timer_durations[timer_full_name] = ("60.000",)
  timer_full_name = signal_face_name + "/" + "Yellow Change"
  timer_durations[timer_full_name] = ("5.000",)
  timer_full_name = signal_face_name + "/" + "Green Delay Approaching"
  timer_durations[timer_full_name] = ("0.000",)
  timer_full_name = signal_face_name + "/" + "Green Delay Present"
  timer_durations[timer_full_name] = ("0.000",)
  timer_full_name = signal_face_name + "/" + "Left Flashing Yellow Waiting"
  timer_durations[timer_full_name] = ("inf",)
  timer_full_name = signal_face_name + "/" + "Left Flashing Yellow Limit"
  timer_durations[timer_full_name] = ("inf",)
  timer_full_name = signal_face_name + "/" + "Minimum Left Flashing Yellow"
  timer_durations[timer_full_name] = ("inf",)

signal_faces_list = list()
signal_faces_dict = dict()

for signal_face_name in signal_face_names:
  signal_face = dict()
  signal_face["name"] = signal_face_name

  toggles_list = list()
  for toggle_name in toggle_names:
    toggle = dict()
    toggle["name"] = toggle_name
    toggle["value"] = False

    match toggle_name:
      case "Traffic Approaching" | "Request Green" | \
           "Green Request Granted" | "Request Partial Clearance" | \
           "Clearance Requested" | "Cleared" | \
           "Conflicting Paths are Clear" | "Traffic Flowing" \
           "Preempt Green" | "Preempt Red":
        important = True

      case _:
        important = False

    toggle["important"] = important
           
    toggles_list.append(toggle)
    
  signal_face["toggles"] = toggles_list

  timers_list = list()
  for timer_name in timer_names:
    timer = dict()
    timer["name"] = timer_name
    timer["state"] = "off"
    timer["signal face name"] = signal_face_name
    timer_full_name = signal_face_name + "/" + timer_name
    timer["duration"] = timer_durations[timer_full_name]
    
    match timer_name:
      case "Red Clearance" | "Yellow Change" | "Minimum Green" | \
           "Passage" | "Maximum Green" | \
           "Green Limit" | "Red Limit" | \
           "Green Delay Approaching" | "Green Delay Present":
        important = True
        
      case _:
        important = False

    timer["important"] = important
    
    timers_list.append(timer)
    
  signal_face["timers"] = timers_list

  signal_faces_list.append(signal_face)
  signal_faces_dict[signal_face_name] = signal_face

if (do_trace):
  trace_file.write ("Timer durations:\n")
  pprint.pprint (timer_durations, trace_file)
  trace_file.write ("\n")
  
# Construct the conflict and partial conflict tables.
  
for signal_face in signal_faces_list:
  partial_conflict_set = None
  
  match signal_face["name"]:
    case "A" | "C":
      conflict_set = ("B", "D")
    case "B" | "D":
      conflict_set = ("A", "C")
      
  if (partial_conflict_set == None):
    partial_conflict_set = conflict_set
  signal_face["conflicts"] = conflict_set
  signal_face["partial conflicts"] = partial_conflict_set

# Limit the time a signal face stays red while it is waiting to
# turn green.  This is a tradeoff between throughput and maximum
# waiting time for a vehicle or pedestrian.

for signal_face in signal_faces_list:
  match signal_face["name"]:
    case "A" | "B" | "C" | "D":
      signal_face["waiting limit"] = waiting_limit

# Construct the travel paths.  A traffic element appears at the first
# milestone, then proceeds to each following milestone.  When it reaches
# the last milestone it vanishes from the simulation.
car_length = 15
car_width = 5
truck_length = 40
truck_width = 8
approach_sensor_long_distance = 150
long_lane_length = 528
lane_width = 12
crosswalk_width = 6

# Subroutine to find the top and bottom of a lane.
# The top is the place where traffic elements stop if they cannot
# enter the intersection from their entrance lane and where traffic elements
# leaving the intersection enter their exit lane.
# The bottom is the other end of the lane, where vehicles enter or leave
# the simulation.

lane_names = ("A", "B", "C", "D", "1", "2", "3", "4")

def find_lane_info (lane_name):
  global lane_width
  global long_lane_length
  
  center_y = 0
  center_x = 0

  match lane_name:
    case "1":
      top_x = center_x - (0.5 * lane_width)
      top_y = center_y + (1.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + long_lane_length
      
    case "A":
      top_x = center_x + (0.5 * lane_width)
      top_y = center_y + (1.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + long_lane_length
            
    case "2":
      top_x = center_x + (1.0 * lane_width)
      top_y = center_y + (0.5 * lane_width)
      bottom_x = top_x + long_lane_length
      bottom_y = top_y
      
    case "B":
      top_x = center_x + (1.0 * lane_width)
      top_y = center_y - (0.5 * lane_width)
      bottom_x = top_x + long_lane_length
      bottom_y = top_y
      
    case "3":
      top_x = center_x + (0.5 * lane_width)
      top_y = center_y - (1.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - long_lane_length
            
    case "C":
      top_x = center_x - (0.5 * lane_width)
      top_y = center_y - (1.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - long_lane_length
            
    case "4":
      top_x = center_x - (1.0 * lane_width)
      top_y = center_y - (0.5 * lane_width)
      bottom_x = top_x - long_lane_length
      bottom_y = top_y
            
    case "D":
      top_x = center_x - (1.0 * lane_width)
      top_y = center_y + (0.5 * lane_width)
      bottom_x = top_x - long_lane_length
      bottom_y = top_y
      
    case _:
      top_x = None
      top_y = None
      bottom_x = None
      bottom_y = None
    
  return (top_x, top_y, bottom_x, bottom_y)

# Construct the travel paths.  Each valid path through the intersection
# has an entry lane and an exit lane.  It also has milestones which
# the traffic elements pass through on their way from the entrance to the exit.
# Some travel paths have a shape which must be empty of vehicles before
# a permissive turn can be taken.

# Construct the shape of the intersection.
max_x = None
max_y = None
min_x = None
min_y = None

for lane_name in lane_names:
  intersection_x, intersection_y, *bottom  = find_lane_info (lane_name)

  if (max_x == None):
    max_x = intersection_x
  if (intersection_x > max_x):
    max_x = intersection_x
  if (min_x == None):
    min_x = intersection_x
  if (intersection_x < min_x):
    min_x = intersection_x
  if (max_y == None):
    max_y = intersection_y
  if (intersection_y > max_y):
    max_y = intersection_y
  if (min_y == None):
    min_y = intersection_y
  if (intersection_y < min_y):
    min_y = intersection_y

intersection_shape = (min_x, min_y, max_x, max_y)
if (do_trace):
  trace_file.write ("Intersection shape:\n")
  pprint.pprint ((min_x, min_y, max_x, max_y), trace_file)
  pprint.pprint (intersection_shape, trace_file)
  
travel_paths = dict()

for entry_lane_name in ("A", "B", "C", "D"):
  
  entry_lane_info = find_lane_info(entry_lane_name)
  entry_start_x = entry_lane_info[2]
  entry_start_y = entry_lane_info[3]
  entry_intersection_x = entry_lane_info[0]
  entry_intersection_y = entry_lane_info[1]
  
  for exit_lane_name in ("1", "2", "3", "4"):

    exit_lane_info = find_lane_info(exit_lane_name)
    exit_intersection_x = exit_lane_info[0]
    exit_intersection_y = exit_lane_info[1]
    exit_end_x = exit_lane_info[2]
    exit_end_y = exit_lane_info[3]
    
    travel_path_name = entry_lane_name + exit_lane_name
    travel_path = dict()
    travel_path["name"] = travel_path_name
    travel_path["entry lane name"] = entry_lane_name
    travel_path["exit lane name"] = exit_lane_name

    permissive_turn_info = None
    permissive_colors = None
    green_colors = None
    permissive_distance = 250
    travel_path_valid = False

    match travel_path_name:
      
      case "A1":
        # Northbound U turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y - car_length) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          exit_intersection_x - (0.5 * lane_width),
          exit_intersection_y - (3 * lane_width) - permissive_distance,
          exit_intersection_x + (0.5 * lane_width),
          exit_intersection_y)

        permissive_turn_info = (("moving South", intersection_shape),
                                ("present", permissive_turn_shape))
        
        permissive_colors = ("Steady Circular Green",)
        green_colors = tuple()
        
      case "C2":
        # Southbound left turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          entry_intersection_x - permissive_distance,
          exit_intersection_y - (0.5 * lane_width),
          exit_intersection_x,
          exit_intersection_y + (0.5 * lane_width))

        permissive_turn_info = (("moving North", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green",)
        green_colors = tuple()
        
      case "C3":
        # Southbound U turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y + car_length) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          entry_intersection_x + (0.5 * lane_width), entry_intersection_y,
          entry_intersection_x + (2.5 * lane_width),
          entry_intersection_y + (3.0 * lane_width) + permissive_distance)

        permissive_turn_info = (("moving North", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green",)
        green_colors = tuple()
                        
      case "A3" | "B4" | "C1" | "D2":
        # Through lanes
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        green_colors = ("Steady Circular Green,")
        
      case "A2":
        # Northbound right turn
        travel_path_valid = True
        
        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          entry_intersection_x - permissive_distance,
          exit_intersection_y - (0.5 * lane_width),
          exit_intersection_x,
          exit_intersection_y + (0.5 * lane_width))
                                                       
        permissive_turn_info = (("moving East", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Red", "Steady Circular Yellow")
        green_colors = ("Steady Circular Green,")
        
      case "A4":
        # Northbound left turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          exit_intersection_x,
          exit_intersection_y - permissive_distance,
          entry_intersection_x,
          entry_intersection_y)
                                                       
        permissive_turn_info = (("moving South", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green",)
        green_colors = tuple()
        
      case "C4":
        # Soundbound right turn
        travel_path_valid = True
        
        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          exit_intersection_x,
          entry_intersection_y,
          exit_intersection_x - permissive_distance,
          exit_intersection_y + (0.5 * lane_width))
                                                       
        permissive_turn_info = (("moving West", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Red", "Steady Circular Yellow")
        green_colors = ("Steady Circular Green,")
        
      case "B1":
        # Westbound left turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_turn_shape = (
          exit_intersection_x - permissive_distance,
          exit_intersection_y - (0.5 * lane_width),
          exit_intersection_x,
          exit_intersection_y + (0.5 * lane_width))
                                                       
        permissive_turn_info = (("moving South", intersection_shape),
                                 ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green,")
        green_colors = tuple()
        
      case "B2":
        # Westbound U turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x -
                            car_length) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
        
        permissive_turn_shape = (
          exit_intersection_x - permissive_distance,
          entry_intersection_y - (0.5 * lane_width),
          exit_intersection_x,
          exit_intersection_y + (0.5 * lane_width))
                                                       
        permissive_turn_info = (("moving East", intersection_shape),
                                 ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green,")
        green_colors = tuple()
        
      case "B3":
        # Westbound right turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
        
        permissive_turn_shape = (
          exit_intersection_x - (0.5 * lane_width),
          exit_intersection_y,
          exit_intersection_x + (0.5 * lane_width),
          entry_intersection_y + permissive_distance)
                                                       
        permissive_turn_info = (("moving North", intersection_shape),
                                 ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Red", "Steady Circular Yellow")
        green_colors = ("Steady Circular Green,")
        
      case "D1":
        # Eastbound right turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
        
        permissive_turn_shape = (
          exit_intersection_x - (0.5 * lane_width),
          entry_intersection_y,
          exit_intersection_x + (0.5 * lane_width),
          entry_intersection_y - permissive_distance)
                                                       
        permissive_turn_info = (("moving South", intersection_shape),
                                 ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Red", "Steady Circular Yellow")
        green_colors = ("Steady Circular Green,")
                
      case "D4":
        # Eastbound U turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x +
                            car_length) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
                
        permissive_turn_shape = (
          exit_intersection_x,
          exit_intersection_y - (0.5 * lane_width),
          exit_intersection_x + permissive_distance,
          entry_intersection_y + (0.5 * lane_width))
                                                       
        permissive_turn_info = (("moving West", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green,")
        green_colors = tuple()

      case "D3":
        # Eastbound left turn
        travel_path_valid = True

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", (entry_intersection_x + exit_intersection_x) / 2.0,
           (entry_intersection_y + exit_intersection_y) / 2.0),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
                
        permissive_turn_shape = (
          exit_intersection_x - (0.5 * lane_width),
          exit_intersection_y - permissive_distance,
          exit_intersection_x + (0.5 * lane_width),
          exit_intersection_y)
                                                       
        permissive_turn_info = (("moving South", intersection_shape),
                                ("present", permissive_turn_shape))
        permissive_colors = ("Steady Circular Green,")
        green_colors = tuple()
        
      case _:
        milestones = None

    travel_path["milestones"] = milestones
    travel_path["permissive turn info"] = permissive_turn_info
    travel_path["permissive colors"] = permissive_colors
    travel_path["green colors"] = green_colors

    if (travel_path_valid):
      travel_paths[travel_path_name] = travel_path
  
if (do_trace):
  trace_file.write ("Travel paths:\n")
  pprint.pprint (travel_paths, trace_file)

# Set up the mapping from the lamp names specified in the finite state
# machines and the lamps actually used.  Each signal face dictionary
# has an entry called lamp names map which consists of a dictionary.
# the keys to this dictionary are the names used in the finite
# state machine and the corresponding values are the names
# of the lamps on the street.

for signal_face in signal_faces_list:
  lamp_names_map = dict()
  
  match signal_face["name"]:
    case "A" | "B" | "C" | "D":
      lamp_names_map["Steady Circular Red"] = "Steady Circular Red"
      lamp_names_map["Steady Circular Yellow"] = "Steady Circular Yellow"
      lamp_names_map["Steady Circular Green"] = "Steady Circular Green"
      lamp_names_map["Flashing Circular Red"] = "Flashing Circular Red"
      lamp_names_map["Flashing Circular Yellow"] = "Flashing Circular Yellow"

  signal_face["lamp names map"] = lamp_names_map
  signal_face["iluminated lamp name"] = ""
  
# Set up the mapping from the vehicle sensors to the toggles they set.

# Signal_face["sensors"] is a dictionary whose indexes are sensor names.
# The value of each entry is a sensor, which is a dictionary.
# Toggles is a tuple of toggle names.  If a toggle name contains a slash
# it refers to a different signal face.

# Specify which toggles are set by which sensors.
for signal_face in signal_faces_list:

  sensor_map = dict()

  # Default mapping of traffic sensors
  sensor_map["Traffic Approaching"] = ("Traffic Approaching",)
  sensor_map["Traffic Present"] = ("Traffic Present",)

  # Non-default mapping of traffic sensors
  match signal_face["name"]:
    case "A":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "C/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "C/Traffic Present")
      
    case "B":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "D/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "D/Traffic Present")
      
    case "C":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "A/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "A/Traffic Present")
      
    case "D":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "D/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "D/Traffic Present")

  # Flash command
  match signal_face["name"]:
      
    case "A" | "B" | "C" | "D":
      sensor_map["Flash"] = ("Flash Red",)

  # Preempt command
  sensor_map["Preempt"] = ("Preempt Red",)

  # Preempt command with the direction the emergency vehicle is approaching
  # from.
  match signal_face["name"]:
    case "D":
      sensor_map["Preempt from West"] = ("Preempt Green",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Red",)

    case "A":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Green",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Red",)

    case "B":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Green",)
      sensor_map["Preempt from North"] = ("Preempt Red",)

    case "C":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Green",)

  # Manual command
  sensor_map["Manual Red"] = ("Manual Red",)
  sensor_map["Manual Green"] = ("Manual Green",)

  # Now construct the sensors for this signal face.
  sensors = dict()
  for sensor_name in sensor_map:
    sensor = dict()
    sensor["name"] = sensor_name
    sensor["toggles"] = sensor_map[sensor_name]
    sensor["controlled by script"] = False
    sensor["lane name"] = signal_face["name"]

    # for the Traffic Approaching and Traffic Present sensors,
    # the size and placement varies between lanes.  These
    # sensors are activated by vehicles.
    lane_info = find_lane_info(signal_face["name"])

    # The vehicle sensors have this size.
    sensor_length = 6
    sensor_width = 10
    
    match sensor_name:
      case "Traffic Approaching":
        match signal_face["name"]:
          
          case "A":
            sensor_offset = approach_sensor_long_distance
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] + sensor_offset
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] + sensor_offset + sensor_length
            
          case "B":
            sensor_offset = approach_sensor_long_distance
            sensor["x min"] = lane_info[0] + sensor_offset
            sensor["y min"] = lane_info[1] - (sensor_width / 2.0)
            sensor["x max"] = lane_info[0] + (sensor_offset + sensor_length)
            sensor["y max"] = lane_info[1] + (sensor_width / 2.0)
            
          case "C":
            sensor_offset = approach_sensor_long_distance
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] - sensor_offset - sensor_length
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] - sensor_offset
            
          case "D":
            sensor_offset = approach_sensor_long_distance
            sensor["x min"] = lane_info[0] - (sensor_offset + sensor_length)
            sensor["y min"] = lane_info[1] - (sensor_width / 2.0)
            sensor["x max"] = lane_info[0] - sensor_offset
            sensor["y max"] = lane_info[1] + (sensor_width / 2.0)
            
      case "Traffic Present":
        sensor_offset = 1
        match signal_face["name"]:

          case "A":
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] + sensor_offset
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] + (sensor_offset + sensor_length)
            
          case "B":
            sensor["x min"] = lane_info[0] + sensor_offset
            sensor["y min"] = lane_info[1] - (sensor_width / 2.0)
            sensor["x max"] = lane_info[0] + (sensor_offset + sensor_length)
            sensor["y max"] = lane_info[1] + (sensor_width / 2.0)

          case "C":
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] - (sensor_offset + sensor_length)
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] - sensor_offset

          case "D":
            sensor["x min"] = lane_info[0] - (sensor_offset + sensor_length)
            sensor["y min"] = lane_info[1] - (sensor_width / 2.0)
            sensor["x max"] = lane_info[0] - sensor_offset
            sensor["y max"] = lane_info[1] + (sensor_width / 2.0)

    if ("x min" in sensor):
      sensor_shape = (sensor["x min"], sensor["y min"],
                      sensor["x max"], sensor["y max"])
      sensor["shape"] = sensor_shape
    
    sensor["value"] = False

    match sensor_name:
      case "Traffic Present" | "Traffic Approaching" | \
           "Preempt" | "Preempt from West" | "Preempt from South" | \
           "Preempt from East" | "Preempt from North":
        important = True

      case _:
        important = False

    sensor["important"] = important
    
    sensors [sensor_name] = sensor
    
  signal_face ["sensors"] = sensors

# Record the offsets of the signal faces relative to the top of the lane.

def find_signal_face_offset (signal_face_name):
  match signal_face_name:
    case "A":
      return ((1.0 * lane_width), (0.5 * lane_width))
    case "B":
      return (0.5 * lane_width, -(1.5 * lane_width))
    case "C":
      return (-(1.0 * lane_width), - (1.5 * lane_width))
    case "D":
      return (-(0.5 * lane_width), (0.5 * lane_width))
    
  return None

for signal_face in signal_faces_list:
  signal_face_name = signal_face ["name"]
  offset_x, offset_y = find_signal_face_offset (signal_face_name)
  signal_face ["offset x"] = offset_x
  signal_face ["offset y"] = offset_y  

# Specify the speed limit in feet per second based on where the
# traffic element is.
intersection_speed_limit = 25 * mph_to_fps
def compute_speed_limit (lane_name, travel_path_name):
  match lane_name:
    case "1" | "A" | "2" | "B" | "3" | "C" | "4" | "D":
      return (35 * mph_to_fps)
    case "intersection":
      # If a vehicle is passing through the intersection without
      # having stopped, it need not slow down.
      entering_lane_name = travel_path_name[0]
      exiting_lane_name = travel_path_name[1]
      entering_speed = compute_speed_limit (entering_lane_name,
                                            travel_path_name)
      exiting_speed = compute_speed_limit (exiting_lane_name, travel_path_name)
      return (min(entering_speed, exiting_speed))
    
  return None

speed_limits = dict()
for travel_path_name in travel_paths:
  travel_path = travel_paths [travel_path_name]
  milestones = travel_path ["milestones"]
  for milestone in milestones:
    lane_name = milestone[0]
    speed_limit = compute_speed_limit (lane_name, travel_path_name)
    speed_limit_ident = travel_path_name + " / " + lane_name
    speed_limits [speed_limit_ident] = float(speed_limit)
        
if (do_trace):
  trace_file.write ("Starting Signal Faces:\n")
  pprint.pprint (signal_faces_list, trace_file)

# Gather the information about the intersection, including
# the finite state machine template for the signal faces
# to keep everything in a single file.
intersection_info = dict()
intersection_info["finite state machine"] = finite_state_machine
intersection_info["signal faces"] = signal_faces_list
intersection_info["travel paths"] = travel_paths
intersection_info["car length"] = car_length
intersection_info["car width"] = car_width
intersection_info["truck length"] = truck_length
intersection_info["truck width"] = truck_width
intersection_info["lane width"] = lane_width
intersection_info["crosswalk width"] = crosswalk_width
intersection_info["speed limits"] = speed_limits
intersection_info["intersection speed limit"] = float(intersection_speed_limit)

# In addition to information about the signal faces, we need information
# about each lane to draw the background image and the signal face images.

lanes_info = dict()
for lane_name in lane_names:
  top_x, top_y, bottom_x, bottom_y = find_lane_info (lane_name)
  lane_info = dict()
  lane_info ["name"] = lane_name
  lane_info ["top x"] = top_x
  lane_info ["top y"] = top_y
  lane_info ["bottom y"] = bottom_y
  lane_info ["bottom x"] = bottom_x
  lane_info ["width"] = lane_width

  match lane_name:
    case "A" | "B" | "C" | "D":
      lane_info["root signal face image"] = "signal_ccc"
      
  lanes_info [lane_name] = lane_info

intersection_info ["lanes info"] = lanes_info

# Output the information about the intersection for the simulator.
if (do_output):
    output_file = open (output_file_name, 'w')
    json.dump (intersection_info, output_file, indent = " ")
    output_file.close()
  
if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file define_four_corners.py
