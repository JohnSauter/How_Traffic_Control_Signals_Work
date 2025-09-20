#!/usr/bin/python3
# -*- coding: utf-8
#
# display_intersection.py displays information about an intersection.

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
import pathlib
import json
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Display information about an intersection.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='display_intersection 0.53 2025-09-15',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('intersection-file', metavar='intersection_file',
                     help='read the intersection description from this ' +
                     'JSON file.')
parser.add_argument ('--lamp-map-file', metavar='lamp_map_file',
                     help='write the lamp map as a LaTex table')
parser.add_argument ('--sensor-map-file', metavar='sensor_map_file',
                     help='write the sensor map as a LaTex table')
parser.add_argument ('--timer-durations-file', metavar='timer_durations_file',
                     help='write the timer durations as a LaTex table')
parser.add_argument ('--table-label', metavar='table_label',
                     help='label the table with this label')
parser.add_argument ('--only-important', action="store_true",
                     help='only output important timers')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_intersection = False
do_lamp_map_output = False
do_sensor_map_output = False
do_timer_durations_output = False
have_table_label = False
table_label = None
only_important = False
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

if (arguments ['intersection-file'] != None):
  do_intersection = True
  intersection_file_name = arguments ['intersection-file']
  intersection_file_name = pathlib.Path(intersection_file_name)

if (arguments ['lamp_map_file'] != None):
  do_lamp_map_output = True
  lamp_map_file_name = arguments ['lamp_map_file']
  lamp_map_file_name = pathlib.Path(lamp_map_file_name)

if (arguments ['sensor_map_file'] != None):
  do_sensor_map_output = True
  sensor_map_file_name = arguments ['sensor_map_file']
  sensor_map_file_name = pathlib.Path(sensor_map_file_name)

if (arguments ['timer_durations_file'] != None):
  do_timer_durations_output = True
  timer_durations_file_name = arguments ['timer_durations_file']
  timer_durations_file_name = pathlib.Path(timer_durations_file_name)

if (arguments ['table_label'] != None):
  have_table_label = True
  table_label = arguments ['table_label']

if (arguments ['only_important'] != None):
  only_important = arguments ['only_important']
  
if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

if (do_intersection):
  intersection_file = open (intersection_file_name, 'r')
  intersection_info = json.load (intersection_file)
  intersection_file.close()

signal_faces_list = intersection_info ["signal faces"]
finite_state_machine = intersection_info ["finite state machine"]
timer_names = finite_state_machine ["timer names"]

if (do_lamp_map_output):
  lamp_map_file = open (lamp_map_file_name, 'w')
  lamp_map_file.write ("\\begin{longtable}{P{1.0cm} | P{5cm} | P{5cm}}\n")
  lamp_map_file.write ("  \\caption{Lamp Wiring}")
  if (have_table_label):
    lamp_map_file.write ("\\label{" + table_label + "}")
  lamp_map_file.write ("\\\\\n")
  lamp_map_file.write ("  Signal Face & Signal Face Output Name & " +
                       "Actual Lamp Name \\endfirsthead\n")
  lamp_map_file.write ("  \\caption{Lamp Wiring continued} \\\\\n")
  lamp_map_file.write ("  Signal Face & Signal Face Output Name & " +
                       "Actual Lamp Name \\endhead\n")
  
  for signal_face in signal_faces_list:
    if ("lamp names map" in signal_face):
        lamp_names_map = signal_face["lamp names map"]
        for lamp_name in lamp_names_map:
          lamp_map_file.write("  \\hline " + signal_face["name"] + " & " +
                              lamp_name + " & " + lamp_names_map[lamp_name] +
                              " \\\\\n")

  lamp_map_file.write ("\\hline \\end{longtable}\n")
  lamp_map_file.close()
          
if (do_sensor_map_output):
  sensor_file = open (sensor_map_file_name, 'w')
  sensor_file.write ("\\begin{longtable}{P{1.0cm} | P{4.0cm} | P{6.0cm}}\n")
  sensor_file.write ("  \\caption{Sensor Wiring}")
  if (have_table_label):
    sensor_file.write ("\\label{" + table_label + "}")
  sensor_file.write ("\\\\\n")
  sensor_file.write ("  Signal Face & Sensor & " +
                       "Toggles \\endfirsthead\n")
  sensor_file.write ("  \\caption{Sensor Wiring continued} \\\\\n")
  sensor_file.write ("  Signal Face & Sensor & " +
                       "Toggles \\endhead\n")
  
  for signal_face in signal_faces_list:
    sensors = signal_face["sensors"]
    for sensor_name in sensors:
      sensor = sensors[sensor_name]
      do_write = True
      if (only_important):
        do_write = sensor["important"]
      if (do_write):
        toggles = sensor["toggles"]
        sensor_file.write("   \\hline " + signal_face["name"] + " & " +
                          sensor_name + " &")
        if (len(toggles) == 0):
          sensor_file.write (" not connected ")
        else:
          first_toggle = True
          for toggle_name in toggles:
            if (not first_toggle):
              sensor_file.write (",")
            sensor_file.write (" " + toggle_name)
            first_toggle = False
        sensor_file.write ("\\\\\n")

  sensor_file.write ("\\hline \\end{longtable}\n")
  sensor_file.close()
  
if (do_timer_durations_output):
  timer_durations_file = open (timer_durations_file_name, 'w')
  timer_durations_file.write (
    "\\begin{longtable}{c | c | c}" + "\n")
  timer_durations_file.write ("  \\caption{Timer Durations}")
  if (have_table_label):
    timer_durations_file.write ("\\label{" + table_label + "}")
  timer_durations_file.write ("\\\\\n")
  timer_durations_file.write ("  Signal Face & Timer & Duration " +
                              "\\endfirsthead\n")
  timer_durations_file.write ("  \\caption{Timer Durations continued} \\\\\n")
  timer_durations_file.write ("  Signal Face & Timer & Duration \\endhead\n")
  
  for signal_face in signal_faces_list:
    timers_list = signal_face["timers"]
    for timer in timers_list:
      timer_name = timer["name"]

      do_write = True
      value_is_finite = True
      if (only_important):
        do_write = timer["important"]
      if (timer["duration"] == float("inf")):
        value_is_finite = False
      
      if (do_write):
        timer_durations_file.write ("   \\hline " + signal_face["name"] +
                                    " & " + timer_name + " & ")
        if (value_is_finite):
          timer_durations_file.write ("\\tablenum{" + str(timer["duration"]) +
                                      "}")
        else:
          timer_durations_file.write ("unlimited")
          
        timer_durations_file.write ("\\\\\n")

  timer_durations_file.write ("\\hline \\end{longtable}\n")
  timer_durations_file.close()
  
if (do_trace):
  trace_file.write ("Starting Signal Faces:\n")
  pprint.pprint (signal_faces_list, trace_file)

if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file display_intersection.py
