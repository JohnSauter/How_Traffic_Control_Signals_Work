#!/usr/bin/python3
# -*- coding: utf-8
#
# traffic_control_signals.py implements the control logic for a traffic
# signal using finite state machines.

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
import csv
import shapely
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Implement a traffic control ' + 
               'signal using finite state machines.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='traffic_control_signals 0.30 2025-05-04',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--events-file', metavar='events_file',
                     help='write event output to the specified file')
parser.add_argument ('--table-file', metavar='table_file',
                     help='write LaTeX table output to the specified file' +
                     ' as a LaTex longtable.')
parser.add_argument ('--red-state-file', metavar='red_state_file',
                     help='write the red state description as a LaTex file')
parser.add_argument ('--yellow-state-file', metavar='yellow_state_file',
                     help=('write the yellow state description ' + 
                           'as a LaTex file'))
parser.add_argument ('--green-state-file', metavar='green_state_file',
                     help='write the green state description as a LaTex file')
parser.add_argument ('--lamp-map-file', metavar='lamp_map_file',
                     help='write the lamp map as a LaTex table')
parser.add_argument ('--sensor-map-file', metavar='sensor_map_file',
                     help='write the sensor map as a LaTex table')
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
parser.add_argument ('--waiting-limit', type=int, metavar='waiting_limit',
                     help='max wait time before getting green preference ' +
                     'for turning green; default 60 seconds.')
parser.add_argument ('--print-statistics', type=bool,
                     metavar='print_statistics',
                     help='print statistics about the simulation ' +
                     'default is False.')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_events_output = False
events_file_name = ""
do_table_output = False
table_file_name = ""
do_red_state_output = False
do_yellow_state_output = False
do_green_state_output = False
do_lamp_map_output = False
do_sensor_map_output = False
table_level = 0
end_time = decimal.Decimal ('0.000')
table_start_time  = decimal.Decimal ('-1.000')
table_caption = "no caption"
do_script_input = False
script_input_file = ""
do_last_event_time_output = False
waiting_limit = 60
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

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_file_name = arguments ['trace_file']
  trace_file_name = pathlib.Path(trace_file_name)
  trace_file = open (trace_file_name, 'w')

if (arguments ['events_file'] != None):
  do_events_output = True
  events_file_name = arguments ['events_file']
  events_file_name = pathlib.Path(events_file_name)

if (arguments ['table_file'] != None):
  do_table_output = True
  table_file_name = arguments ['table_file']
  table_file_name = pathlib.Path(table_file_name)

if (arguments ['red_state_file'] != None):
  do_red_state_output = True
  red_state_output_file_name = arguments ['red_state_file']
  red_state_output_file_name = pathlib.Path(red_state_output_file_name)

if (arguments ['yellow_state_file'] != None):
  do_yellow_state_output = True
  yellow_state_output_file_name = arguments ['yellow_state_file']
  yellow_state_output_file_name = pathlib.Path(yellow_state_output_file_name)

if (arguments ['green_state_file'] != None):
  do_green_state_output = True
  green_state_output_file_name = arguments ['green_state_file']
  green_state_output_file_name = pathlib.Path(green_state_output_file_name)

if (arguments ['lamp_map_file'] != None):
  do_lamp_map_output = True
  lamp_map_file_name = arguments ['lamp_map_file']
  lamp_map_file_name = pathlib.Path(lamp_map_file_name)

if (arguments ['sensor_map_file'] != None):
  do_sensor_map_output = True
  sensor_map_file_name = arguments ['sensor_map_file']
  sensor_map_file_name = pathlib.Path(sensor_map_file_name)

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

if (arguments ['waiting_limit'] != None):
  waiting_limit = arguments ['waiting_limit']

if (arguments ['print_statistics'] != None):
  print_statistics = arguments ['print_statistics']

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

start_time = decimal.Decimal("0.000")
current_time = fractions.Fraction(start_time)
last_event_time = current_time

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

  
# Construct the template finite state machine.  This template
# contains the states, actions and transitions.  All of the signal
# faces use it.

finite_state_machine = dict()

red_state = list()

substate = dict()
substate["name"] = "Waiting for Clearance"
substate["actions" ] = list()
actions_list = substate["actions"]
action = ("set lamp", "Steady Circular Red")
actions_list.append(action)
action = ("start timer", "Red Clearance")
actions_list.append(action)
action = ("start timer", "Red Limit")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]
conditional_tests = list()
conditional_test = ("timer is completed", "Red Clearance")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear" )
exits_list.append(exit)
red_state.append(substate)

substate = dict()
substate["name"] = "Travel Path is Clear"
substate["actions"] = list()
actions_list = substate["actions"]
action=("set toggle", "Cleared")
actions_list.append(action)
action = ("clear toggle", "Clearance Requested")
actions_list.append(action)
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ( "clear toggle", "Traffic Flowing" )
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)
action = ("clear toggle", "Preempt Red")
actions_list.append(action)
action = ("clear toggle", "Manual Red")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]
conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Going Green 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Going Green 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Going Green 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Red Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Flashing" )
exits_list.append(exit)
red_state.append(substate)

substate = dict()
substate["name"] = "Going Green 1"
substate["actions"] = list()
actions_list = substate["actions"]
action=("set toggle", "Request Green")
actions_list.append(action)
action=("clear toggle", "Traffic Present")
actions_list.append(action)
action=("clear toggle", "Traffic Approaching")
actions_list.append(action)
substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Green Request Granted")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 2" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Green Request Granted")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 1" )
exits_list.append(exit)

red_state.append(substate)

substate=dict()
substate["name"] = "Going Green 2"
substate["actions"] = list()
actions_list = substate["actions"]
action=("clear toggle", "Request Green")
actions_list.append(action)
action = ("set toggle", "Request Partial Clearance")
actions_list.append(action)
substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Partial Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Minimum Green" )
exits_list.append(exit)
red_state.append(substate)

substate = dict()
substate["name"] = "Flashing"
substate["actions"] = list()
actions_list = substate["actions"]
action=("set lamp", "Flashing Circular Red")
actions_list.append(action)
action=("clear toggle", "Flash Red")
actions_list.append(action)
substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is false", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Waiting for Clearance" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Flashing" )
exits_list.append(exit)

red_state.append(substate)

finite_state_machine["Red"] = red_state

green_state = list()
substate = dict()
substate["name"] = "Minimum Green"
substate["actions"] = list()
actions_list = substate["actions"]
action=("set lamp", "Steady Circular Green")
actions_list.append(action)
action = ("clear toggle", "Cleared")
actions_list.append(action)
action = ("clear toggle", "Request Partial Clearance")
actions_list.append(action)
action = ("clear toggle", "Request Clearance")
actions_list.append(action)
action = ("start timer", "Minimum Green")
actions_list.append(action)
action = ("start timer", "Maximum Green")
actions_list.append(action)
action = ("set toggle", "Traffic Flowing")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ( "toggle is false", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)
green_state.append(substate)

substate = dict()
substate["name"] = "Looking for Gap"
substate["actions"] = list()
actions_list = substate["actions"]
action = ("start timer", "Passage")
actions_list.append(action)
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
actions_list.append(action)
action = ("clear toggle", "Manual Green")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Maximum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Green", "Waiting for Clearance Request")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Waiting for Clearance Request"
substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Preempt Green")
actions_list.append(action)
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("start timer", "Maximum Green")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap" )
exits_list.append(exit)

conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

green_state.append(substate)

finite_state_machine["Green"] = green_state

yellow_state = list()
substate = dict()
substate["name"] = "Going Red"
substate["actions"] = list()
actions_list = substate["actions"]
action=("set lamp", "Steady Circular Yellow")
actions_list.append(action)
action = ("clear toggle", "Cleared")
actions_list.append(action)
action = ("start timer", "Yellow Change")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("timer is completed", "Yellow Change")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Waiting for Clearance" )
exits_list.append(exit)

yellow_state.append(substate)

substate = dict()
substate["name"] = "Left Flashing 1"
substate["actions"] = list()
actions_list = substate["actions"]
action = ("set lamp", "Flashing Left Arrow Yellow")
actions_list.append(action)
action = ("clear toggle", "Cleared")
actions_list.append(action)
action = ("set toggle", "Traffic Flowing")
actions_list.append(action)
action = ("start timer", "Minimum Left Flashing Yellow")
actions_list.append(action)
action = ("start timer", "Left Flashing Yellow Waiting")
actions_list.append(action)
action = ("start timer", "Green Limit")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Minimum Left Flashing Yellow")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Left Flashing 2")
exits_list.append(exit)

yellow_state.append(substate)

substate = dict()
substate["name"] = "Left Flashing 2"
substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Green", "Minimum Green")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer not complete", "Left Flashing Yellow Waiting")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 2" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer not complete", "Left Flashing Yellow Waiting")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 2" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Left Flashing Yellow Waiting")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Left Flashing Yellow Waiting")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Green" )
exits_list.append(exit)

yellow_state.append(substate)

substate = dict()
substate["name"] = "Flashing"
substate["actions"] = list()
actions_list = substate["actions"]
action = ("set lamp", "Flashing Circular Yellow")
actions_list.append(action)
action = ("clear toggle", "Flash Yellow")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is false", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Waiting for Clearance" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Flashing" )
exits_list.append(exit)


yellow_state.append(substate)

substate = dict()
substate["name"] = "Going Green"
substate["actions"] = list()
actions_list = substate["actions"]
action = ("set toggle", "Request Clearance")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Minimum Green" )
exits_list.append(exit)

yellow_state.append(substate)

finite_state_machine["Yellow"] = yellow_state

if (do_trace):
  trace_file.write ("Finite State Machine template:\n")
  pprint.pprint (finite_state_machine, trace_file)
  trace_file.write ("\n")

#
# Write out the finite state machine template for the documentation.
#
def cap_first_letter (the_string):
  return (the_string[0].upper() + the_string[1:])

def write_out_state (the_state, output_file_name):
  output_file = open (output_file_name, 'w')
  output_file.write ("\\begin{description}[style=standard]\n")

  for substate in the_state:
    if (do_trace):
      trace_file.write ("Writing out substate " + substate ["name"] + ".\n")
    substate_name = substate["name"]
    output_file.write ("\\item [Substate] " + substate_name + "\n")
    output_file.write ("  \\begin{description}\n")
    
    actions = substate["actions"]
    output_file.write ("  \\item [Entry Actions]\n")
    output_file.write ("    \\begin{itemize}\n")
    output_file.write ("    \\item[\\relax]\n")
    
    for action in actions:
      output_file.write ("    \\item " + cap_first_letter(action[0]) +
                         " " + action[1] + ".\n")  
    output_file.write ("    \\end{itemize}\n")

    exits = substate["exits"]
    output_file.write ("  \\item [Exits]\n")
    output_file.write ("    \\begin{itemize}\n")
    output_file.write ("    \\item[\\relax]\n")
    for exit in exits:
      output_file.write ("    \\item\n")
      output_file.write ("      \\begin{description}\n")
      clauses = exit[0]
      first_clause = True
      for clause in clauses:
        if (first_clause):
          output_file.write ("      \\item [condition:] " + clause[0] + " " +
                             clause[1] + "\n")
        else:
          output_file.write ("      \\item [and:] " + clause[0] + " " +
                             clause[1] + "\n")
        first_clause = False
      output_file.write ("      \\item [destination:] State " + exit[1] +
                         " Substate " + exit[2] + "\n")
      output_file.write ("      \\end{description}\n")
    output_file.write ("    \\end{itemize}\n")
    output_file.write ("  \\end{description}\n")

  output_file.write ("\\end{description}\n")
  output_file.close()

if (do_red_state_output):
  write_out_state (red_state, red_state_output_file_name)

if (do_green_state_output):
  write_out_state (green_state, green_state_output_file_name)

if (do_yellow_state_output):
  write_out_state (yellow_state, yellow_state_output_file_name)

# Build the finite state machines for the signal faces:

signal_face_names = ( "A", "psw", "pse", "B", "C", "D", "E", "pnw", "pne",
                      "F", "G", "H", "J" )

toggle_names = ( "Clearance Requested", "Cleared",
                 "Conflicting Paths are Clear", "Flash Red", "Flash Yellow",
                 "Green Request Granted",
                 "Manual Green", "Manual Red",
                 "Partial Conflicting Paths are Clear", "Preempt Green",
                 "Preempt Red", "Request Clearance", "Request Green Granted",
                 "Request Green", "Request Partial Clearance",
                 "Traffic Approaching", "Traffic Flowing", "Traffic Present" )
timer_names = ( "Left Flashing Yellow Waiting", "Red Limit",
                "Minimum Left Flashing Yellow", "Maximum Green",
                "Minimum Green", "Passage", "Red Clearance", "Green Limit",
                "Yellow Change" )

# Set the duration of each timer in each signal face.

timer_durations = dict()

for signal_face_name in ("A", "psw", "pse", "D", "E", "pnw", "pne", "H", "J"):
  timer_full_name = signal_face_name + "/" + "Red Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("inf")

for signal_face_name in ("B", "C", "F", "G"):
  timer_full_name = signal_face_name + "/" + "Red Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("60.000")
  timer_full_name = signal_face_name + "/" + "Maximum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("60.000")
  timer_full_name = signal_face_name + "/" + "Minimum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("12.000")
  timer_full_name = signal_face_name + "/" + "Passage"
  timer_durations[timer_full_name] = decimal.Decimal ("3.500")
  timer_full_name = signal_face_name + "/" + "Red Clearance"
  timer_durations[timer_full_name] = decimal.Decimal ("1.000")
  timer_full_name = signal_face_name + "/" + "Green Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("inf")
  timer_full_name = signal_face_name + "/" + "Yellow Change"
  timer_durations[timer_full_name] = decimal.Decimal ("5.000")

for signal_face_name in ("A", "E"):
  timer_full_name = signal_face_name + "/" + "Left Flashing Yellow Waiting"
  timer_durations[timer_full_name] = decimal.Decimal ("15.000")
  timer_full_name = signal_face_name + "/" + "Minimum Left Flashing Yellow"
  timer_durations[timer_full_name] = decimal.Decimal ("5.000")
  timer_full_name = signal_face_name + "/" + "Maximum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("20.000")
  timer_full_name = signal_face_name + "/" + "Minimum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("5.000")
  timer_full_name = signal_face_name + "/" + "Passage"
  timer_durations[timer_full_name] = decimal.Decimal ("1.900")
  timer_full_name = signal_face_name + "/" + "Red Clearance"
  timer_durations[timer_full_name] = decimal.Decimal ("1.000")
  timer_full_name = signal_face_name + "/" + "Green Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("60.000")
  timer_full_name = signal_face_name + "/" + "Yellow Change"
  timer_durations[timer_full_name] = decimal.Decimal ("3.500")

for signal_face_name in ("D", "H"):
  timer_full_name = signal_face_name + "/" + "Maximum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("30.000")
  timer_full_name = signal_face_name + "/" + "Minimum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("7.000")
  timer_full_name = signal_face_name + "/" + "Passage"
  timer_durations[timer_full_name] = decimal.Decimal ("1.900")
  timer_full_name = signal_face_name + "/" + "Red Clearance"
  timer_durations[timer_full_name] = decimal.Decimal ("1.500")
  timer_full_name = signal_face_name + "/" + "Green Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("60.000")
  timer_full_name = signal_face_name + "/" + "Yellow Change"
  timer_durations[timer_full_name] = decimal.Decimal ("3.000")

for signal_face_name in ("J"):
  timer_full_name = signal_face_name + "/" + "Maximum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("30.000")
  timer_full_name = signal_face_name + "/" + "Minimum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("7.000")
  timer_full_name = signal_face_name + "/" + "Passage"
  timer_durations[timer_full_name] = decimal.Decimal ("1.900")
  timer_full_name = signal_face_name + "/" + "Red Clearance"
  timer_durations[timer_full_name] = decimal.Decimal ("1.000")
  timer_full_name = signal_face_name + "/" + "Green Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("60.000")
  timer_full_name = signal_face_name + "/" + "Yellow Change"
  timer_durations[timer_full_name] = decimal.Decimal ("3.000")

for signal_face_name in ("pse", "psw", "pne", "pnw"):
  timer_full_name = signal_face_name + "/" + "Maximum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("10.000")
  timer_full_name = signal_face_name + "/" + "Minimum Green"
  timer_durations[timer_full_name] = decimal.Decimal ("6.000")
  timer_full_name = signal_face_name + "/" + "Passage"
  timer_durations[timer_full_name] = decimal.Decimal ("1.000")
  timer_full_name = signal_face_name + "/" + "Red Clearance"
  timer_durations[timer_full_name] = decimal.Decimal ("3.000")
  timer_full_name = signal_face_name + "/" + "Green Limit"
  timer_durations[timer_full_name] = decimal.Decimal ("60.000")
  timer_full_name = signal_face_name + "/" + "Yellow Change"
  timer_durations[timer_full_name] = decimal.Decimal ("19.000")

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
    toggles_list.append(toggle)
  signal_face["toggles"] = toggles_list

  timers_list = list()
  for timer_name in timer_names:
    timer = dict()
    timer["name"] = timer_name
    timer["state"] = "off"
    timer["signal face name"] = signal_face_name
    timer_full_name = signal_face_name + "/" + timer_name
    if timer_full_name in timer_durations:
      timer["duration"] = timer_durations[timer_full_name]
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
    case "A":
      conflict_set = ("psw", "pse", "D", "F", "G", "H", "J")
      partial_conflict_set = ("psw", "pse", "D", "H", "H")
    case "psw" | "pse":
      conflict_set = ("A", "B", "C", "D", "F", "G", "J")
    case "B" | "C":
      conflict_set = ("psw", "pse", "D", "E", "pnw", "pne", "H")
    case "D":
      conflict_set = ("A", "psw", "pse", "B", "C", "E", "pnw", "pne", "F",
                      "G", "H", "J")
    case "E":
      conflict_set = ("B", "C", "D", "pnw", "pne", "H")
      partial_conflict_set = ("D", "pnw", "pne", "H")
    case "pnw" | "pne":
      conflict_set = ("B", "C", "D", "E", "F", "G", "H")
    case "F" | "G":
      conflict_set = ("A", "psw", "pse", "D", "pnw", "pne", "H", "J")
    case "H":
      conflict_set = ("A", "B", "C", "D", "E", "pnw", "pne", "F", "G")
    case "J":
      conflict_set = ("A", "psw", "pse", "D", "F", "G")
      
  if (partial_conflict_set == None):
    partial_conflict_set = conflict_set
  signal_face["conflicts"] = conflict_set
  signal_face["partial conflicts"] = partial_conflict_set

# Limit the time a signal face stays red while it is waiting to
# turn green.  This is a tradeoff between throughput and maximum
# waiting time for a vehicle or pedestrian.

for signal_face in signal_faces_list:
  match signal_face["name"]:
    case "A" | "psw" | "pse" | "D" | "E" | "pnw" | "pne" | "H" | "J":
      signal_face["waiting limit"] = waiting_limit

    case "B" | "C" | "F" | "G":
      signal_face["waiting limit"] = waiting_limit / 2;

# Construct the travel paths.  A traffic element appears at the first
# milestone, then proceeds to each following milestone.  When it reaches
# the last milestone it vanishes from the simulation.
car_length = 15
truck_length = 40
approach_sensor_long_distance = 365
approach_sensor_short_distance = 120
long_lane_length = 528
short_lane_length = 450
very_short_lane_length = 40
lane_width = 12
crosswalk_width = 6

# Subroutine to find the top and bottom of a lane.
# The top is the place where traffic elements stop if they cannot
# enter the intersection from their entrance lane and where traffic elements
# leaving the intersection enter their exit lane.
# The bottom is the other end of the lane, where vehicles enter or leave
# the simulation.

lane_names = ("A", "B", "C", "D", "E", "F", "G", "H", "J", "1", "2", "3", "4",
              "5", "6", "psw", "pse", "pnw", "pne")

def find_lane_info (lane_name):
  global lane_width
  global long_lane_length
  global short_lane_length
  global very_short_lane_length
  
  center_y = 0
  center_x = 0

  match lane_name:
    case "1":
      top_x = center_x - (2.0 * lane_width)
      top_y = center_y + (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + long_lane_length
      
    case "2":
      top_x = center_x - (1.0 * lane_width)
      top_y = center_y + (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + long_lane_length
      
    case "A":
      top_x = center_x - (0.0 * lane_width)
      top_y = center_y + (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + short_lane_length
      
    case "B":
      top_x = center_x + (1.0 * lane_width)
      top_y = center_y + (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + long_lane_length
      
    case "C":
      top_x = center_x + (2.0 * lane_width)
      top_y = center_y + (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y + long_lane_length
      
    case "3":
      top_x = center_x + (5.0 * lane_width)
      top_y = center_y + (0.5 * lane_width)
      bottom_x = top_x + long_lane_length
      bottom_y = top_y
      
    case "D":
      top_x = center_x + (5.0 * lane_width)
      top_y = center_y - (0.5 * lane_width)
      bottom_x = top_x + long_lane_length
      bottom_y = top_y
      
    case "4":
      top_x = center_x + (2.0 * lane_width)
      top_y = center_y - (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - long_lane_length
      
    case "5":
      top_x = center_x + (1.0 * lane_width)
      top_y = center_y - (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - long_lane_length
      
    case "E":
      top_x = center_x + (0.0 * lane_width)
      top_y = center_y - (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - short_lane_length
      
    case "F":
      top_x = center_x - (1.0 * lane_width)
      top_y = center_y - (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - long_lane_length
      
    case "G":
      top_x = center_x - (2.0 * lane_width)
      top_y = center_y - (4.0 * lane_width)
      bottom_x = top_x
      bottom_y = top_y - long_lane_length
      
    case "6":
      top_x = center_x - (5.0 * lane_width)
      top_y = center_y - (1.0 * lane_width)
      bottom_x = top_x - long_lane_length
      bottom_y = top_y
      
    case "H":
      top_x = center_x - (5.0 * lane_width)
      top_y = center_y + (0.0 * lane_width)
      bottom_x = top_x - long_lane_length
      bottom_y = top_y
      
    case "J":
      top_x = center_x - (5.0 * lane_width)
      top_y = center_y + (1.0 * lane_width)
      bottom_x = top_x - very_short_lane_length
      bottom_y = top_y
      
    case "psw":
      top_x = center_x - (4.0 * lane_width)
      top_y = center_y + (3.5 * lane_width)
      bottom_x = top_x - (1.0 * lane_width)
      bottom_y = top_y

    case "pse":
      top_x = center_x + (4.0 * lane_width)
      top_y = center_y + (3.5 * lane_width)
      bottom_x = top_x + (1.0 * lane_width)
      bottom_y = top_y
      
    case "pnw":
      top_x = center_x - (4.0 * lane_width)
      top_y = center_y - (3.5 * lane_width)
      bottom_x = top_x - (1.0 * lane_width)
      bottom_y = top_y

    case "pne":
      top_x = center_x + (4.0 * lane_width)
      top_y = center_y - (3.5 * lane_width)
      bottom_x = top_x + (1.0 * lane_width)
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

intersection_shape = shapely.geometry.box (min_x, min_y, max_x, max_y)
if (do_trace):
  trace_file.write ("Intersection shape:\n")
  pprint.pprint ((min_x, min_y, max_x, max_y), trace_file)
  pprint.pprint (intersection_shape, trace_file)
  
travel_paths = dict()

for entry_lane_name in ("A", "psw", "pse", "B", "C", "D", "E", "pnw", "pne",
                        "F", "G", "H", "J"):
  
  entry_lane_info = find_lane_info(entry_lane_name)
  entry_start_x = entry_lane_info[2]
  entry_start_y = entry_lane_info[3]
  entry_intersection_x = entry_lane_info[0]
  entry_intersection_y = entry_lane_info[1]
  
  match entry_lane_name:
    case "A":
      adjacent_lane_name = "B"
    case "E":
      adjacent_lane_name = "F"
    case "J":
      adjacent_lane_name = "H"
    case _:
      adjacent_lane_name = None

  if (adjacent_lane_name != None):
    adjacent_lane_info = find_lane_info(adjacent_lane_name)
    adjacent_start_x = adjacent_lane_info[2]
    adjacent_start_y = adjacent_lane_info[3]
  
  for exit_lane_name in ("1", "2", "pse", "psw", "3", "4", "5", "pne", "pnw",
                         "6"):

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

    permissive_left_info = None
    permissive_right_info = None
    permissive_distance = 250
    
    match travel_path_name:
      case "A6":
        # Northbound left turn

        milestones = (
          (adjacent_lane_name, adjacent_start_x, adjacent_start_y),
          (adjacent_lane_name, adjacent_start_x, entry_start_y),
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x,
           entry_intersection_y - (2 * car_length)),
          ("intersection", (exit_intersection_x + car_length),
           exit_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_left_shape = shapely.geometry.box (
          entry_intersection_x - (2.5 * lane_width),
          entry_intersection_y - (3 * lane_width) - permissive_distance,
          entry_intersection_x - (0.5 * lane_width), entry_intersection_y)
        permissive_left_info = (("present", permissive_left_shape),)
        
      case "A1" | "A2":
        # Northbound U turn

        milestones = (
          (adjacent_lane_name, adjacent_start_x, adjacent_start_y),
          (adjacent_lane_name, adjacent_start_x, entry_start_y),
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x,
           entry_intersection_y - (2 * car_length)),
          ("intersection", exit_intersection_x,
           exit_intersection_y - car_length),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_left_shape = shapely.geometry.box (
          entry_intersection_x - (2.5 * lane_width),
          entry_intersection_y - (3 * lane_width) - permissive_distance,
          entry_intersection_x - (0.5 * lane_width), entry_intersection_y)
        permissive_left_info = (("present", permissive_left_shape),)
        
      case "E4" | "E5":
        # Southbound U turn

        milestones = (
          (adjacent_lane_name, adjacent_start_x, adjacent_start_y),
          (adjacent_lane_name, adjacent_start_x, entry_start_y),
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x,
           entry_intersection_y + (2 * car_length)),
          ("intersection", exit_intersection_x,
           exit_intersection_y + car_length),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_left_shape = shapely.geometry.box (
          entry_intersection_x + (0.5 * lane_width), entry_intersection_y,
          entry_intersection_x + (2.5 * lane_width),
          entry_intersection_y + (3.0 * lane_width) + permissive_distance)
        permissive_left_info = (("present", permissive_left_shape),)
        
      case "E3":
        # Southbound left turn

        milestones = (
          (adjacent_lane_name, adjacent_start_x, adjacent_start_y),
          (adjacent_lane_name, adjacent_start_x, entry_start_y),
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x,
           entry_intersection_y + (2 * car_length)),
          ("intersection", exit_intersection_x - car_length,
           exit_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_left_shape = shapely.geometry.box (
          entry_intersection_x + (0.5 * lane_width), entry_intersection_y,
          entry_intersection_x + (2.5 * lane_width),
          entry_intersection_y + (3.0 * lane_width) + permissive_distance)
        permissive_left_info = (("present", permissive_left_shape),)
        
      case "B5" | "C4":
        # Northbound through lanes

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

      case "F2" | "G1":
        # Soundbound through lanes

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

      case "C3":
        # Northbound right turn

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x,
           entry_intersection_y - car_length),
          ("intersection", exit_intersection_x - car_length,
           exit_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_right_shape = shapely.geometry.box (
          entry_intersection_x - (lane_width / 2),
          exit_intersection_y - (lane_width / 2),
          exit_intersection_x + (lane_width * 2),
          entry_intersection_y + (lane_width / 2))
                                                       
        permissive_right_info = (("moving East", intersection_shape),
                                 ("present", permissive_right_shape))
      case "G6":
        # Soundbound right turn
        
        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x,
           entry_intersection_y + car_length),
          ("intersection", exit_intersection_x + car_length,
           exit_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_right_shape = shapely.geometry.box (
          exit_intersection_x - (lane_width * 2),
          entry_intersection_y,
          exit_intersection_x + (lane_width * 2),
          exit_intersection_y + (lane_width / 2))
                                                       
        permissive_right_info = (("moving West", intersection_shape),
                                 ("present", permissive_right_shape))
      case "D2" | "D1":
        # Westbound left turn

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x - (2 * car_length),
           entry_intersection_y),
          ("intersection", exit_intersection_x,
           exit_intersection_y - car_length),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

      case "D6":
        # Westbound straight through
        
        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

      case "D3":
        # Westbound U turn

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x - car_length,
           entry_intersection_y),
          ("intersection", exit_intersection_x - car_length,
           exit_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
        
      case "D4" | "D5":
        # Westbound right turn

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x - car_length,
           entry_intersection_y),
          ("intersection", exit_intersection_x,
           exit_intersection_y + car_length),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

        permissive_right_shape = shapely.geometry.box (
          exit_intersection_x - (lane_width / 2),
          exit_intersection_y - (lane_width * 2),
          exit_intersection_x + (lane_width / 2),
          entry_intersection_y + (2.0 * lane_width) + permissive_distance)
                                                       
        permissive_right_info = (("moving East", intersection_shape),
                                 ("present", permissive_right_shape))
        
      case "H4" | "H5":
        # Eastbound left turn

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x + (2 * car_length),
           entry_intersection_y),
          ("intersection", exit_intersection_x,
           exit_intersection_y + car_length),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

      case "H3":
        # Eastbound striaght through

        milestones = (
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))

      case "J1" | "J2":
        # Eastbound right turn

        milestones = (
          (adjacent_lane_name, adjacent_start_x, adjacent_start_y),
          (adjacent_lane_name, entry_start_x - (1.0 * car_length),
           adjacent_start_y),
          (entry_lane_name, entry_start_x, entry_start_y),
          (entry_lane_name, entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x, entry_intersection_y),
          ("intersection", entry_intersection_x + car_length,
           entry_intersection_y),
          ("intersection", exit_intersection_x,
           exit_intersection_y - car_length),
          ("intersection", exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_intersection_x, exit_intersection_y),
          (exit_lane_name, exit_end_x, exit_end_y))
        
      case "psepsw" | "pnepnw":
        # pedestrian crossing westbound:
        # Pedestrians cross in both directions without conflict.
        # We model this by having westbound
        # pedestrians walk on the north side of the crosswalk.
        
        milestones = (
          (entry_lane_name, entry_start_x,
           entry_start_y - (crosswalk_width / 4.0)),
          (entry_lane_name, entry_intersection_x,
           entry_intersection_y - (crosswalk_width / 4.0)),
          ("crosswalk", entry_intersection_x,
           entry_intersection_y - (crosswalk_width / 4.0)),
          ("crosswalk", exit_intersection_x,
           exit_intersection_y - (crosswalk_width / 4.0)),
          (exit_lane_name, exit_intersection_x,
           exit_intersection_y - (crosswalk_width / 4.0)),
          (exit_lane_name, exit_end_x, exit_end_y - (crosswalk_width / 4.0)))

      case "pswpse" | "pnwpne":
        # Pedestrian crossing eastbound
        # Eastbound pedestrians walk on the south side of the crosswalk.

        milestones = (
          (entry_lane_name, entry_start_x,
           entry_start_y + (crosswalk_width / 4.0)),
          (entry_lane_name, entry_intersection_x,
           entry_intersection_y + (crosswalk_width / 4.0)),
          ("crosswalk", entry_intersection_x,
           entry_intersection_y + (crosswalk_width / 4.0)),
          ("crosswalk", exit_intersection_x,
           exit_intersection_y + (crosswalk_width / 4.0)),
          (exit_lane_name, exit_intersection_x,
           exit_intersection_y + (crosswalk_width / 4.0)),
          (exit_lane_name, exit_end_x, exit_end_y + (crosswalk_width / 4.0)))
        
      case _:
        milestones = None

    travel_path["milestones"] = milestones
    travel_path["permissive left turn info"] = permissive_left_info
    travel_path["permissive right turn info"] = permissive_right_info
    
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
    case "A" | "E":
      lamp_names_map["Steady Circular Red"] = "Steady Left Arrow Red"
      lamp_names_map["Steady Circular Yellow"] = (
        "Steady Left Arrow Yellow (upper)")
      lamp_names_map["Steady Circular Green"] = "Steady Left Arrow Green"
      lamp_names_map["Flashing Circular Red"] = "Flashing Left Arrow Red"
      lamp_names_map["Flashing Circular Yellow"] = (
        "Flashing Left Arrow Yellow (upper)")
      lamp_names_map["Flashing Left Arrow Yellow"] = (
        "Flashing Left Arrow Yellow (lower)")
    case "B" | "F":
      lamp_names_map["Steady Circular Green"] = "Steady Circular Green"
    case "H":
      lamp_names_map["Steady Circular Green"] = ("Steady Left Arrow Green" +
                                                 " and Steady Circular Green")
    case "J":
      lamp_names_map["Steady Circular Red"] = "Steady Right Arrow Red"
      lamp_names_map["Steady Circular Yellow"] = "Steady Right Arrow Yellow"
      lamp_names_map["Steady Circular Green"] = "Steady Right Arrow Green"
      lamp_names_map["Flashing Circular Red"] = "Flashing Right Arrow Red"
      lamp_names_map["Flashing Circular Yellow"] = (
        "Flashing Right Arrow Yellow")
    case "psw" | "pse" | "pnw" | "pne":
      lamp_names_map["Steady Circular Red"] = "Don't Walk"
      lamp_names_map["Steady Circular Yellow"] = "Walk with Countdown"
      lamp_names_map["Steady Circular Green"] = "Walk"
      lamp_names_map["Flashing Circular Red"] = "Don't Walk"
      lamp_names_map["Flashing Circular Yellow"] = "Don't Walk"
      
  signal_face["lamp names map"] = lamp_names_map

if (do_lamp_map_output):
  lamp_map_file = open (lamp_map_file_name, 'w')
  lamp_map_file.write ("\\begin{longtable}{P{1.0cm} | P{5cm} | P{5cm}}\n")
  lamp_map_file.write ("  \\caption{Lamp Wiring}\\label{lamp_wiring} \\\\\n")
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
    case "B":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "C/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "C/Traffic Present")
      
    case "C":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "B/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "B/Traffic Present")
      
    case "psw":
      sensor_map["Traffic Approaching"] = ()
      sensor_map["Traffic Present"] = ("Traffic Present",
                                       "pse/Traffic Present")
      
    case "pse":
      sensor_map["Traffic Approaching"] = ()
      sensor_map["Traffic Present"] = ("Traffic Present",
                                       "psw/Traffic Present")
      
    case "pnw":
      sensor_map["Traffic Approaching"] = ()
      sensor_map["Traffic Present"] = ("Traffic Present",
                                       "pne/Traffic Present")
      
    case "pne":
      sensor_map["Traffic Approaching"] = ()
      sensor_map["Traffic Present"] = ("Traffic Present",
                                       "pnw/Traffic Present")
      
    case "D" | "H" | "J":
      sensor_map["Traffic Approaching"] = ()
      sensor_map["Traffic Present"] = ("Traffic Present",
                                       "Traffic Approaching")
    case "F":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "G/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "G/Traffic Present")
      
    case "G":
      sensor_map["Traffic Approaching"] = ("Traffic Approaching",
                                           "F/Traffic Approaching")
      sensor_map["Traffic Present"] = ("Traffic Present", "F/Traffic Present")

  # Flash command
  match signal_face["name"]:
    case "A" | "psw" | "pse" | "D" | "E" | "pnw" | "pne" | "H" | "J":
      sensor_map["Flash"] = ("Flash Red",)
      
    case "B" | "C" | "F" | "G":
      sensor_map["Flash"] = ("Flash Yellow",)

  # Preempt command
  sensor_map["Preempt"] = ("Preempt Red",)

  # Preempt command with the direction the emergency vehicle is approaching
  # from.
  match signal_face["name"]:
    case "H" | "J":
      sensor_map["Preempt from West"] = ("Preempt Green",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Red",)

    case "A" | "B" | "C":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Green",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Red",)

    case "D":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Green",)
      sensor_map["Preempt from North"] = ("Preempt Red",)

    case "E" | "F" | "G":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Green",)

    case "psw" | "pse" | "pnw" | "pne":
      sensor_map["Preempt from West"] = ("Preempt Red",)
      sensor_map["Preempt from South"] = ("Preempt Red",)
      sensor_map["Preempt from East"] = ("Preempt Red",)
      sensor_map["Preempt from North"] = ("Preempt Red",)
            
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
    # sensors are activated by vehicles and pedestrians.
    lane_info = find_lane_info(signal_face["name"])

    # The vehicle sensors have this size.
    sensor_length = 6
    sensor_width = 10
    
    match sensor_name:
      case "Traffic Approaching":
        match signal_face["name"]:
          case "A":
            sensor_offset = approach_sensor_short_distance
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] + sensor_offset
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] + sensor_offset + sensor_length
            
          case "B" | "C":
            sensor_offset = approach_sensor_long_distance
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] + sensor_offset
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] + sensor_offset + sensor_length
            
          case "E":
            sensor_offset = approach_sensor_short_distance
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] - sensor_offset - sensor_length
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] - sensor_offset
            
          case "F" | "G":
            sensor_offset = approach_sensor_long_distance
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] - sensor_offset - sensor_length
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] - sensor_offset
            
      case "Traffic Present":
        sensor_offset = 1
        match signal_face["name"]:
          case "psw" | "pnw":
            sensor["x min"] = lane_info[0] - 2
            sensor["y min"] = lane_info[1]
            sensor["x max"] = lane_info[0]
            sensor["y max"] = lane_info[1] + (crosswalk_width / 2.0)
            
          case "pse" | "pne":
            sensor["x min"] = lane_info[0]
            sensor["y min"] = lane_info[1] - (crosswalk_width / 2.0)
            sensor["x max"] = lane_info[0] + 2
            sensor["y max"] = lane_info[1]
            
          case "A" | "B" | "C":
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] + sensor_offset
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] + sensor_offset + sensor_length
            
          case "D":
            sensor["x min"] = lane_info[0] + sensor_offset
            sensor["y min"] = lane_info[1] - (sensor_width / 2.0)
            sensor["x max"] = lane_info[0] + sensor_offset + sensor_length
            sensor["y max"] = lane_info[1] + (sensor_width / 2.0)

          case "E" | "F" | "G":
            sensor["x min"] = lane_info[0] - (sensor_width / 2.0)
            sensor["y min"] = lane_info[1] - sensor_offset - sensor_length
            sensor["x max"] = lane_info[0] + (sensor_width / 2.0)
            sensor["y max"] = lane_info[1] - sensor_offset

          case "H" | "J":
            sensor["x min"] = lane_info[0] - sensor_offset - sensor_length
            sensor["y min"] = lane_info[1] - (sensor_width / 2.0)
            sensor["x max"] = lane_info[0] - sensor_offset
            sensor["y max"] = lane_info[1] + (sensor_width / 2.0)

    if ("x min" in sensor):
      sensor_shape = shapely.geometry.box (sensor["x min"], sensor["y min"],
                                         sensor["x max"], sensor["y max"])
      sensor["shape"] = sensor_shape
    
    sensor["value"] = False
    sensors [sensor_name] = sensor
    
  signal_face ["sensors"] = sensors
          
if (do_sensor_map_output):
  sensor_file = open (sensor_map_file_name, 'w')
  sensor_file.write ("\\begin{longtable}{P{1.0cm} | P{4.0cm} | P{6.0cm}}\n")
  sensor_file.write ("  \\caption{Sensor Wiring} \\\\\n")
  sensor_file.write ("  Signal Face & Sensor & " +
                       "Toggles \\endfirsthead\n")
  sensor_file.write ("  \\caption{Sensor Wiring continued} \\\\\n")
  sensor_file.write ("  Signal Face & Sensor & " +
                       "Toggles \\endhead\n")
  
  for signal_face in signal_faces_list:
    sensors = signal_face["sensors"]
    for sensor_name in sensors:
      sensor = sensors[sensor_name]
      sensor_file.write("   \\hline " + signal_face["name"] + " & " +
                        sensor_name + " &")
      toggles = sensor["toggles"]
      first_toggle = True
      for toggle_name in toggles:
        if (not first_toggle):
          sensor_file.write (",")
        sensor_file.write (" " + toggle_name)
        first_toggle = False
      sensor_file.write ("\\\\\n")

  sensor_file.write ("\\hline \\end{longtable}\n")
  sensor_file.close()
  
if (do_trace):
  trace_file.write ("Starting Signal Faces:\n")
  pprint.pprint (signal_faces_list, trace_file)

# Read the script file, if one was specified.
script_set = set()
if (do_script_input):
  with open (script_file_name, 'rt') as scriptfile:
    reader = csv.DictReader (scriptfile)
    for row in reader:
      the_time = fractions.Fraction (row['time'])
      the_operator = row['operator']
      signal_face_name = row['signal face']
      the_operand = row['operand']
      the_count = int(row['count'])
      the_interval = fractions.Fraction (row['interval'])
      for counter in range(0, the_count):
        this_time = the_time + (the_interval * counter);
        this_action = (this_time, the_operator, signal_face_name, the_operand)
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

# Format the speed for display.
def format_speed(the_speed_in_fps):
  the_speed_in_mph = the_speed_in_fps / mph_to_fps
  if (the_speed_in_mph < 5.0):
    return ((f'{the_speed_in_fps:04.1f}') + " fps")
  else:
    return ((f'{the_speed_in_mph:04.1f}') + " mph")

# format a location or distance for display.
def format_location(the_location):
  return (f'{the_location:.0f}')

# Format the place name for display
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

# Return the value of a named toggle in a specified signal face
def toggle_value (signal_face, toggle_name):
    toggles = signal_face["toggles"]
    for the_toggle in toggles:
      if (the_toggle["name"] == toggle_name):
        return (the_toggle["value"])

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
    print (format_time(current_time) + " toggle " + signal_face["name"] + "/" +
           toggle_name + " unknown.")
    error_counter = error_counter + 1
  return

# Return True if traffic can not flow through the specified signal
# face if traffic is already flowing through the conflicting signal face.
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
               " with any signal face that is already allowed to turn " +
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
      for signal_face in requesting_green:
        no_conflicts = True
        for conflicting_signal_face in allowed_green:
          if (does_conflict (signal_face, conflicting_signal_face)):
            no_conflicts = False
        if (no_conflicts and (signal_face not in had_its_chance)):
          requesting_green.remove(signal_face)
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
        signal_face["iluminated lamp name"] = external_lamp_name
        if (verbosity_level >= 2):
          print (format_time(current_time) + " signal face " +
                 signal_face["name"] + " lamp set to " + external_lamp_name +
                 ".")
        if ((table_level >= 2) and (current_time > table_start_time)):
          table_file.write ("\\hline " + format_time_N(current_time) + " & " +
                            signal_face["name"] +
                            " & Set lamp to " + external_lamp_name +
                            ". \\\\\n")
        if (do_events_output):
          events_file.write (str(current_time) + "," + signal_face["name"] +
                             ",lamp," + external_lamp_name + "\n")
          last_event_time = current_time
          
      case "set toggle":
        set_toggle_value (signal_face, action[1], True, "")
        
      case "clear toggle":
        # Don't clear the Traffic Present or the Traffic Approaching toggle
        # if a sensor which sets it is still active.
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
  state = finite_state_machine[state_name]
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

def add_traffic_element (type, travel_path_name):
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
             format_location(traffic_element["distance remaining"]) +
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
  shape_B = sensor["shape"]
  
  # An object will have no shape if it has left the simulation.
  if ((shape_A == None) or (shape_B == None)):
    return (False)
  
  if (shape_A.intersects(shape_B)):
    if (do_trace):
      trace_file.write ("These objects intersect at " +
                        format_time(current_time) + ":\n")
      pprint.pprint (traffic_element, trace_file)
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
  if (stopped_duration < 1):
    if (do_trace):
      trace_file.write (" Not stopped long enough.\n\n")
    return False
        
  # Check for a vehicle present or approaching.
  for permissive_item in permissive_info:
    movement_type = permissive_item[0]
    permissive_shape = permissive_item[1]
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
             format_location(traffic_element["distance remaining"]) +
             " speed " + format_speed(traffic_element["speed"]) +
             " moved " + format_location(distance_moved) + ".")
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
               format_location(traffic_element["distance remaining"]) +
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
                     format_location(
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
                       format_location(traffic_element["distance remaining"]) +
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
def perform_script_action (the_operator, signal_face_name, the_operand):
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
          add_traffic_element (the_operator, the_operand)
          
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
           "(" + str(len(running_timers)) + ").")
    
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
      remove_timers_list = remove_timers_list + " " + the_timer["name"]
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
    state = finite_state_machine[state_name]
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
                     toggle_name + " for True.")
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
                     toggle_name + " for False.")
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
                     timer_name + " for being complete.")
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
                     timer_name + " for being not complete.")
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
    
  # Run any ripe actionss in the script.
  to_remove = set()
  for the_action in script_set:
    the_time = the_action[0]
    the_operator = the_action[1]
    signal_face_name = the_action[2]
    the_operand = the_action[3]
    if (the_time <= current_time):
      perform_script_action (the_operator, signal_face_name, the_operand)
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

# End of file traffic_control_signals.py
