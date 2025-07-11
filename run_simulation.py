#!/usr/bin/python3
# -*- coding: utf-8
#
# run_simulation.py simulates an intersection controlled by a traffic signal.

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
import decimal
import fractions
import pathlib
import json
import csv
import shapely
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Simulate an intersection controlled by a traffic signal.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='traffic_control_signals 0.39 2025-07-06',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--input-file', metavar='input_file',
                     help='JSON description of the intersection')
parser.add_argument ('--events-file', metavar='events_file',
                     help='write event output to the specified file')
parser.add_argument ('--table-file', metavar='table_file',
                     help='write LaTeX table output to the specified file' +
                     ' as a LaTex longtable.')
parser.add_argument ('--table-level', type=int, metavar='table_level',
                     help='control the level of detail in the table: ' +
                     '1 is normal, 0 none')
parser.add_argument ('--table-start', type=decimal.Decimal,
                     metavar='table_start',
                     help='do not include information before this time' +
                     ' in the LaTex table, default is -1.000')
parser.add_argument ('--duration', type=decimal.Decimal, metavar='duration',
                     help='length of time to run the simulator, ' +
                     'default is 0.000')
parser.add_argument ('--table-caption', metavar='table_caption',
                     help='caption of LaTex table.')
parser.add_argument ('--last-event-time', metavar='last_event_time',
                     help='time of last event written to this file'),
parser.add_argument ('--script-input', metavar='script_input',
                     help='actions for the simulator to execute')
parser.add_argument ('--print-statistics', type=bool,
                     metavar='print_statistics',
                     help='print statistics about the simulation ' +
                     'default is False.')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_input = False
input_file_name = ""
do_events_output = False
events_file_name = ""
do_table_output = False
table_file_name = ""
table_level = 0
end_time = decimal.Decimal ('0.000')
table_start_time  = decimal.Decimal ('-1.000')
table_caption = "no caption"
do_script_input = False
script_input_file = ""
do_last_event_time_output = False
print_statistics = False
verbosity_level = 1
error_counter = 0

# Verbosity_level and table level:
# 1 only errors (and statistics if requested)
# 2 add lamp changes, script actions, and vehicles and pedestrians
#   arriving, leaving and reaching milestones
# 3 add state changes and blocking
# 4 add toggle and sensor changes
# 5 add lots of other items for debugging
# 6 add tests of toggles

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

if (arguments ['events_file'] != None):
  do_events_output = True
  events_file_name = arguments ['events_file']
  events_file_name = pathlib.Path(events_file_name)

if (arguments ['table_file'] != None):
  do_table_output = True
  table_file_name = arguments ['table_file']
  table_file_name = pathlib.Path(table_file_name)

if ((arguments ['table_level'] != None) and do_table_output):
  table_level = arguments ['table_level']

if (arguments ['duration'] != None):
  end_time = arguments ['duration']
  
if (arguments ['table_start'] != None):
  table_start_time = arguments ['table_start']

if (arguments ['table_caption'] != None):
  table_caption = arguments ['table_caption']
  
if (arguments ['script_input'] != None):
  do_script_input = True
  script_file_name = arguments ['script_input']
  script_file_name = pathlib.Path(script_file_name)
  
if (arguments ['last_event_time'] != None):
  do_last_event_time_output = True
  last_event_time_file_name = arguments ['last_event_time']
  last_event_time_file_name = pathlib.Path(last_event_time_file_name)

if (arguments ['print_statistics'] != None):
  print_statistics = arguments ['print_statistics']

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

start_time = decimal.Decimal("0.000")
current_time = fractions.Fraction(start_time)
last_event_time = current_time

#
# Capitolize the first letter of a string.
#
def cap_first_letter (the_string):
  return (the_string[0].upper() + the_string[1:])

# Write the first lines in the table file.

if (do_table_output):
  table_file = open (table_file_name, 'w')
  table_file.write ("\\begin{longtable}{c | P{1.00cm} | p{9.25cm}}\n")
  table_file.write ("  \\caption{" + table_caption + "} \\\\\n")
  table_file.write ("  Time & Lane & Event \\endfirsthead \n")
  table_file.write ("  \\caption{" + table_caption + " continued} \\\\\n")
  table_file.write ("  Time & Lane & Events \\endhead \n")

# Write the first line in the event file.
if (do_events_output):
  events_file = open (events_file_name, 'w')
  events_file.write ("time,lane,type,color,name,position_x,position_y," +
                     "destination_x,destination_y,orientation,length,speed," +
                     "travel path,present\n")

# Subroutine to write a traffic element event to the event file.
def write_event (traffic_element, tag):
  global last_event_time
  
  events_file.write (str(current_time) + "," +
                     traffic_element["current lane"] + "," +
                     traffic_element["type"] + "," +
                     tag + "," +
                     traffic_element["name"] + "," +
                     str(traffic_element["position x"]) + "," +
                     str(traffic_element["position y"]) + "," +
                     str(traffic_element["target x"]) + "," +
                     str(traffic_element["target y"]) + "," +
                     str(traffic_element["angle"]) + "," +
                     str(traffic_element["length"]) + "," +
                     str(traffic_element["speed"]) + "," +
                     traffic_element["travel path name"] + "," +
                     str(traffic_element["present"]) + "\n")
  last_event_time = current_time
  return

# Read the intersection information.

if (do_input):
  input_file = open (input_file_name, 'r')
  intersection_info = json.load (input_file)
  finite_state_machine = intersection_info["finite state machine"]
  input_file.close()
else:
  intersection_info = dict()
  finite_state_machine = dict()

signal_faces_list = intersection_info ["signal faces"]
signal_faces_dict = dict()
for signal_face in signal_faces_list:
  signal_face_name = signal_face["name"]
  signal_faces_dict[signal_face_name] = signal_face

travel_paths = intersection_info ["travel paths"]
car_length = intersection_info ["car length"]
truck_length = intersection_info ["truck length"]
crosswalk_width = intersection_info ["crosswalk width"]

for signal_face in signal_faces_list:
  signal_face ["clearance requested by"] = set()
  
if (do_trace):
  trace_file.write ("Starting Signal Faces:\n")
  pprint.pprint (signal_faces_list, trace_file)

# Read the script file, if one was specified.
script_set = set()
if (do_script_input):
  with open (script_file_name, 'r') as scriptfile:
    reader = csv.DictReader (scriptfile)
    for row in reader:
      the_time = fractions.Fraction (row['time'])
      the_operator = row['operator']
      signal_face_name = row['signal face']
      the_operand = row['operand']
      permissive_delay = fractions.Fraction (row['permissive_delay'])
      the_count = int(row['count'])
      the_interval = fractions.Fraction (row['interval'])
      for counter in range(0, the_count):
        this_time = the_time + (the_interval * counter);
        this_action = (this_time, the_operator, signal_face_name, the_operand,
                       permissive_delay)
        script_set.add(this_action)
 
  if (do_trace):
    trace_file.write ("Script:\n")
    pprint.pprint (script_set, trace_file)
    trace_file.write ("\n")
  
# System Programs

# The clock is advanced only if this cycle has resulted in no activity.
no_activity = True              

# Format the clock for display
def format_time(the_time):
  return (f'{the_time:07.3f}')

# Format the clock for display unless it has the same value as last time,
# in which case just produce a blank space.
previous_time = None
def format_time_N(the_time):
  global previous_time
  if (the_time == previous_time):
    return (" ")
  previous_time = the_time
  return (format_time (the_time))

# The conversion factor from miles per hour to feet per second:
mph_to_fps = fractions.Fraction(5280, 60*60)

# Format a speed for display.
def format_speed(the_speed_in_fps):
  the_speed_in_mph = the_speed_in_fps / mph_to_fps
  if (the_speed_in_mph < 5.0):
    return ((f'{the_speed_in_fps:04.1f}') + " fps")
  else:
    return ((f'{the_speed_in_mph:04.1f}') + " mph")

# Format a location for display.
def format_location(the_location):
  return (f'{the_location:.0f}')

# Format a distance for display.
def format_distance(the_distance_in_feet):
  if (the_distance_in_feet == 0):
    return ("0 ft")
  if (the_distance_in_feet >= 9):
    return (format_location(the_distance_in_feet) + " ft")
  if (the_distance_in_feet >= 1):
    return (f'{the_distance_in_feet:.1f}' + " ft")
  the_distance_in_inches = the_distance_in_feet * 12
  if (the_distance_in_inches >= 9):
    return (f'{the_distance_in_inches:.0f}' + " in")
  if (the_distance_in_inches >= 1):
    return (f'{the_distance_in_inches:.1f}' + " in")
  return (f'{the_distance_in_inches:.6f}' + " in")

# Format a traffic element's place name for display.
def place_name(traffic_element):
  current_lane = traffic_element["current lane"]
  match current_lane:
    case "intersection":
      return ("the intersection")
    case "crosswalk":
      return ("the crosswalk")
    case _:
      return ("lane " + current_lane)
  return (None)

# Return the value of a named toggle in a specified signal face.
def toggle_value (signal_face, toggle_name):
  global error_counter
                                            
  toggles = signal_face["toggles"]
  for the_toggle in toggles:
    if (the_toggle["name"] == toggle_name):
      if (verbosity_level >= 6):
        print (format_time(current_time) + " toggle " + signal_face["name"] +
               "/" + toggle_name + " is " + str(the_toggle["value"]) + ",")
      return (the_toggle["value"])

  error_counter = error_counter + 1
  if (verbosity_level >= 1):
    print (format_time(current_time) + "signal face " + signal_face["name"] +
           " testing unknown toggle " + toggle_name + ".")
  return None

# Set the value of a named toggle in a specified signal face.
def set_toggle_value (signal_face, toggle_name, new_value, source):
  global no_activity
  global error_counter
  
  toggles = signal_face["toggles"]
  for the_toggle in toggles:
    if (the_toggle["name"] == toggle_name):
      if (the_toggle["value"] != new_value):
        if (new_value):
          operator = "Set toggle "
        else:
          operator = "Clear toggle "
        if (source != ""):
          byline = " by " + source
        else:
          byline = ""
          
        if (verbosity_level >= 4):
          print (format_time(current_time) + " signal face " +
                 signal_face["name"] + " " + operator + toggle_name + byline +
                 ".")
            
        if ((table_level >= 4) and (current_time > table_start_time)):
          table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                            signal_face["name"] + "& " + operator + 
                            toggle_name + byline + ". \\\\\n")
        no_activity = False
        the_toggle["value"] = new_value

        # Compute the maximum time a traffic element must wait at this
        # signal face.  The wait time starts when a sensor triggers a
        # toggle and ends when traffic is flowing through that signal face.
        if ((toggle_name == "Traffic Flowing") and ("waiting" in signal_face)):
          if (signal_face["waiting"]):
            signal_face["waiting"] = False
            wait_time = current_time - signal_face["wait start"]
            if (verbosity_level >= 5):
              print (format_time(current_time) + " signal face " +
                     signal_face["name"] + " finishes waiting: " +
                     format_time(wait_time) + ".")
            if ((table_level >= 5) and (current_time > table_start_time)):
              table_file.write ("\\hline " + format_time_N(current_time) +
                                " & " + signal_face ["name"] +
                                " & finishes waiting for " +
                                format_time(wait_time) + ".\\\\\n")
            if ("max wait time" not in signal_face):
              signal_face ["max wait time"] = wait_time
              signal_face ["max wait start"] = signal_face["wait start"]
            else:
              if (wait_time > signal_face["max wait time"]):
                signal_face["max wait time"] = wait_time
                signal_face["max wait start"] = signal_face["wait start"]
                        
      return
    
  if (verbosity_level >= 1):
    print (format_time(current_time) + " setting unknown toggle " +
           signal_face["name"] + "/" + toggle_name + ".")
  error_counter = error_counter + 1
  return

# Return True if traffic can not flow through the specified signal
# face because traffic is already flowing through the conflicting signal face.
def does_conflict (signal_face, conflicting_signal_face):
  conflict_set = signal_face["conflicts"]
  if (conflicting_signal_face ["name"] in conflict_set):
    if (verbosity_level >= 5):
      print (format_time(current_time) + " signal face " +
             signal_face["name"] + " conflicts with " +
             conflicting_signal_face ["name"] + ".")
    return True
  if (verbosity_level >= 5):
    print (format_time(current_time) + " signal face " + signal_face["name"] +
           " does not conflict with " + conflicting_signal_face ["name"] + ".")
  return False

# Allow signal faces to turn green in the order they requested, but
# allow non-conflicting faces to turn green even if they were requested
# later, provided they haven't already turned green while the oldest
# request is waiting for its turn and provided the oldest request has not
# been waiting too long.

requesting_green = list()
allowed_green = list()
had_its_chance = list()

def green_request_granted():
  global requesting_green
  global allowed_green
  global had_its_chance
  global no_activity

  # If a signal face is on the requesting green list, but is no longer
  # requesting green, remove it from the list.  This usually happens
  # because the signal face has turned green, but can also happen
  # if a vehicle makes a permissive right turn so the signal face
  # no longer needs to turn green.
  
  to_remove = list()
  for signal_face in requesting_green:
    if (not toggle_value(signal_face, "Request Green")):
      if (verbosity_level >= 5):
        print (format_time(current_time) + " signal face " +
               signal_face["name"] + " no longer requesting green.")
      to_remove.append(signal_face)
  for signal_face in to_remove:
    requesting_green.remove(signal_face)

  # Likewise, if a signal face is on the allowed green list, but is no
  # longer interested in turning green, remove it from the list.
  to_remove = list()
  for signal_face in allowed_green:
    if (not toggle_value(signal_face, "Request Green")):
      if (not ((toggle_value(signal_face, "Request Clearance")) or
               toggle_value(signal_face, "Request Partial Clearance"))):
        if (verbosity_level >= 5):
          print (format_time(current_time) + " signal face " +
                 signal_face["name"] + " no longer requesting clearance.")
        to_remove.append(signal_face)
  for signal_face in to_remove:
    allowed_green.remove(signal_face)
    signal_face_name = signal_face["name"]
    # Remove the clearance request from the signal faces we sent it to.
    for conflicting_face in signal_faces_list:
      if (signal_face_name in conflicting_face["clearance requested by"]):
        if (verbosity_level >= 5):
          print (format_time(current_time) + " signal face " +
                 signal_face_name + " no longer requesting clearance from " +
                 conflicting_face["name"] + ".")
        conflicting_face["clearance requested by"].remove(signal_face_name)
        if (len(conflicting_face["clearance requested by"]) == 0):
          set_toggle_value (conflicting_face, "Clearance Requested", False,
                            "system program Partial Clearance Requested")
              
  # If a signal face is requesting green, place it on the list of
  # signal faces requesting green unless it is already on the list
  # or is on the list of signal faces allowed to turn green.
  for signal_face in signal_faces_list:
    if ((toggle_value(signal_face, "Request Green")) and
         (signal_face not in requesting_green) and
         (signal_face not in allowed_green)):
      if (verbosity_level >= 5):
        print (format_time(current_time) + " signal face " +
               signal_face["name"] + " requesting green.")
      requesting_green.append(signal_face)

      # Start the waiting clock.  It will end when traffic flows
      # at this signal face.              
      if ("waiting" not in signal_face):
        signal_face["waiting"] = False
      if (not signal_face["waiting"]):
        signal_face["wait start"] = current_time
        signal_face["waiting"] = True
        if (verbosity_level >= 5):
          print (format_time(current_time) + " signal face " +
                 signal_face["name"] + " starts waiting.")
        if ((table_level >= 5) and (current_time > table_start_time)):
          table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                            signal_face ["name"] + "& starts waiting. \\\\\n")

  # If the list of signal faces allowed to turn green is empty,
  # allow the oldest signal face on the list of signal faces
  # requesting to turn green to turn green and empty the list
  # of signal faces that have turned green out of turn.
  if ((len(allowed_green) == 0) and (len(requesting_green) > 0)):
    next_green = requesting_green.pop(0)  
    allowed_green.append(next_green)
    had_its_chance = list()
    no_activity = False
    if (verbosity_level >= 5):
      print (format_time(current_time) + " signal face " + next_green["name"] +
             " is allowed to turn green because no other face is" +
             " allowed to turn green.")

  # If the oldest signal face on the list of signal faces requesting
  # to turn green does not conflict with any of the signal faces already
  # allowed to turn green, also allow it to turn green.  Keep doing this
  # until either there are no signal faces requesting to turn green
  # or the oldest signal face has a conflict.
  keep_greening = True
  while (keep_greening):
    if (len(requesting_green) == 0):
      keep_greening = False
      continue
    signal_face = requesting_green[0]
    no_conflicts = True
    keep_greening= False
    for conflicting_signal_face in allowed_green:
      if (does_conflict (signal_face, conflicting_signal_face)):
        no_conflicts = False
        
    # Add "or True" to the conditional test below to test safety_check.
    # Doing that will cause any complex script, including the multiple script
    # used to build the documentation, to switch to flashing.
    
    if (no_conflicts): 
      requesting_green.remove(signal_face)
      allowed_green.append(signal_face)
      had_its_chance.append(signal_face)
      keep_greening = True
      no_activity = False
      if (verbosity_level >= 5):
        print (format_time(current_time) + " signal face " +
               signal_face["name"] +
               " is allowed to turn green because it does not conflict" +
               " with any signal face that is already allowed to turn" +
               " green.")
    
  # Allow a signal face to turn green even if it is not its turn
  # provided it does not conflict with any signal face already
  # allowed to turn green and has not already been allowed to turn
  # green out of turn since the oldest waiting signal face was allowed
  # to turn green.  However, if the oldest signal face has
  # been waiting a long time, don't allow any other signal face
  # to go ahead of it.
  if (len(requesting_green) > 0):
    signal_face = requesting_green[0]
    waiting_time = current_time - signal_face["wait start"]
    if (waiting_time > signal_face["waiting limit"]):
      if (verbosity_level >= 5):
        print (format_time(current_time) + " signal face " +
               signal_face["name"] +
               " is given preference because it has been waiting for " +
               format_time(waiting_time) + ".")
    else:
      to_remove = list()
      for signal_face in requesting_green:
        no_conflicts = True
        for conflicting_signal_face in allowed_green:
          if (does_conflict (signal_face, conflicting_signal_face)):
            no_conflicts = False
        if (no_conflicts and (signal_face not in had_its_chance)):
          to_remove.append(signal_face)
          allowed_green.append(signal_face)
          had_its_chance.append(signal_face)
          no_activity = False
          if (verbosity_level >= 5):
            print (format_time(current_time) + " signal face " +
                   signal_face["name"] +
                   " is allowed to turn green because it does not conflict" +
                   " with any other face that is already allowed to turn" +
                   " green and has not already turned green while the oldest" +
                   " signal face has been waiting for its turn.")
            
      for signal_face in to_remove:
        requesting_green.remove(signal_face)

  if (verbosity_level >= 5):
    requesting_green_names = ""
    for signal_face in requesting_green:
      requesting_green_names = (requesting_green_names +
                                signal_face["name"] + " ")
    if (len(requesting_green_names) > 0):
      print (format_time(current_time) + " signal faces " +
             requesting_green_names + "are requesting to turn green.")
    allowed_green_names = ""
    for signal_face in allowed_green:
      allowed_green_names = allowed_green_names + signal_face["name"] + " "
    if (len(allowed_green_names) > 0):
      print (format_time(current_time) + " signal faces " +
             allowed_green_names + "are allowed to turn green.")

  # Remove a signal face from the allowed green list if it has its
  # traffic flowing.  This will allow the next signal face in the
  # requesting green list, if there is one, to be allowed to turn green.
  # That signal face will conflict with a signal face that is already green,
  # thus causing it to turn red.
  for signal_face in allowed_green:
    if (toggle_value(signal_face, "Traffic Flowing")):
      no_activity = False
      allowed_green.remove(signal_face)
      set_toggle_value (signal_face, "Green Request Granted", False,
                        "system program Green Request Granted")
      signal_face["clearance requested by"] = set()
      if (verbosity_level >= 5):
        print (format_time(current_time) + " signal face " +
               signal_face["name"] + " traffic is now flowing.")
      
  for signal_face in allowed_green:
    set_toggle_value (signal_face, "Green Request Granted", True,
                      "system program Green Request Granted")
  return

def clearance_requested():
  for signal_face in signal_faces_list:
    if (toggle_value (signal_face, "Request Clearance")):
      conflicting_face_names = signal_face ["conflicts"]
      for conflicting_face_name in conflicting_face_names:
        conflicting_face = signal_faces_dict[conflicting_face_name]
        if (not toggle_value (conflicting_face, "Cleared")):
          set_toggle_value (conflicting_face, "Clearance Requested", True,
                            "system program Clearance Requested")
          conflicting_face["clearance requested by"].add(signal_face["name"])
  return
        
def partial_clearance_requested():
  for signal_face in signal_faces_list:
    if (toggle_value (signal_face, "Request Partial Clearance")):
      conflicting_face_names = signal_face ["partial conflicts"]
      for conflicting_face_name in conflicting_face_names:
        conflicting_face = signal_faces_dict[conflicting_face_name]
        if (not toggle_value (conflicting_face, "Cleared")):
          set_toggle_value (conflicting_face, "Clearance Requested", True,
                            "system program Partial Clearance Requested")
          conflicting_face["clearance requested by"].add(signal_face["name"])
  return

# Maintain the Conflicting Paths are Clear toggle.  It is false
# unless the signal face is requesting clearance and all conflicting
# paths are clear.
def conflicting_paths_are_clear():
  for signal_face in signal_faces_list:
    all_paths_clear = False
    if (toggle_value (signal_face, "Request Clearance") or
        toggle_value (signal_face, "Request Partial Clearance")):
      all_paths_clear = True
      conflicting_face_names = signal_face ["conflicts"]
      for conflicting_face_name in conflicting_face_names:
        conflicting_face = signal_faces_dict[conflicting_face_name]
        if (not toggle_value (conflicting_face, "Cleared")):
          all_paths_clear = False
    set_toggle_value (signal_face, "Conflicting Paths are Clear",
                      all_paths_clear,
                      "system program Conflicting Paths are Clear")
  return

# Do the same for partial conflicting paths.

def partial_conflicting_paths_are_clear():
  for signal_face in signal_faces_list:
    all_paths_clear = False
    if (toggle_value (signal_face, "Request Partial Clearance")):
      all_paths_clear = True
      conflicting_face_names = signal_face ["partial conflicts"]
      for conflicting_face_name in conflicting_face_names:
        conflicting_face = signal_faces_dict[conflicting_face_name]
        if (not toggle_value (conflicting_face, "Cleared")):
          all_paths_clear = False
    set_toggle_value (signal_face, "Partial Conflicting Paths are Clear",
                      all_paths_clear,
                      "system program Partial Conflicting Paths are Clear")
  return

# Check for conflicting greens, since this is a safety issue.
def safety_check ():
  global error_counter

  conflict_detected = False
  
  for signal_face in signal_faces_list:
    if (signal_face["state"] == "Green"):
      for conflicting_signal_face in signal_faces_list:
        if ((conflicting_signal_face != signal_face) and
            (conflicting_signal_face["state"] == "Green")):
          if (does_conflict (signal_face, conflicting_signal_face)):
            if (verbosity_level >= 1):
              print (format_time(current_time) + " signal faces " +
               signal_face["name"] + " and " +
               conflicting_signal_face["name"] + " are both green.")
            if (do_trace):
              trace_file.write ("Safety Check detected a failure.\n")
              pprint.pprint (signal_face, trace_file)
              pprint.pprint (conflicting_signal_face, trace_file)
            conflict_detected = True
            
  if (conflict_detected):
    for signal_face in signal_faces_list:
      sensors = signal_face["sensors"]
      sensor = sensors["Flash"]
      sensor ["value"] = True

      if (verbosity_level >= 2):
        print (format_time(current_time)  + " sensor " +
               signal_face["name"] + "/" + "Flash" + " set to " +
                   str(sensor["value"]) + " by system program safety check.")
      if ((table_level >= 2) and (current_time > table_start_time)):
        table_file.write ("\\hline " + format_time_N(current_time) +
                          " & " + signal_face ["name"] + " & Sensor " +
                          "Flash" + " set to " + str(sensor["value"]) +
                          " by system program safety check. \\\\\n")
        
  return

# the traffic signal simulator: run the finite state machines

running_timers = list()

def perform_actions (signal_face, substate):
  global running_timers
  global error_counter
  global last_event_time
  
  for action in substate["actions"]:
    if (verbosity_level >= 5):
      print (format_time(current_time) + " signal face " +
             signal_face["name"] + " action " + action[0] + " : " + action[1] +
             ".")
    match action[0]:
      case "set lamp":
        internal_lamp_name = action[1]
        lamp_names_map = signal_face["lamp names map"]
        if (internal_lamp_name in lamp_names_map):
          external_lamp_name = lamp_names_map[internal_lamp_name]
        else:
          external_lamp_name = internal_lamp_name

        if (signal_face["iluminated lamp name"] == external_lamp_name):
          if (verbosity_level >= 5):
            print (format_time(current_time) + " signal face " +
                   signal_face["name"] + " lamp already set to " +
                   external_lamp_name + ",")
        else:
          signal_face["iluminated lamp name"] = external_lamp_name
          if (verbosity_level >= 2):
            print (format_time(current_time) + " signal face " +
                   signal_face["name"] + " lamp set to " + external_lamp_name +
                   ".")
          if ((table_level >= 2) and (current_time > table_start_time)):
            table_file.write ("\\hline " + format_time_N(current_time) +
                              " & " + signal_face["name"] +
                              " & Set lamp to " + external_lamp_name +
                              ". \\\\\n")
          if (do_events_output):
            events_file.write (str(current_time) + "," + signal_face["name"] +
                               ",lamp," + external_lamp_name + "\n")
            last_event_time = current_time
          
      case "set toggle":
        set_toggle_value (signal_face, action[1], True, "")
        
      case "clear toggle":
        # Don't clear a toggle if a sensor which sets it is still active.
        new_toggle_value = False
        signal_face_name = signal_face["name"]
        toggle_name = action[1]
        full_toggle_name = signal_face_name + "/" + toggle_name
        # Check all of the signal faces to see if any have a sensor
        # which triggers this toggle.
        for test_signal_face in signal_faces_list:
          test_signal_face_name = test_signal_face["name"]
          test_sensors = test_signal_face["sensors"]
          for test_sensor_name in test_sensors:
            full_test_sensor_name = (test_signal_face_name + "/" +
                                     test_sensor_name)
            test_sensor = test_sensors[test_sensor_name]
            test_toggle_names = test_sensor["toggles"]
            for test_toggle_name in test_toggle_names:
              exploded_test_toggle_name = test_toggle_name.partition("/")
              if (exploded_test_toggle_name[1] == ""):
                referenced_signal_face_name = test_signal_face_name
                referenced_toggle_name_root = test_toggle_name
              else:
                referenced_signal_face_name = exploded_test_toggle_name[0]
                referenced_toggle_name_root = exploded_test_toggle_name[2]
              full_referenced_toggle_name = (referenced_signal_face_name +
                                             "/" + referenced_toggle_name_root)
              if (full_referenced_toggle_name == full_toggle_name):
                # This sensor triggers the toggle we are trying to clear.
                # If it is active we cannot clear this toggle.
                if (test_sensor["value"]):
                    new_toggle_value = True
                    if (verbosity_level >= 5):
                      print (format_time(current_time) + " signal face " +
                             signal_face_name +
                             " Unable to clear toggle " + toggle_name +
                             " because sensor " + full_test_sensor_name +
                             " is still active.")
                    if ((table_level >= 5) and
                        (current_time > table_start_time)):
                      table_file.write ("\\hline " +
                                        format_time_N(current_time) +
                                        " & " + signal_face_name +
                                        " & Unable to clear toggle " +
                                        toggle_name + " because sensor " +
                                        full_test_sensor_name +
                                        " is still active." + "\\\\\n")
              
        if (not new_toggle_value):
          set_toggle_value (signal_face, toggle_name, new_toggle_value, "")
          
      case "start timer":
        timer_name = action[1]
        timers_list = signal_face["timers"]
        for the_timer in timers_list:
          if (the_timer["name"] == timer_name):
            if (the_timer["duration"] != decimal.Decimal ("inf")):
              the_timer["state"] = "running"
              the_timer["remaining time"] = the_timer["duration"]
              remaining_time = fractions.Fraction(the_timer["remaining time"])
              the_timer["completion time"] = current_time + remaining_time
              if (the_timer not in running_timers):
                running_timers.append(the_timer)
              if (verbosity_level >= 5):
                print (format_time(current_time) + " signal face " +
                       signal_face["name"] + " start timer " +
                       timer_name + " duration " +
                       format_time(the_timer["remaining time"]) + ".")
              if ((table_level >= 5) and (current_time > table_start_time)):
                table_file.write ("\\hline " + format_time_N(current_time) +
                                  " & " + signal_face ["name"] +
                                  " & Start timer " + timer_name + ". \\\\\n")
      case _:
        if (verbosity_level >= 1):
          print (format_time(current_time) + " signal face " +
                 signal_face["name"] + " unknown action " + action[0] + ".")
          error_counter = error_counter + 1
          
  return    

# Enter the signal face into the named state and substate.
def enter_state (signal_face, state_name, substate_name):
  global no_activity

  if ("state" in signal_face):
    old_state_name = signal_face["state"]
  else:
    old_state_name = ""
    
  if ("substate" in signal_face):
    old_substate_name = signal_face["substate"]
  else:
    old_substate_name = ""

  # Entering a state is only a significant event if the state is different.
  significant_event = False
  if ((state_name != old_state_name) or (substate_name != old_substate_name)):
    no_activity = False
    significant_event = True
  else:
    if (verbosity_level >= 5):
      print (format_time(current_time) + " signal face " +
             signal_face["name"] + " not a significant state change.")
      
  signal_face["state"] = state_name
  signal_face["substate"] = substate_name

  if (((verbosity_level >= 3) and significant_event) or
      (verbosity_level >= 5)):
    print (format_time(current_time) + " signal face " + signal_face["name"] +
           " enters state " + state_name +
           " substate " + substate_name + ".")
  if ((table_level >= 3) and (current_time > table_start_time) and
      significant_event):
    table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                      signal_face["name"] + " & " +
                      "Enter state " + state_name + " substate " +
                      substate_name + ". \\\\\n")
  states = finite_state_machine["states"]
  state = states[state_name]
  for substate in state:
    if (substate["name"] == substate_name):
      perform_actions (signal_face, substate)
          
  return

# The traffic element dictionary holds information about each car, truck
# and pedestrian who is close to the intersection.
traffic_elements = dict()

# Subroutine to return the speed limit for a lane in feet per second.
# The speed of a vehicle in the intersection is the speed of the lane
# the vehicle entered from or will exit onto, whichever is less,
# unless the vehicle stopped before entering the intersection
# in which case it is 25 mph.

def speed_limit (lane_name, travel_path_name, was_stopped):
  match lane_name:
    case "1" | "2" | "B" | "C" | "4" | "5" | "F" | "G":
      return (45 * mph_to_fps)
    case "A" | "D" | "3" | "E" | "6" | "H" | "J":
      return (25 * mph_to_fps)
    case "psw" | "pse" | "pnw" | "pne" | "crosswalk":
      return (fractions.Fraction(35, 10))
    case "intersection":
      if (was_stopped):
        return (25 * mph_to_fps)
      entering_lane_name = travel_path_name[0]
      exiting_lane_name = travel_path_name[1]
      entering_speed = speed_limit (entering_lane_name, travel_path_name,
                                    was_stopped)
      exiting_speed = speed_limit (exiting_lane_name, travel_path_name,
                                   was_stopped)
      return (min(entering_speed, exiting_speed))
    
  return None

# Rebuild the shape and clearance spaces of a traffic element
# after it has moved.
def rebuild_shapes (traffic_element):
  global vehicle_clearance

  # If the shape of a traffic element overlaps the shape of
  # a sensor, the sensor is triggered by the traffic element.
  start_x = traffic_element["position x"]
  start_y = traffic_element["position y"]
  min_x = start_x - (traffic_element["width"] / 2.0)
  min_y = start_y
  max_x = start_x + (traffic_element["width"] / 2.0)
  max_y = start_y + traffic_element["length"]
  box = shapely.geometry.box(min_x, min_y, max_x, max_y)
  box = shapely.affinity.rotate (box, traffic_element["angle"],
                                 origin=(start_x, start_y), use_radians=True)
  traffic_element["shape"] = box

  # If the shape of a traffic element overlaps the clearance space of a second
  # traffic element, the second is blocked by the first.
  # The clearance space of a traffic element is a box the width of the
  # traffic element, stop_clearance feet long, positioned just in front
  # of the traffic element
  stop_clearance = traffic_element["length"] / 3
  box = shapely.geometry.box(min_x, min_y, max_x, min_y - stop_clearance)
  box = shapely.affinity.rotate (box, traffic_element["angle"],
                                 origin=(start_x, start_y), use_radians=True)
  traffic_element["stop shape"] = box

  # However, the blocked vehicle cannot start moving until the blocking
  # vehicle has moved some distance beyond the clearance space.
  go_clearance = stop_clearance * 1.5
  box = shapely.geometry.box(min_x, min_y, max_x, min_y - go_clearance)
  box = shapely.affinity.rotate (box, traffic_element["angle"],
                                 origin=(start_x, start_y), use_radians=True)
  traffic_element["go shape"] = box
  
  
  return

# The traffic element has reached the next milestone.  Make it the current
# milestone.
def new_milestone (traffic_element):

  if (do_trace):
    trace_file.write ("New milestone top:\n")
    pprint.pprint (traffic_element, trace_file)
    
  this_milestone_index = traffic_element["milestone index"]
  milestones_list = traffic_element["milestones"]
  next_milestone_index = this_milestone_index + 1
  next_milestone = milestones_list[next_milestone_index]
  traffic_element["current lane"] = next_milestone[0]
  start_x = next_milestone[1]
  start_y = next_milestone[2]
  traffic_element["start x"] = start_x
  traffic_element["start y"] = start_y
  following_milestone_index = next_milestone_index + 1
  following_milestone = milestones_list[following_milestone_index]
  target_x = following_milestone[1]
  target_y = following_milestone[2]
  traffic_element["target x"] = target_x
  traffic_element["target y"] = target_y
  traffic_element["next lane"] = following_milestone[0]
  distance_between_milestones = math.sqrt(((start_x-target_x)**2) +
                                          ((start_y-target_y)**2))
  traffic_element["distance between milestones"] = distance_between_milestones
  traffic_element["speed"] = speed_limit(traffic_element["current lane"],
                                         traffic_element["travel path name"],
                                         traffic_element["was stopped"])
  # If the distance to the next milestone is zero the angle is indeterminate,
  # so don't change it.
  if (distance_between_milestones > 0):
    traffic_element["angle"] = math.atan2 (target_x - start_x,
                                           start_y - target_y)
  traffic_element["position x"] = start_x
  traffic_element["position y"] = start_y
  traffic_element["distance remaining"] = distance_between_milestones
  rebuild_shapes (traffic_element)
  traffic_element["milestone index"] = next_milestone_index

  if (do_trace):
    trace_file.write ("New milestone bottom:\n")
    pprint.pprint (traffic_element, trace_file)
    
  return

# Subroutine to add a traffic element to the traffic elements dictionary.
# A traffic element starts at its first milestone.
next_traffic_element_number = 0

def add_traffic_element (type, travel_path_name, permissive_delay):
  global travel_paths
  global traffic_elements
  global next_traffic_element_number
  global current_time
  
  traffic_element = dict()

  this_name = f'{type} {next_traffic_element_number:04d}'
  next_traffic_element_number = next_traffic_element_number + 1
  traffic_element["name"] = this_name
  
  traffic_element["type"] = type
  traffic_element["travel path name"] = travel_path_name
  traffic_element["permissive delay"] = permissive_delay
  travel_path = travel_paths[travel_path_name]
  milestone_list = travel_path["milestones"]
  traffic_element["milestones"] = milestone_list
  milestone_index = 0
  traffic_element["milestone index"] = -1
  traffic_element["was stopped"] = False

  match type:
    case "car":
      traffic_element["length"] = car_length
      traffic_element["width"] = 5.8
    case "truck":
      traffic_element["length"] = truck_length
      traffic_element["width"] = 8.5
    case "pedestrian":
      traffic_element["length"] = 2
      traffic_element["width"] = (crosswalk_width / 3.0)

  traffic_element["current time"] = current_time
  traffic_element["present"] = True
  traffic_element["blocker name"] = None
  traffic_element["stopped time"] = current_time
  new_milestone (traffic_element)

  # If this traffic element would be born blocked, don't spawn it.
  blocker_name = check_still_blocked (traffic_element)
  
  if (blocker_name != None):
    # This traffic element does not get spawned.
    traffic_element["present"] = False
  
    if (verbosity_level >= 2):
      print (format_time(current_time) + " " + this_name +
             " is blocked from spawning by " + blocker_name + ".")
    if ((table_level >= 2) and (current_time > table_start_time)):
      table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                        traffic_element["current lane"] + " & " +
                        cap_first_letter(this_name) +
                        " is blocked from spawning by " + blocker_name +
                        ". \\\\\n")
    if (do_trace):
      trace_file.write ("New traffic element not created:\n")
      pprint.pprint (traffic_element, trace_file)
      trace_file.write (" because it is blocked by:\n")
      pprint.pprint (traffic_elements[blocker_name], trace_file)

  else:
    if (verbosity_level >= 2):
      print (format_time(current_time) + " " + this_name +
             " starts on travel path " + travel_path_name +
             " in lane " + traffic_element["current lane"] +
             " at position (" +
             format_location(traffic_element["position x"]) +
             ", " + format_location(traffic_element["position y"]) +
             ") distance to next milestone " +
             format_distance(traffic_element["distance remaining"]) +
             " speed " + format_speed(traffic_element["speed"]) +
             " angle " + str(math.degrees(traffic_element["angle"])) +
             " degrees.")
    if ((table_level >= 2) and (current_time > table_start_time)):
      table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                        traffic_element["current lane"] + " & " +
                        cap_first_letter(this_name) +
                        " starts on travel path " +
                        travel_path_name + " speed " +
                        format_speed(abs(traffic_element["speed"])) +
                        ". \\\\\n")
    if (do_events_output):
      write_event (traffic_element, "new")
                       
    traffic_elements[this_name] = traffic_element

    if (do_trace):
      trace_file.write ("New traffic element:\n")
      pprint.pprint (traffic_element, trace_file)
    
  return

# Check if a traffic element is triggering a sensor
def check_overlap_sensor (traffic_element, sensor):
  # If either the traffic elements or the sensor does not have a shape,
  # there cannot be any overlap between them.
  if ("shape" not in traffic_element):
    return (False)
  if ("shape" not in sensor):
    return (False)

  shape_A = traffic_element["shape"]

  # If the traffic element has left the intersection it has no shape.
  if (shape_A == None):
    return (False)
  
  shape_B_list = sensor["shape"]
  shape_B = shapely.geometry.box (shape_B_list[0], shape_B_list[1],
                                  shape_B_list[2], shape_B_list[3])
  
  if (shape_A.intersects(shape_B)):
    if (do_trace):
      trace_file.write ("These objects intersect at " +
                        format_time(current_time) + ":\n")
      pprint.pprint (traffic_element, trace_file)
      pprint.pprint (shape_B)
      pprint.pprint (sensor, trace_file)
      trace_file.write ("\n")
      
    return (True)
  else:
    return (False)

# Subroutine to test for overlap of a traffic element's stop space
# with another traffic element.  Return None if there is no blockage;
# otherwise return the name of the blocking traffic element.
def check_stopped_by(traffic_element_A, traffic_element_B):

  # If either of the traffic elements does not have a shape,
  # there cannot be any overlap between them.
  
  if ("shape" not in traffic_element_A):
    return (None)
  if ("shape" not in traffic_element_B):
    return (None)

  shape_A = traffic_element_A["stop shape"]
  shape_B = traffic_element_B["shape"]
  
  # An object will have no shape if it has left the simulation.
  if ((shape_A == None) or (shape_B == None)):
    return (None)
  
  if (shape_A.intersects(shape_B)):
    if (do_trace):
      trace_file.write ("These objects intersect at " +
                        format_time(current_time) + ":\n")
      pprint.pprint (traffic_element_A, trace_file)
      pprint.pprint (traffic_element_B, trace_file)
      trace_file.write ("\n")
      
    return (traffic_element_B["name"])
  else:
    return (None)

# Subroutine to test for overlap of a traffic element's go space
# with another traffic element.  Return None if there is no blockage;
# otherwise return the name of the blocking traffic element.
def check_still_stopped_by(traffic_element_A, traffic_element_B):

  # If either of the traffic elements does not have a shape,
  # there cannot be any overlap between them.
  
  if ("shape" not in traffic_element_A):
    return (None)
  if ("shape" not in traffic_element_B):
    return (None)

  shape_A = traffic_element_A["go shape"]
  shape_B = traffic_element_B["shape"]
  
  # An object will have no shape if it has left the simulation.
  if ((shape_A == None) or (shape_B == None)):
    return (None)
  
  if (shape_A.intersects(shape_B)):
    if (do_trace):
      trace_file.write ("These objects intersect at " +
                        format_time(current_time) + ":\n")
      pprint.pprint (traffic_element_A, trace_file)
      pprint.pprint (traffic_element_B, trace_file)
      trace_file.write ("\n")
      
    return (traffic_element_B["name"])
  else:
    return (None)

# Subroutine to check a traffic element to see if the last move
# caused it to overlap another traffic element.
# If so, return that blocking traffic element's name.
# Otherwise, return None.
def check_blocked(traffic_element):
  for other_traffic_element_name in traffic_elements:

    # Only check other traffic elements
    if (other_traffic_element_name == traffic_element["name"]):
      continue

    other_traffic_element = traffic_elements[other_traffic_element_name]
    blocking_name = check_stopped_by (traffic_element, other_traffic_element)
    if (blocking_name != None):
      return blocking_name

  return (None)

# Check a traffic element to see if is still blocked.
# If so, return that blocking traffic element's name.
# If not, return None.
def check_still_blocked(traffic_element):
  for other_traffic_element_name in traffic_elements:

    # Only check other traffic elements
    if (other_traffic_element_name == traffic_element["name"]):
      continue

    other_traffic_element = traffic_elements[other_traffic_element_name]
    blocking_name = check_still_stopped_by (traffic_element,
                                            other_traffic_element)
    if (blocking_name != None):
      return blocking_name
    
  return (None)

# Subroutine to check an area for the presence of a traffic element that
# makes moving into the area unsafe.
def check_conflicting_traffic (traffic_element, permissive_info):
  global error_counter
  
  # We can enter the intersection if it is safe.  First, stop for
  # a second.  A real driver will be checking for oncoming traffic.

  if (do_trace):
    trace_file.write ("Check for conflicting traffic with " +
                      traffic_element["name"] + ".\n")
    pprint.pprint (traffic_element, trace_file)
    
  if (traffic_element["speed"] > 0):
    if (do_trace):
      trace_file.write (" Still moving.\n\n")
    return False

  stopped_duration = current_time - traffic_element["stopped time"]
  if (do_trace):
    trace_file.write (" Stopped for " + format_time(stopped_duration)
                      + ".\n")
  if (stopped_duration < traffic_element["permissive delay"]):
    if (do_trace):
      trace_file.write (" Not stopped long enough.\n\n")
    return False
        
  # Check for a vehicle present or approaching.
  for permissive_item in permissive_info:
    movement_type = permissive_item[0]
    permissive_shape_list = permissive_item[1]
    permissive_shape = shapely.geometry.box (permissive_shape_list[0],
                                             permissive_shape_list[1],
                                             permissive_shape_list[2],
                                             permissive_shape_list[3])
    for other_traffic_element_name in traffic_elements:

      # Only check other traffic elements
      if (other_traffic_element_name == traffic_element["name"]):
        continue

      other_traffic_element = traffic_elements[other_traffic_element_name]
      if (not other_traffic_element["present"]):
        continue
          
      stop_shape = other_traffic_element["stop shape"]
      if (stop_shape.intersects(permissive_shape)):
        if (do_trace):
          trace_file.write ("Possible conflict with " +
                            other_traffic_element_name + ":\n")
          pprint.pprint (stop_shape, trace_file)
          pprint.pprint (permissive_shape_list, trace_file)
          pprint.pprint (permissive_shape, trace_file)
          
        if (movement_type == "present"):
          if (do_trace):
            trace_file.write (" Permissive turn is blocked by presence:\n")
            pprint.pprint (other_traffic_element, trace_file)
            trace_file.write ("\n")
          return False

        # The other traffic element most be moving towards us
        # to make entering unsafe.
        if (other_traffic_element["speed"] == 0):
          continue

        # Check the direction of movement.
        movement_angle = other_traffic_element["angle"]
        
        if (do_trace):
          trace_file.write ("Movement angle: " + str(movement_angle) + ".\n")
      
        match movement_type:

          case "moving North":
            if (abs(movement_angle) < math.radians(90)):
              if (do_trace):
                trace_file.write ("Permissive turn is blocked " +
                                  "by North movement.\n")
                pprint.pprint (other_traffic_element, trace_file)
                trace_file.write ("\n")
              return False
            else:
              if (do_trace):
                trace_file.write ("Permissive turn is not blocked " +
                                  "by North movement.\n")
                pprint.pprint (other_traffic_element, trace_file)           

          case "moving South":
            if (abs(movement_angle) > math.radians(90)):
              if (do_trace):
                trace_file.write ("Permissive turn is blocked " +
                                  "by South movement.\n")
                pprint.pprint (other_traffic_element, trace_file)
                trace_file.write ("\n")
              return False
            else:
              if (do_trace):
                trace_file.write ("Permissive turn is not blocked " +
                                  "by South movement.\n")
                pprint.pprint (other_traffic_element, trace_file)
            
          case "moving East":
            if ((movement_angle > math.radians(0)) and
                (movement_angle < math.radians(180))):
              if (do_trace):
                trace_file.write ("Permissive turn is blocked " +
                                  "by East movement.\n")
                pprint.pprint (other_traffic_element, trace_file)
                trace_file.write ("\n")
              return False
            else:
              if (do_trace):
                trace_file.write ("Permissive turn is not blocked " +
                                  " by East movement.\n")
                pprint.pprint (other_traffic_element, trace_file)

          case "moving West":
            if ((movement_angle < math.radians(0)) and
                (movement_angle > math.radians(-180))):
              if (do_trace):
                trace_file.write ("Permissive turn is blocked " +
                                  "by West movement.\n")
                pprint.pprint (other_traffic_element, trace_file)
                trace_file.write ("\n")
              return False
            else:
              if (do_trace):
                trace_file.write ("Permissive turn is not blocked " +
                                  "by West movement.\n")
                pprint.pprint (other_traffic_element, trace_file)
            
          case _:
            print ("Invalid conflicting movement: " + movement_type + ".")
            error_counter = error_counter + 1

  # If all the tests pass, we can proceed.
  if (do_trace):
    trace_file.write ("No conflicts.\n\n")
  return True

# Subroutine to see if a traffic element may change lanes.
# If we are trying to enter the intersection or crosswalk
# the light must either be green or the movement must be
# permitted even though the light is not green.

def can_change_lanes (traffic_element):
  global current_time
  
  this_milestone_index = traffic_element["milestone index"]
  next_milestone_index = this_milestone_index + 1
  previous_milestone_index = this_milestone_index - 1
  milestone_list = traffic_element["milestones"]
  next_milestone = milestone_list[next_milestone_index]
  previous_milestone = milestone_list[previous_milestone_index]
  
  current_lane = traffic_element["current lane"]

  # If the current lane does not have a signal face,
  # we can proceed.
  if (current_lane not in signal_faces_dict):
    return True
  
  signal_face = signal_faces_dict[current_lane]

  travel_path_name = traffic_element["travel path name"]
  travel_path = travel_paths[travel_path_name]
  
  match next_milestone[0]:
    case "intersection" | "crosswalk":
      
      if (do_trace):
        trace_file.write ("Considering entering " + next_milestone[0] + ":\n")
        pprint.pprint (traffic_element, trace_file)
        pprint.pprint (signal_face, trace_file)
        pprint.pprint (travel_path, trace_file)

      # If the lamp is green we can enter the intersection.
      iluminated_lamp_name = signal_face["iluminated lamp name"]
      green_lamps = ("Steady Circular Green", "Steady Left Arrow Green",
                     "Steady Left Arrow Green and Steady Circular Green",
                     "Steady Right Arrow Green", "Walk")
      if (iluminated_lamp_name in green_lamps):
        if (do_trace):
          trace_file.write (" Lamp is green.\n\n")
        return True

      # If the lamp is a flashing left arrow yellow we can enter the
      # intersection after a short pause provided there is no traffic
      # in or approaching the intersection that will interfere with us.
      permissive_left_lamps = "Flashing Left Arrow Yellow (lower)"
      if (iluminated_lamp_name in permissive_left_lamps):
        permissive_info = travel_path ["permissive left turn info"]
        if (check_conflicting_traffic (traffic_element, permissive_info)):
          if (do_trace):
            trace_file.write (" No conflicting trafficc elements.\n\n")
          return True
        else:
          return False

      # If the lamp is red, or about to turn red, we can turn right
      # after a short pause provided there is no conflicting traffic.
      permissive_red_lamps = ("Steady Circular Red", "Steady Left Arrow Red",
                              "Steady Right Arrow Red")
      permissive_yellow_lamps = ("Steady Circular Yellow",
                                 "Steady Left Arrow Yellow",
                                 "Steady Right Arrow Yellow")
      if ((iluminated_lamp_name in permissive_red_lamps) or
          (iluminated_lamp_name in permissive_yellow_lamps)):
        # If a right turn on red is allowed, the travel path will have
        # permissive info.
        permissive_info = travel_path ["permissive right turn info"]
        if (permissive_info == None):
          return False
        if (check_conflicting_traffic (traffic_element, permissive_info)):
          if (do_trace):
            trace_file.write (" No conflicting trafficc elements.\n\n")
          return True
        else:
          return False
          
      # The lamp is neither green nor permissive
      if (do_trace):
        trace_file.write (" Lamp is neither green nor permissive.\n\n")
      return False
        
    case _:
      # The milestone is neither the entrance to the intersection nor
      # the entrance to the crosswalk.  Always allow it.
      return True
    
  
# Subroutine to move a traffic element.
def move_traffic_element (traffic_element):
  global current_time
  global no_activity

  if (do_trace):
    trace_file.write ("Move traffic element top at " +
                      format_time(current_time) + ":\n")
    pprint.pprint (traffic_element, trace_file)
    
  # See if our blocker has moved out of the way.
  if (traffic_element["blocker name"] != None):
    blocker_name = check_still_blocked (traffic_element)
    if (blocker_name == None):
      # The blocker has left.
      old_speed = traffic_element["old speed"]
      blocker_name = traffic_element["blocker name"]
      blocker = traffic_elements[blocker_name]
      blocker_speed = blocker["speed"]
      if ((blocker_speed > 0) and (blocker_speed < old_speed)):
        old_speed = blocker_speed
      traffic_element["speed"] = old_speed
      traffic_element["blocker name"] = None

      if ((table_level >= 3) and (current_time > table_start_time)):
        table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                          traffic_element["current lane"] + " & " +
                          cap_first_letter(traffic_element["name"]) +
                          " is unblocked. \\\\\n")
        
      if (verbosity_level >= 3):  
        print (format_time(current_time) + " " + traffic_element["name"] +
               " in " + place_name(traffic_element) + " is unblocked.")
      
      if (do_trace):
        trace_file.write (" Blocker has departed.\n")

      if (do_events_output):
        write_event(traffic_element, "unblocked")
        
  old_time = traffic_element["current time"]
  delta_time = current_time - old_time
  current_position_x = traffic_element["position x"]
  current_position_y = traffic_element["position y"]
  target_x = traffic_element["target x"]
  target_y = traffic_element["target y"]
  delta_x = current_position_x - target_x
  delta_y = current_position_y - target_y
  distance_remaining = traffic_element["distance remaining"]
  total_distance = traffic_element["distance between milestones"]
  traffic_element["current time"] = current_time
  
  if ((delta_time > 0) and (total_distance > 0)):
    current_speed = traffic_element["speed"]
    distance_moved = delta_time * current_speed
    old_position_x = current_position_x
    old_position_y = current_position_y
    old_distance_remaining = distance_remaining
    distance_remaining = distance_remaining - distance_moved
    if (distance_remaining <= 0):
      distance_remaining = 0
    traffic_element["distance remaining"] = distance_remaining
    fraction_moved = 1.0 - (distance_remaining / total_distance)
    start_x = traffic_element["start x"]
    start_y = traffic_element["start y"]
    target_x = traffic_element["target x"]
    target_y = traffic_element["target y"]
    position_x = start_x + (fraction_moved * (target_x - start_x))
    position_y = start_y + (fraction_moved * (target_y - start_y))
    traffic_element["position x"] = position_x
    traffic_element["position y"] = position_y
    rebuild_shapes (traffic_element)
      
    if (verbosity_level >= 5):  
      print (format_time(current_time) + " " + traffic_element["name"] +
             " in " + place_name(traffic_element) + " from position (" +
             format_location(old_position_x) + ", " +
             format_location(old_position_y) + ") to position (" +
             format_location(traffic_element["position x"]) + ", " +
             format_location(traffic_element["position y"]) + 
             ") distance to next milestone " +
             format_distance(traffic_element["distance remaining"]) +
             " speed " + format_speed(traffic_element["speed"]) +
             " moved " + format_distance(distance_moved) + ".")
    if (do_trace):
      trace_file.write ("Moved from (" + format_location(old_position_x) +
                        ", " + format_location(old_position_y) + ") to (" +
                        format_location(position_x) + ", " +
                        format_location(position_y) + ") in " +
                        format_time(delta_time) + ".\n")
      pprint.pprint (traffic_element, trace_file)
      
    # Undo the move if we are blocked.
    blocking_traffic_element_name = check_blocked(traffic_element)
    if (blocking_traffic_element_name != None):
      # We are blocked.
      traffic_element["position x"] = old_position_x
      traffic_element["position y"] = old_position_y
      traffic_element["distance remaining"] = old_distance_remaining
      traffic_element["blocker name"] = blocking_traffic_element_name
      if (traffic_element["speed"] > 0):
        traffic_element["old speed"] = traffic_element["speed"]
      traffic_element["speed"] = 0
      if (verbosity_level >= 3):  
        print (format_time(current_time) + " " + traffic_element["name"] +
               " in " + place_name(traffic_element) + " at position (" +
               format_location(traffic_element["position x"]) + ", " +
               format_location(traffic_element["position y"]) +
               " ) distance to next milestone  " +
               format_distance(traffic_element["distance remaining"]) +
               " is blocked by " + blocking_traffic_element_name + ".")
      if ((table_level >= 3) and (current_time > table_start_time)):
        table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                          traffic_element["current lane"] + " & " +
                          cap_first_letter(traffic_element["name"]) +
                          " is blocked by " +
                          blocking_traffic_element_name + ". \\\\\n")
        
      if (do_events_output):
        write_event(traffic_element, "blocked")
                           
      return
    
    no_activity = False
  if (distance_remaining == 0):
    # We have reached the next milestone.
    this_milestone_index = traffic_element["milestone index"]
    next_milestone_index = this_milestone_index + 1
    following_milestone_index = next_milestone_index + 1
    milestone_list = traffic_element["milestones"]
    if ((verbosity_level >= 5) and (traffic_element["speed"] != 0)):        
      print (format_time(current_time) + " " + traffic_element["name"] +
             " in " + place_name(traffic_element) + " at position (" +
             format_location(traffic_element["position x"]) + ", " +
             format_location(traffic_element["position y"]) +
             ") (milestone " + str(next_milestone_index) + " of " +
             str(len(milestone_list)) + ") speed " +
             format_speed(traffic_element["speed"]) + ".")
    if (following_milestone_index >= len(milestone_list)):
      # We have reached the last milestone.
      traffic_element["present"] = False
      traffic_element["shape"] = None
      if (verbosity_level >= 2):
        print (format_time(current_time) + " " +
               traffic_element["name"] +
               " in " + place_name(traffic_element) +
               " exits the simulation at position (" +
               format_location(traffic_element["position x"]) + ", " +
               format_location(traffic_element["position y"]) + ").")
      if ((table_level >= 2) and (current_time > table_start_time)):
        table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                          traffic_element["current lane"] + " & " +
                          cap_first_letter(traffic_element["name"]) +
                          " exits the simulation. \\\\\n")
      if (do_events_output):
        write_event (traffic_element, "exiting")
      
      no_activity = False
    else:
      # There is a milestone after the next one.
      this_milestone = milestone_list[this_milestone_index]
      next_milestone = milestone_list[next_milestone_index]
      following_milestone = milestone_list[following_milestone_index]
      
      # Check for changing lanes
      current_lane = traffic_element["current lane"]
      if (next_milestone[0] != current_lane):
        # We cannot enter the intersection or crosswalk if the light is red.
        if (not can_change_lanes (traffic_element)):
          if (traffic_element["speed"] != 0):
            traffic_element["speed"] = 0
            traffic_element["was stopped"] = True
            traffic_element["stopped time"] = current_time

            if (verbosity_level >= 2):
              print (format_time(current_time) + " " +
                     traffic_element["name"] +
                     " in " + place_name(traffic_element) +
                     " at position (" +
                     format_location(traffic_element["position x"]) +
                     ", " +
                     format_location(traffic_element["position y"]) +
                     ") distance to next milestone " +
                     format_distance(
                       traffic_element["distance remaining"]) +
                     " stopped.")
            if ((table_level >= 2) and (current_time > table_start_time)):
              table_file.write ("\\hline " + format_time_N(current_time) +
                                " & " + traffic_element["current lane"] +
                                " & " +
                                cap_first_letter(traffic_element["name"]) +
                                " stopped. \\\\\n")
            if (do_events_output):
              write_event (traffic_element, "stopped")
              
            no_activity = False
        else:
          # We are allowed to enter this lane.
          match next_milestone[0]:
            case "crosswalk" | "intersection":
              if (verbosity_level >= 2):
                print (format_time(current_time) + " " +
                       traffic_element["name"] +
                       " in " + place_name(traffic_element) +
                       " enters the " + next_milestone[0] +
                       " at position (" +
                       format_location(traffic_element["position x"]) + ", " +
                       format_location(traffic_element["position y"]) + ").")
            
              if ((table_level >= 2) and (current_time > table_start_time)):
                table_file.write ("\\hline " + format_time_N(current_time) +
                                  " & " + traffic_element["current lane"] +
                                  " & " +
                                  cap_first_letter(traffic_element["name"]) +
                                  " enters the " + next_milestone[0] +
                                  ". \\\\\n")
              
              new_milestone (traffic_element)

              if (do_trace):
                trace_file.write ("Entering " + next_milestone[0] + ":\n")
                pprint.pprint (traffic_element, trace_file)
                
              if (do_events_output):
                write_event (traffic_element, "entering")
                
              no_activity = False
              
            case _:
              # Changing lanes but not into the intersection or crosswalk
              old_lane = traffic_element["current lane"]
              new_milestone (traffic_element)
          
              match old_lane:
                case "intersection" | "crosswalk":
                  tail_text = " leaves the " + old_lane
                case _:
                  tail_text = " leaves lane " + old_lane
              
              if (verbosity_level >= 2):
                print (format_time(current_time) + " " +
                       traffic_element["name"] +
                       " in " + place_name(traffic_element) +
                       " at position (" +
                       format_location(traffic_element["position x"]) + ", " +
                       format_location(traffic_element["position y"]) + 
                       ") distance to next milestone " +
                       format_distance(traffic_element["distance remaining"]) +
                       " speed " + format_speed(traffic_element["speed"]) +
                       tail_text + ".")
              if ((table_level >= 2) and (current_time > table_start_time)):
                table_file.write ("\\hline " + format_time_N(current_time) +
                                  " & " + traffic_element["current lane"] +
                                  " & " +
                                  cap_first_letter(traffic_element["name"]) +
                                  tail_text + ". \\\\\n")
              if (do_trace):
                trace_file.write ("Changing lane from " + old_lane + ":\n")
                pprint.pprint (traffic_element, trace_file)
            
              if (do_events_output):
                write_event (traffic_element, "changing lane")

              no_activity = False
      else:
        # Not changing lanes
        new_milestone (traffic_element)

        if (verbosity_level >= 5):
          print (format_time(current_time) + " " +
                 traffic_element["name"] +
                 " in " + place_name(traffic_element) + " at position (" +
                 format_location(traffic_element["position x"]) + ", " +
                 format_location(traffic_element["position y"]) +
                 ") speed " + format_speed(traffic_element["speed"]) +
                 " at a milestone.")
        if ((table_level >= 5) and (current_time > table_start_time)):
          table_file.write ("\\hline " + format_time_N(current_time) +
                            " & " + traffic_element["current lane"] +
                            " & " +
                            cap_first_letter(traffic_element["name"]) +
                            " at position (" +
                            format_location(traffic_element["position x"]) +
                            ", " +
                            format_location(traffic_element["position y"]) +
                            ") at a milestone. \\\\\n")
        no_activity = False

        if (do_trace):
          trace_file.write ("Reached milestone:\n")
          pprint.pprint (traffic_element, trace_file)

        if (do_events_output):
            write_event (traffic_element, "reaching milestone")
            
  return

# Subroutine to activate any sensors that detect a traffic element.
def check_sensors():
  for signal_face in signal_faces_list:
    signal_face_name = signal_face["name"]
    sensors = signal_face["sensors"]
    for sensor_name in sensors:
      sensor = sensors[sensor_name]
      if ("shape" in sensor):
        triggered = False
        for traffic_element_name in traffic_elements:
          traffic_element = traffic_elements[traffic_element_name]
          if (check_overlap_sensor (traffic_element, sensor)):
            triggered = True
            sensor["triggered by"] = traffic_element["name"]
        if (not sensor["controlled by script"]):
          if (sensor["value"] != triggered):
            sensor["value"] = triggered
            if (verbosity_level >= 2):
              print (format_time(current_time)  + " sensor " +
                     signal_face["name"] + "/" + sensor_name + " set to " +
                     str(sensor["value"]) + " by " + sensor["triggered by"] +
                     ".")
            if ((table_level >= 2) and (current_time > table_start_time)):
              table_file.write ("\\hline " + format_time_N(current_time) +
                                " & " + signal_face ["name"] + " & Sensor " +
                                sensor_name + " set to " +
                                str(sensor["value"]) + " by " +
                                sensor["triggered by"] + ". \\\\\n")
            
  return
            
  
def timer_state (signal_face, timer_name):
  timers_list = signal_face["timers"]
  for the_timer in timers_list:
    if (the_timer["name"] == timer_name):
      return the_timer["state"]

# Execute an action from the script.
def perform_script_action (the_operator, signal_face_name, the_operand,
                           permissive_delay):
  for signal_face in signal_faces_list:
    if ((signal_face["name"] == signal_face_name) or
        (signal_face_name == "all")):
      match the_operator:
        case "set toggle":
          set_toggle_value (signal_face, the_operand, True, "script")
        case "sensor on" | "sensor off":
          sensor_name = the_operand
          sensors = signal_face["sensors"]
          sensor = sensors[sensor_name]
          sensor["controlled by script"] = True

          if (the_operator == "sensor on"):
            sensor ["value"] = True
          else:
            sensor ["value"] = False
            
          if (verbosity_level >= 2):
            print (format_time(current_time)  + " sensor " +
                   signal_face["name"] + "/" + sensor_name + " set to " +
                   str(sensor["value"]) + " by script.")
          if ((table_level >= 2) and (current_time > table_start_time)):
            table_file.write ("\\hline " + format_time_N(current_time) +
                              " & " + signal_face ["name"] + " & Sensor " +
                              sensor_name + " set to " + str(sensor["value"]) +
                              " by script. \\\\\n")
            
        case "car" | "truck" | "pedestrian":
          add_traffic_element (the_operator, the_operand, permissive_delay)
          
  return

# Update the timers to the current time.
def update_timers():
  global no_activity
  
  remove_timers = list()
  if (verbosity_level >= 5):
    active_timer_list = ""
    for the_timer in running_timers:
      active_timer_list = (active_timer_list + " " +
                           the_timer["signal face name"] + "/" +
                           the_timer["name"])
    print (format_time(current_time) + " Active timers: " + active_timer_list +
           ".")
    
  for the_timer in running_timers:
    the_timer["remaining time"] = the_timer["completion time"] - current_time
    if (verbosity_level >= 5):
      print (format_time(current_time) + " timer " +
             the_timer ["signal face name"] + "/" + the_timer["name"] +
             " has " + format_time(the_timer["remaining time"]) +
             " remaining.")
    if ((the_timer ["state"] == "running") and
        (the_timer["remaining time"] <= 0)):
      the_timer["state"] = "completed"
      remove_timers.append(the_timer)
      no_activity = False
      if (verbosity_level >= 5):
        print (format_time(current_time) + " timer " +
               the_timer ["signal face name"] + "/" + the_timer["name"] +
               " completed.")
      if ((table_level >= 5) and (current_time > table_start_time)):          
        table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                          the_timer ["signal face name"] + " & Timer " +
                          the_timer ["name"] + " completed. \\\\\n")

  if ((verbosity_level >= 5) and (len(remove_timers) > 0)):
    remove_timers_list = ""

    for the_timer in remove_timers:
      remove_timers_list = (remove_timers_list + " " +
                            the_timer["signal face name"] + "/" +
                            the_timer["name"])
    print (format_time(current_time) + " Timers being removed: " +
           remove_timers_list + ".")
    
  for the_timer in remove_timers:
    running_timers.remove(the_timer)

  if ((verbosity_level >= 5) and (len(remove_timers) > 0)):
    active_timer_list = ""
    for the_timer in running_timers:
      active_timer_list = (active_timer_list + " " +
                           the_timer["signal face name"] + "/" +
                           the_timer["name"])
    print (format_time(current_time) + " Remaining active timers: " +
           active_timer_list + "(" + str(len(running_timers)) + ").")
    
  return

# Find the next timer completion time.
def find_next_timer_completion_time():
  next_timer_completion_time = None
  for the_timer in running_timers:
    if (next_timer_completion_time == None):
      next_timer_completion_time = the_timer["completion time"]
    else:
      if (the_timer["completion time"] < next_timer_completion_time):
        next_timer_completion_time = the_timer["completion time"]
  return (next_timer_completion_time)

# Find the time of the next action in the script.
def find_next_script_action_time():
  next_script_action_time = None
  for the_action in script_set:
    the_time = the_action[0]
    if (next_script_action_time == None):
      next_script_action_time = the_time
    else:
      if (the_time < next_script_action_time):
        next_script_action_time = the_time
  return (next_script_action_time)

# Find the next traffic element time.
# TODO
def find_next_traffic_element_time():
  min_time = end_time
  for traffic_element_name in traffic_elements:
    traffic_element = traffic_elements[traffic_element_name]
    if (traffic_element["present"]):
      return (current_time + fractions.Fraction(1, 1000))
  return (None)

# Main loop
while ((current_time < end_time) and (error_counter == 0)):

  if (verbosity_level >= 5):
    print (format_time(current_time) + " top of simulation loop.")

  # Run the state machines.
  for signal_face in signal_faces_list:
    # If we are starting up enter state Red substate Walting for Clearance.
    if ("state" not in signal_face):
      enter_state (signal_face, "Red", "Waiting for Clearance")
    state_name = signal_face["state"]
    substate_name = signal_face["substate"]

    # Test for exiting the current state.
    new_state_name = None
    new_substate_name = None
    found_exit = None
    states = finite_state_machine["states"]
    state = states[state_name]
    substate = None
    for the_substate in state:
      if (the_substate["name"] == substate_name):
        substate = the_substate
        break
    if (verbosity_level >= 5):
      print (format_time(current_time) + " Signal face " +
             signal_face["name"] + " state " + signal_face["state"] +
             " substate " + substate["name"] + " evaluating exits.")
    for the_exit in substate["exits"]:
      conditionals = the_exit [0]
      conditions_all_true = True
      for conditional in conditionals:
        match conditional[0]:
          case "toggle is true":
            toggle_name = conditional[1]
            if (verbosity_level >= 5):
              print (format_time(current_time) + " Testing toggle " +
                     signal_face["name"] + "/" + toggle_name + " for True.")
            if (not toggle_value(signal_face, toggle_name)):
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + toggle_name +
                       " is false.")
              conditions_all_true = False
            else:
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + toggle_name +
                       " is true.")
                
          case "toggle is false":
            toggle_name = conditional[1]
            if (verbosity_level >= 5):
              print (format_time(current_time) + " Testing toggle " +
                     signal_face["name"] + "/" + toggle_name + " for False.")
            if (toggle_value(signal_face, toggle_name)):
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + toggle_name +
                       " is true.")
              conditions_all_true = False
            else:
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + toggle_name +
                       " is false.")
                
          case "timer is completed":
            timer_name = conditional[1]
            if (verbosity_level >= 5):
              print (format_time(current_time) + " Testing timer " +
                     signal_face["name"] + "/" + timer_name +
                     " for being complete.")
            if (timer_state (signal_face, timer_name) != "completed"):
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + timer_name +
                       " is not complete.")
              conditions_all_true = False
            else:
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + timer_name +
                       " has completed.")
                
          case "timer not complete":
            timer_name = conditional[1]
            if (verbosity_level >= 5):
              print (format_time(current_time) + " Testing timer " +
                     signal_face["name"] + "/" + timer_name +
                     " for being not complete.")
            if (timer_state (signal_face, timer_name) == "completed"):
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + timer_name +
                       " has completed.")
              conditions_all_true = False
            else:
              if (verbosity_level >= 5):
                print (format_time(current_time) + "  " + timer_name +
                       " has not completed.")

          case _:
            print ("Unknown condition test: " + conditional[0] + ".")
            error_counter = error_counter + 1
            
      if (conditions_all_true):
        found_exit = the_exit
        break
      
    if (found_exit != None):
      new_state_name = found_exit[1]
      new_substate_name = found_exit[2]
      enter_state (signal_face, new_state_name, new_substate_name)
      
  
  # Run the system programs.
  green_request_granted()
  clearance_requested()
  partial_clearance_requested()
  conflicting_paths_are_clear()
  partial_conflicting_paths_are_clear()
  safety_check()
    
  # Run any ripe actionss in the script.
  to_remove = set()
  for the_action in script_set:
    the_time = the_action[0]
    the_operator = the_action[1]
    signal_face_name = the_action[2]
    the_operand = the_action[3]
    permissive_delay = the_action[4]
    if (the_time <= current_time):
      perform_script_action (the_operator, signal_face_name, the_operand,
                             permissive_delay)
      to_remove.add(the_action)
      no_activity = False
      
  for the_action in to_remove:
    script_set.remove(the_action)

  # See if any vehicles or pedestrians are activating any sensors
  check_sensors()
    
  # If there are active sensors, set their corresponding toggles.
  for signal_face in signal_faces_list:
    sensors = signal_face ["sensors"]
    for sensor_name in sensors:
      sensor = sensors[sensor_name]
      if (sensor ["value"]):
        if (verbosity_level >= 5):
          print (format_time(current_time) + " sensor " +
                 signal_face ["name"] + "/" + sensor ["name"] +
                 " remains True.")

        toggle_names = sensor["toggles"]
        for toggle_name in toggle_names:
          exploded_toggle_name = toggle_name.partition("/")
          if (exploded_toggle_name[1] == ""):
            toggle_signal_face_name = signal_face["name"]
            root_toggle_name = toggle_name
          else:
            toggle_signal_face_name = exploded_toggle_name[0]
            root_toggle_name = exploded_toggle_name[2]

          toggle_signal_face = signal_faces_dict[toggle_signal_face_name]
          if (not toggle_value (toggle_signal_face, root_toggle_name)):
            if (verbosity_level >= 5):
              print (format_time(current_time) + " Sensor " +
                     signal_face ["name"] + "/" + sensor_name + " is True.")
            if ((table_level >= 5) and (current_time > table_start_time)):
              table_file.write ("\\hline " + format_time_N(current_time) +
                                " & " + signal_face["name"] +
                                " &  Sensor " + sensor_name +
                                " is True. \\\\\n")
            set_toggle_value (toggle_signal_face, root_toggle_name, True,
                              "sensor " + signal_face["name"] + "/" +
                              sensor_name)
            no_activity = False          
        
  # Update the positions of the cars, trucks and pedestrians.
  for traffic_element_name in traffic_elements:
    traffic_element = traffic_elements[traffic_element_name]
    if (traffic_element["present"]):
      move_traffic_element(traffic_element)
        
  # Update the timers.
  update_timers()
  
  # We only update the clock if there is no activity.
  if (no_activity):
    next_timer_completion_time = find_next_timer_completion_time()
    next_script_action_time = find_next_script_action_time()
    next_traffic_element_time = find_next_traffic_element_time()

    # If there are no timers running, no script actions waiting to run
    # and no traffic elements present then we are done.
    if ((next_timer_completion_time == None) and
        (next_script_action_time == None) and
        (next_traffic_element_time == None)):
      break

    # Otherwise we advance the clock to the next significant event.
    next_clock_time = end_time
    if ((next_timer_completion_time != None) and
        (next_timer_completion_time < next_clock_time)):
      next_clock_time = next_timer_completion_time
    if ((next_script_action_time != None) and
        (next_script_action_time < next_clock_time)):
      next_clock_time = next_script_action_time
    if ((next_traffic_element_time != None) and
        (next_traffic_element_time < next_clock_time)):
      next_clock_time = next_traffic_element_time

    if (do_trace):
      trace_file.write ("Advance clock from " + format_time(current_time) +
                        " to " + format_time(next_clock_time) + ".\n")
      
    current_time = next_clock_time
  else:
    no_activity = True
  
if (do_trace):
  trace_file.write ("Ending Signal Faces:\n")
  pprint.pprint (signal_faces_list, trace_file)

 # If requested, also print the maximum wait times.
if (print_statistics and (verbosity_level >= 1)):
  for signal_face in signal_faces_list:
    if ("max wait time" in signal_face):
      print (format_time(current_time) + " signal face " +
             signal_face["name"] + " maximum wait " +
             format_time(signal_face["max wait time"]) + " at " +
             format_time(signal_face["max wait start"]) + ".")
  
if (do_table_output):
  table_file.write ("\\hline \\end{longtable}\n")
  table_file.close()

# If requested, output the time of the last event, rounded up
# to the nearest second.
if (do_last_event_time_output):
  last_event_time_file = open (last_event_time_file_name, "w")
  last_event_time_file.write (str(int(last_event_time) + 1) + "\n")
  last_event_time_file.close()
  
if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file run_simulation.py
