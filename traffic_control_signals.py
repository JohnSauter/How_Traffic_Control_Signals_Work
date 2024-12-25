#!/usr/bin/python3
# -*- coding: utf-8
#
# traffic_control_signals.py implements the control logic for a traffic
# signal using finite state machines.

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
import math
import pprint
import decimal
import fractions
import csv
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Implement a traffic control ' + 
               'signal using finite state machines.'),
  epilog=('Copyright © 2024 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='traffic_control_signals 0.5 2024-12-24',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--log-file', metavar='log_file',
                     help='write logging output to the specified file')
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
parser.add_argument ('--log-level', type=int, metavar='log_level',
                     help='control the level of detail in the log: ' +
                     '1 is normal, 0 none')
parser.add_argument ('--log-start', type=decimal.Decimal, metavar='log_start',
                     help='do not log before this time, ' +
                     'default is -1.000')
parser.add_argument ('--duration', type=decimal.Decimal, metavar='duration',
                     help='length of time to run the simulator, ' +
                     'default is 0.000')
parser.add_argument ('--log-caption', metavar='log_caption',
                     help='caption of table created by log file')
parser.add_argument ('--script-input', metavar='script_input',
                     help='events for the simulator to execute')
parser.add_argument ('--waiting-limit', type=int, metavar='waiting_limit',
                     help='max wait time before getting green preference ' +
                     'for turning green; default 60 seconds.')
parser.add_argument ('--statistics', type=int, metavar='statistics',
                     help='statistics about the simulation ' +
                     'default is none.')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = 0
tracefile = ""
do_logging = 0
logfile = ""
do_red_state_output = 0
do_yellow_state_output = 0
do_green_state_output = 0
do_lamp_map_output = 0
do_sensor_map_output = 0
logging_level = 0
end_time = decimal.Decimal ('0.000')
log_start_time  = decimal.Decimal ('-1.000')
log_caption = "no caption"
do_script_input = 0
script_input_file = ""
waiting_limit = 60
statistics = 0
verbosity_level = 1
error_counter = 0

# Verbosity_level and logging level:
# 1 only errors and statistics if requested
# 2 add lamp changes, script actions, and vehicles and pedestrians
#   arriving, leaving and reaching milestones
# 3 add state changes
# 4 add toggle and sensor changes
# 5 add lots of other items

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = 1
  trace_file_name = arguments ['trace_file']
  tracefile = open (trace_file_name, 'wt')

if (arguments ['log_file'] != None):
  do_logging = 1
  log_file_name = arguments ['log_file']
  logfile = open (log_file_name, 'wt')

if (arguments ['red_state_file'] != None):
  do_red_state_output = 1
  red_state_output_file_name = arguments ['red_state_file']

if (arguments ['yellow_state_file'] != None):
  do_yellow_state_output = 1
  yellow_state_output_file_name = arguments ['yellow_state_file']

if (arguments ['green_state_file'] != None):
  do_green_state_output = 1
  green_state_output_file_name = arguments ['green_state_file']

if (arguments ['lamp_map_file'] != None):
  do_lamp_map_output = 1
  lamp_map_file_name = arguments ['lamp_map_file']

if (arguments ['sensor_map_file'] != None):
  do_sensor_map_output = 1
  sensor_map_file_name = arguments ['sensor_map_file']

if ((arguments ['log_level'] != None) and (do_logging == 1)):
  logging_level = arguments ['log_level']

if (arguments ['duration'] != None):
  end_time = arguments ['duration']
  
if (arguments ['log_start'] != None):
  log_start_time = arguments ['log_start']

if (arguments ['log_caption'] != None):
  log_caption = arguments ['log_caption']
  
if (arguments ['script_input'] != None):
  do_script_input = 1
  script_file_name = arguments ['script_input']
  
if (arguments ['waiting_limit'] != None):
  waiting_limit = arguments ['waiting_limit']

if (arguments ['statistics'] != None):
  statistics = arguments ['statistics']

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

start_time = decimal.Decimal("0.000")
current_time = fractions.Fraction(start_time)
  
# Write the first lines in the log file.

if (do_logging):
  logfile.write ("\\begin{longtable}{c | P{1.00cm} | p{9.25cm}}\n")
  logfile.write ("  \\caption{" + log_caption + "} \\\\\n")
  logfile.write ("  Time & Lane & Event \\endfirsthead \n")
  logfile.write ("  \\caption{" + log_caption + " continued} \\\\\n")
  logfile.write ("  Time & Lane & Events \\endhead \n")
  
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

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 1" )
exits_list.append(exit)
red_state.append(substate)

substate = dict()
substate["name"] = "Going Green 1"
substate["actions"] = list()
actions_list = substate["actions"]
action=("set toggle", "Request Green")
actions_list.append(action)
substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Green Request Granted")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 2" )
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
exit = ( conditional_tests, "Yellow", "Left Flashing 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
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
conditional_test = ("timer is not complete", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is not complete", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is not complete", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
conditional_test = ("timer is not complete", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Traffic Present")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Traffic Approaching")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("timer is not complete", "Maximum Green")
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

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Waiting for Clearance Request" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Waiting for Clearance Request" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
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

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
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
action = ("start timer", "Left Flashing Yellow Waiting")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Left Flashing Yellow Waiting")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Green" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Left Flashing Yellow Waiting")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Green" )
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

if (do_trace != 0):
  tracefile.write ("Finite State Machine template:\n")
  pprint.pprint (finite_state_machine, tracefile)
  tracefile.write ("\n")

#
# Write out the finite state machine template for the documentation.
#
def cap_first_letter (the_string):
  return (the_string[0].upper() + the_string[1:])

def write_out_state (the_state, output_file_name):
  output_file = open (output_file_name, 'w')
  output_file.write ("\\begin{description}[style=standard]\n")

  for substate in the_state:
    if (do_trace == 1):
      tracefile.write ("Writing out substate " + substate ["name"] + ".\n")
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

if (do_red_state_output == 1):
  write_out_state (red_state, red_state_output_file_name)

if (do_green_state_output == 1):
  write_out_state (green_state, green_state_output_file_name)

if (do_yellow_state_output == 1):
  write_out_state (yellow_state, yellow_state_output_file_name)

# Build the finite state machines for the signal faces:

signal_face_names = ( "A", "ps", "B", "C", "D", "E", "pn", "F", "G", "H", "J" )

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

for signal_face_name in ("A", "ps", "D", "E", "pn", "H", "J"):
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
  timer_durations[timer_full_name] = decimal.Decimal ("10.000")
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

for signal_face_name in ("ps", "pn"):
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

if (do_trace != 0):
  tracefile.write ("Timer durations:\n")
  pprint.pprint (timer_durations, tracefile)
  tracefile.write ("\n")

# Construct the conflict and partial conflict tables.
  
for signal_face in signal_faces_list:
  partial_conflict_set = None
  
  match signal_face["name"]:
    case "A":
      conflict_set = ("ps", "D", "F", "G", "H", "J")
      partial_conflict_set = ("ps", "D", "H", "H")
    case "ps":
      conflict_set = ("A", "B", "C", "D", "F", "G", "J")
    case "B" | "C":
      conflict_set = ("ps", "D", "E", "pn", "H")
    case "D":
      conflict_set = ("A", "ps", "B", "C", "E", "pn", "F", "G", "H", "J")
    case "E":
      conflict_set = ("B", "C", "D", "pn", "H")
      partial_conflict_set = ("D", "pn", "H")
    case "pn":
      conflict_set = ("B", "C", "D", "E", "F", "G", "H")
    case "F" | "G":
      conflict_set = ("A", "ps", "D", "pn", "H", "J")
    case "H":
      conflict_set = ("A", "B", "C", "D", "E", "pn", "F", "G")
    case "J":
      conflict_set = ("A", "ps", "D", "F", "G")
      
  if (partial_conflict_set == None):
    partial_conflict_set = conflict_set
  signal_face["conflicts"] = conflict_set
  signal_face["partial conflicts"] = partial_conflict_set

# Limit the time a signal face stays red while it is waiting to
# turn green.  This is a tradeoff between throughput and maximum
# waiting time for a vehicle or pedestrian.

for signal_face in signal_faces_list:
  match signal_face["name"]:
    case "A" | "ps" | "D" | "E" | "pn" | "H" | "J":
      signal_face["waiting limit"] = waiting_limit

    case "B" | "C" | "F" | "G":
      signal_face["waiting limit"] = waiting_limit / 2;

# Construct the travel paths.  A traffic element appears at the first
# milestone, then proceeds each following milestone.  When it reaches
# the last milestone it vanishes from the simulation.
approach_sensor_distance = 365
long_lane_length = 528
short_lane_length = 450
lane_width = 12

travel_paths = dict()
for entry_lane_name in ("A", "ps", "B", "C", "D", "E", "pn",
                        "F", "G", "H", "J"):
  
  adjacent_lane_name = None
  match entry_lane_name:
    case "A":
      adjacent_lane_name = "B"
    case "E":
      adjacent_lane_name = "F"
    
  for exit_lane_name in ("1", "2", "3", "4", "5", "6"):
    travel_path_name = entry_lane_name + exit_lane_name
    travel_path = None
    
    match travel_path_name:
      case "A1" | "E4":
        # U turn to far lane
        travel_path = ((adjacent_lane_name, long_lane_length),
                       (adjacent_lane_name, short_lane_length),
                       (entry_lane_name, short_lane_length),
                       (entry_lane_name, 0),
                       ("intersection", lane_width*4), ("intersection", 0),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "A2" | "E5":
        # U turn to near lane
        travel_path = ((adjacent_lane_name, long_lane_length),
                       (adjacent_lane_name, short_lane_length),
                       (entry_lane_name, short_lane_length),
                       (entry_lane_name, 0),
                       ("intersection", lane_width*3), ("intersection", 0),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "A6":
        # Left turn
        travel_path = ((adjacent_lane_name, long_lane_length),
                       (adjacent_lane_name, short_lane_length),
                       (entry_lane_name, short_lane_length),
                       (entry_lane_name, 0),
                       ("intersection", lane_width*7), ("intersection", 0),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "E3":
        # Left turn
        travel_path = ((adjacent_lane_name, long_lane_length),
                       (adjacent_lane_name, short_lane_length),
                       (entry_lane_name, short_lane_length),
                       (entry_lane_name, 0),
                       ("intersection", lane_width*6), ("intersection", 0),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "B5" | "C4" | "F2" | "G1":
        # Straight through
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*5),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))
        
      case "D2":
        # Left turn to far lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*7),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "D1":
        # Left turn to near lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*8),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "D6":
        # Straight through
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*7),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))
        
      case "D5":
        # Right turn to far lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*4),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "D4":
        # Right turn to near lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*3),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "H5":
        # Left turn to ner lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*7),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "H4":
        # Left turn to far lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*8),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "J1":
        # Right turn to near lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*3),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

      case "J2":
        # Right turn to far lane
        travel_path = ((entry_lane_name, long_lane_length),
                       (entry_lane_name, 0), ("intersection", lane_width*4),
                       (exit_lane_name, 0), (exit_lane_name, long_lane_length))

    travel_paths[travel_path_name] = travel_path

for travel_path_name in ("ps", "pn"):
  entry_lane_name = travel_path_name
  travel_path = ((entry_lane_name, lane_width),
                 (entry_lane_name, 0),
                 ("crosswalk", lane_width*6),
                 ("crosswalk", 0))
  
  travel_paths[travel_path_name] = travel_path
    
if (do_trace > 0):
  tracefile.write ("Travel paths:\n")
  pprint.pprint (travel_paths, tracefile)

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
      lamp_names_map["Steady Circular Green"] = "Steady Up Arrow Green"
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
    case "ps" | "pn":
      lamp_names_map["Steady Circular Red"] = "Don't Walk"
      lamp_names_map["Steady Circular Yellow"] = "Walk with Countdown"
      lamp_names_map["Steady Circular Green"] = "Walk"
      lamp_names_map["Flashing Circular Red"] = "Don't Walk"
      lamp_names_map["Flashing Circular Yellow"] = "Don't Walk"
      
  signal_face["lamp names map"] = lamp_names_map

if (do_lamp_map_output != 0):
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

# Signal_face["sensors"]is a dictionary whose indexes are sensor names.
# The value of each entry is a sensor, which is a dictionary
# with entries name, toggles, position, length, and value.
# Toggles is a tuple of toggle names.  If a toggle name contains a slash
# it refers to a different signal face.  Position is the distance from
# the stop line to the center of the sensor.  Length is the length of
# the sensor.  Value is True or False.  Only the Traffic Approaching
# and Traffic Present sensors have sizes and positions in the lane.

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
    case "A" | "ps" | "D" | "E" | "pn" | "H" | "J":
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

    case "ps" | "pn":
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

    # for the Traffic Approaching and Traffic Present sensors,
    # the size and placement varies between lanes.  These
    # sensors are activated by vehicles and pedestrians.
    match sensor_name:
      case "Traffic Approaching":
        match signal_face["name"]:
          case "A" | "B" | "C" | "E" | "F" | "G":
            sensor["position"] = 365
            sensor["length"] = 6
            
      case "Traffic Present":
        match signal_face["name"]:
          case "ps" | "pn":
            sensor["position"] = 1
            sensor["length"] = 2
          case _:
            sensor["position"] = 3
            sensor["length"] = 6
    
    sensor["value"] = False
    sensors [sensor_name] = sensor
    
  signal_face ["sensors"] = sensors
          
if (do_sensor_map_output != 0):
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
  
if (do_trace != 0):
  tracefile.write ("Starting Signal Faces:\n")
  pprint.pprint (signal_faces_list, tracefile)

# Read the script file, if one was specified.
script_set = set()
if (do_script_input == 1):
  with open (script_file_name, 'rt') as scriptfile:
    reader = csv.DictReader (scriptfile)
    for row in reader:
      the_time = fractions.Fraction (row['time'])
      the_operator = row['operator']
      signal_face_name = row['signal face']
      the_operand = row['operand']
      the_event = (the_time, the_operator, signal_face_name, the_operand)
      script_set.add(the_event)

  if (do_trace > 0):
    tracefile.write ("Script:\n")
    pprint.pprint (script_set, tracefile)
    tracefile.write ("\n")
  
# System Programs

# The clock is advanced only if this cycle has resulted in no activity.
no_activity = True              

# Format the clock for display
def format_time(the_time):
  return (f'{the_time:07.3f}')

# The conversion factor from miles per hour to feet per second:
mph_to_fps = fractions.Fraction(5280, 60*60)

# Format the speed for display.
def format_speed(the_speed):
  the_speed_in_mph = the_speed / mph_to_fps
  return (f'{the_speed_in_mph:02.0f}')

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
            
        if ((logging_level >= 4) and (current_time > log_start_time)):
          logfile.write ("\\hline " + format_time(current_time) + " & " +
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
            if ((logging_level >= 5) and (current_time > log_start_time)):
              logfile.write ("\\hline " + format_time(current_time) + " & " +
                             signal_face ["name"] +
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
        if ((logging_level >= 5) and (current_time > log_start_time)):
          logfile.write ("\\hline " + format_time(current_time) + " & " +
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
        if ((logging_level >= 2) and (current_time > log_start_time)):
          logfile.write ("\\hline " + format_time(current_time) + " & " +
                         signal_face["name"] +
                         " & Set lamp to " + external_lamp_name + ". \\\\\n")
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
                    if (verbosity_level >= 4):
                      print (format_time(current_time) + " signal face " +
                             signal_face_name +
                             " Unable to clear toggle " + toggle_name +
                             " because sensor " + full_test_sensor_name +
                             " is still active.")
                    if ((logging_level >= 4) and
                        (current_time > log_start_time)):
                      logfile.write ("\\hline " + format_time(current_time) +
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
              if ((logging_level >= 5) and (current_time > log_start_time)):
                logfile.write ("\\hline " + format_time(current_time) + " & " +
                               signal_face ["name"] + " & Start timer " +
                               timer_name + ". \\\\\n")
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
  if ((state_name != old_state_name) or (substate_name != old_substate_name)):
    no_activity = False
  else:
    if (verbosity_level >= 5):
      print (format_time(current_time) + " signal face " +
             signal_face["name"] + " not a significant state change.")
      
  signal_face["state"] = state_name
  signal_face["substate"] = substate_name

  if (verbosity_level >= 3):
    print (format_time(current_time) + " signal face " + signal_face["name"] +
           " enters state " + state_name +
           " substate " + substate_name + ".")
  if ((logging_level >= 3) and (current_time > log_start_time)):
    logfile.write ("\\hline " + format_time(current_time) + " & " +
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
# Because lane positions are measured from the stop line,
# approach lanes have negative speed, departure lanes have positive speed.
# The crosswalk and intersection measure from the end, so they have
# negative speeds.
def speed_limit (lane_name):
  match lane_name:
    case "1" | "2" |"4" | "5":
      return (45 * mph_to_fps)
    case "B" | "C" | "F" | "G":
      return (-45 * mph_to_fps)
    case "3" | "6":
      return (25 * mph_to_fps)
    case "A" | "D" | "E" | "H" | "J":
      return (-25 * mph_to_fps)
    case "ps" | "pn" | "crosswalk" :
      return (fractions.Fraction(-35, 10))
    case "intersection":
      return (-25 * mph_to_fps)
  return None

# Subroutine to add a traffic element to the traffic elements dictionary.
# A traffic element starts at its first milestone.
next_traffic_element_number = 0
def add_traffic_element (type, travel_path_name):
  global travel_paths
  global traffic_elements
  global next_traffic_element_number
  
  traffic_element = dict()

  this_name = f'{type} {next_traffic_element_number:04d}'
  next_traffic_element_number = next_traffic_element_number + 1
  traffic_element["name"] = this_name
  
  traffic_element["type"] = type
  milestone_list = travel_paths[travel_path_name]
  traffic_element["milestones"] = milestone_list
  milestone_index = 0
  traffic_element["milestone index"] = milestone_index
  milestone = milestone_list[milestone_index]
  traffic_element["current lane"] = milestone[0]
  position = milestone[1]
  traffic_element["position"] = position
  next_milestone_index = milestone_index + 1
  next_milestone = milestone_list[next_milestone_index]
  traffic_element["distance remaining"] = abs(position - next_milestone[1])
  traffic_element["speed"] = speed_limit(traffic_element["current lane"])
  match type:
    case "car":
      traffic_element["length"] = 15
    case "truck":
      traffic_element["length"] = 40
    case "pedestrian":
      traffic_element["length"] = 3
      
  traffic_element["current time"] = current_time
  traffic_element["present"] = True

  if (verbosity_level >= 2):
    print (format_time(current_time) + " " + this_name +
           " starts on travel path " + travel_path_name +
           " in lane " + traffic_element["current lane"] +
           " at position " + str(traffic_element["position"]) +
           " distance to next milestone " +
           str(traffic_element["distance remaining"]) +
           " speed " + format_speed(traffic_element["speed"]) + ".")
  if ((logging_level >= 2) and (current_time > log_start_time)):
    logfile.write ("\\hline " + format_time(current_time) + " & " +
                   traffic_element["current lane"] + " & " +
                   cap_first_letter(this_name) + " starts on travel path " +
                   travel_path_name + " speed " +
                   format_speed(abs(traffic_element["speed"])) + ". \\\\\n")

  traffic_elements[this_name] = traffic_element
  return

# Subroutine to test for overlap of a traffic element
# with either a sensor or another traffic element.
def check_overlap (object_A, object_B):
  position_A = object_A["position"]
  length_A = object_A["length"]
  max_A = position_A + (length_A / 2)
  min_A = position_A - (length_A / 2)
  position_B = object_B["position"]
  length_B = object_B["length"]
  max_B = position_B + (length_B / 2)
  min_B = position_B - (length_B / 2)

  if ((max_A >= min_B) and (min_A <= max_B)):
    return (True)
  if ((max_B >= min_A) and (min_B <= max_A)):
    return (True)
  return (False)

# Subroutine to move a traffic element
def move_traffic_element (traffic_element):
  global current_time
  global no_activity

  delta_time = current_time - traffic_element["current time"]
  current_position = traffic_element["position"]
  distance_remaining = traffic_element["distance remaining"]
    
  if (delta_time > 0):
    current_speed = traffic_element["speed"]
    # Approach lanes have negative speed, departure lanes positive speed.
    distance_moved = delta_time * current_speed
    current_position = current_position + distance_moved
    distance_remaining = distance_remaining - abs(distance_moved)
    if (distance_remaining <= 0):
      current_position = current_position - distance_remaining
      distance_remaining = 0
    traffic_element["distance remaining"] = distance_remaining
    traffic_element["position"] = current_position
    traffic_element["current time"] = current_time
    if (verbosity_level >= 5):
        
      print (format_time(current_time) + " " + traffic_element["name"] +
             " in " + place_name(traffic_element) + " at position " +
             str(traffic_element["position"]) +
             " distance to next milestone  " +
             str(traffic_element["distance remaining"]) +
             " speed " + format_speed(traffic_element["speed"]) + ".")
    no_activity = False
  if (distance_remaining == 0):
    # We have reached this milestone.
    if ((verbosity_level >= 5) and (traffic_element["speed"] != 0)):        
      print (format_time(current_time) + " " + traffic_element["name"] +
             " in " + place_name(traffic_element) + " at position " +
             str(traffic_element["position"]) +
             " (a milestone) speed " + format_speed(traffic_element["speed"]) +
             ".")
    this_milestone_index = traffic_element["milestone index"]
    next_milestone_index = this_milestone_index + 1
    milestone_list = traffic_element["milestones"]
    if (next_milestone_index >= len(milestone_list)):
      traffic_element["present"] = False
      if (verbosity_level >= 2):
        print (format_time(current_time) + " " +
               traffic_element["name"] +
               " in " + place_name(traffic_element) + " exits the simulation.")
      if ((logging_level >= 2) and (current_time > log_start_time)):
        logfile.write ("\\hline " + format_time(current_time) + " & " +
                         traffic_element["current lane"] + " & " +
                       cap_first_letter(traffic_element["name"]) +
                       " exits the simulation. \\\\\n")
      
      no_activity = False
    else:
      this_milestone = milestone_list[this_milestone_index]
      next_milestone = milestone_list[next_milestone_index]
      # Check for changing lanes
      current_lane = traffic_element["current lane"]
      if (next_milestone[0] != current_lane):
        # We cannot enter the intersection or crosswalk if the light is red.
        if ((next_milestone[0] == "intersection") or
            (next_milestone[0] == "crosswalk")):
          if (current_lane in signal_faces_dict):
            signal_face = signal_faces_dict[current_lane]
            if (signal_face["state"] != "Green"):
              if (traffic_element["speed"] != 0):
                traffic_element["speed"] = 0
                if (verbosity_level >= 2):
                    print (format_time(current_time) + " " +
                           traffic_element["name"] +
                           " in " + place_name(traffic_element) +
                           " at position " + str(traffic_element["position"]) +
                           " distance to next milestone " +
                           str(traffic_element["distance remaining"]) +
                           " stopped.")
                if ((logging_level >= 2) and (current_time > log_start_time)):
                  logfile.write ("\\hline " + format_time(current_time) +
                                 " & " + traffic_element["current lane"] +
                                 " & " +
                                 cap_first_letter(traffic_element["name"]) +
                                 " stopped. \\\\\n")
                no_activity = False
            else:
              # We are trying to enter the intersection or the crosswalk
              # and the light is green.
              if (verbosity_level >= 2):
                print (format_time(current_time) + " " +
                       traffic_element["name"] +
                       " in " + place_name(traffic_element) +
                       " entering " + next_milestone[0] + ".")
            
              if ((logging_level >= 2) and (current_time > log_start_time)):
                logfile.write ("\\hline " + format_time(current_time) +
                               " & " + traffic_element["current lane"] +
                               " & " +
                               cap_first_letter(traffic_element["name"]) +
                               " entering " + next_milestone[0] + ". \\\\\n")
                
              traffic_element["current lane"] = next_milestone[0]
              traffic_element["position"] = next_milestone[1]
              traffic_element["speed"] = speed_limit(next_milestone[0])
              following_milestone_index = next_milestone_index + 1
              following_milestone = milestone_list[following_milestone_index]
              traffic_element["distance remaining"] = (
                abs(next_milestone[1] - following_milestone[1]))
              traffic_element["milestone index"] = next_milestone_index
              no_activity = False
        else:
          # Changing lanes but not into the intersection or crosswalk
          traffic_element["current lane"] = next_milestone[0]
          traffic_element["speed"] = speed_limit(next_milestone[0])
          # A milestone that changes lanes must be followed by
          # a milestone that does not change lanes.
          following_milestone_index = next_milestone_index + 1
          following_milestone = milestone_list[following_milestone_index]
          current_position = next_milestone[1]
          traffic_element["position"] = current_position
          traffic_element["distance remaining"] = (
            abs(current_position - following_milestone[1]))
          traffic_element["milestone index"] = next_milestone_index
          if (verbosity_level >= 2):
              print (format_time(current_time) + " " +
                     traffic_element["name"] +
                     " in " + place_name(traffic_element) +
                     " at position " + str(traffic_element["position"]) +
                     " distance to next milestone " +
                     str(traffic_element["distance remaining"]) +
                     " speed " + format_speed(traffic_element["speed"]) +
                     " lane change.")
          if ((logging_level >= 2) and (current_time > log_start_time)):
            logfile.write ("\\hline " + format_time(current_time) +
                           " & " + traffic_element["current lane"] +
                           " & " +
                           cap_first_letter(traffic_element["name"]) +
                           " at position " + str(traffic_element["position"]) +
                           " lane change. \\\\\n")
          no_activity = False
      else:
        # Not changing lanes
        current_position = next_milestone[1]
        traffic_element["position"] = current_position
        traffic_element["distance remaining"] = (
          abs(current_position - next_milestone[1]))
        traffic_element["milestone index"] = next_milestone_index
        if (verbosity_level >= 5):
          print (format_time(current_time) + " " +
                 traffic_element["name"] +
                 " in " + place_name(traffic_element) + " at position " +
                 str(traffic_element["position"]) +
                 " speed " + format_speed(traffic_element["speed"]) +
                 " at a milestone.")
        if ((logging_level >= 5) and (current_time > log_start_time)):
          logfile.write ("\\hline " + format_time(current_time) +
                         " & " + traffic_element["current lane"] +
                         " & " +
                         cap_first_letter(traffic_element["name"]) +
                         " at position " + str(traffic_element["position"]) +
                         " at a milestone. \\\\\n")
        no_activity = False
              
  return

# Subroutine to activate any sensors that detect a traffic element.
def check_sensors():
  for signal_face in signal_faces_list:
    signal_face_name = signal_face["name"]
    sensors = signal_face["sensors"]
    for sensor_name in sensors:
      sensor = sensors[sensor_name]
      if ("position" in sensor):
        triggered = False
        for traffic_element_name in traffic_elements:
          traffic_element = traffic_elements[traffic_element_name]
          if (signal_face_name == traffic_element["current lane"]):
            if (check_overlap (traffic_element, sensor)):
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
            if ((logging_level >= 2) and (current_time > log_start_time)):
              logfile.write ("\\hline " + format_time(current_time) + " & " +
                             signal_face ["name"] + " & Sensor " +
                             sensor_name + " set to " + str(sensor["value"]) +
                             " by " + sensor["triggered by"] +
                             ". \\\\\n")
            
  return
            
  
def timer_state (signal_face, timer_name):
  timers_list = signal_face["timers"]
  for the_timer in timers_list:
    if (the_timer["name"] == timer_name):
      return the_timer["state"]

# Execute an event from the script.
def perform_script_event (the_operator, signal_face_name, the_operand):
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
          if ((logging_level >= 2) and (current_time > log_start_time)):
            logfile.write ("\\hline " + format_time(current_time) + " & " +
                           signal_face ["name"] + " & Sensor " +
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
      if ((logging_level >= 5) and (current_time > log_start_time)):          
        logfile.write ("\\hline " + format_time(current_time) + " & " +
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

# Find the time of the next event in the script.
def find_next_script_event_time():
  next_script_event_time = None
  for the_event in script_set:
    the_time = the_event[0]
    if (next_script_event_time == None):
      next_script_event_time = the_time
    else:
      if (the_time < next_script_event_time):
        next_script_event_time = the_time
  return (next_script_event_time)

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
            if (not toggle_value(signal_face, toggle_name)):
              conditions_all_true = False
          case "toggle is false":
            toggle_name = conditional[1]
            if (toggle_value(signal_face, toggle_name)):
              conditions_all_true = False
          case "timer is completed":
            timer_name = conditional[1]
            if (timer_state (signal_face, timer_name) != "completed"):
              conditions_all_true = False
          case "timer not complete":
            timer_name = conditional[1]
            if (timer_state (signal_face, timer_name) == "completed"):
              conditions_all_true = False
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
    
  # Run the events in the script.
  to_remove = set()
  for the_event in script_set:
    the_time = the_event[0]
    the_operator = the_event[1]
    signal_face_name = the_event[2]
    the_operand = the_event[3]
    if (the_time <= current_time):
      perform_script_event (the_operator, signal_face_name, the_operand)
      to_remove.add(the_event)
      no_activity = False
  for the_event in to_remove:
    script_set.remove(the_event)

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
            if (verbosity_level >= 4):
              print (format_time(current_time) + " Sensor " +
                     signal_face ["name"] + "/" + sensor_name + " is True.")
            if ((logging_level >= 4) and (current_time > log_start_time)):
              logfile.write ("\\hline " + format_time(current_time) +
                             " & " + signal_face["name"] +
                             " &  Sensor " + sensor_name + " is True. \\\\\n")
            set_toggle_value (toggle_signal_face, root_toggle_name, True,
                              "sensor " + signal_face["name"] + "/" +
                              sensor_name)
            no_activity = False          
        
  # Update the positions of the cars, trucks and pedestrians
  for traffic_element_name in traffic_elements:
    traffic_element = traffic_elements[traffic_element_name]
    if (traffic_element["present"]):
      move_traffic_element(traffic_element)
        
  # Update the timers.
  update_timers()
  
  # We only update the clock if there is no activity.
  if (no_activity):
    next_timer_completion_time = find_next_timer_completion_time()
    next_script_event_time = find_next_script_event_time()
    next_traffic_element_time = find_next_traffic_element_time()

    # If there are no timers running, no script events waiting to run
    # and no traffic elements present then we are done.
    if ((next_timer_completion_time == None) and
        (next_script_event_time == None) and
        (next_traffic_element_time == None)):
      break

    # Otherwise we advance the clock to the next significant event.
    next_clock_time = end_time
    if ((next_timer_completion_time != None) and
        (next_timer_completion_time < next_clock_time)):
      next_clock_time = next_timer_completion_time
    if ((next_script_event_time != None) and
        (next_script_event_time < next_clock_time)):
      next_clock_time = next_script_event_time
    if ((next_traffic_element_time != None) and
        (next_traffic_element_time < next_clock_time)):
      next_clock_time = next_traffic_element_time
    current_time = next_clock_time
  else:
    no_activity = True
  
if (do_trace != 0):
  tracefile.write ("Ending Signal Faces:\n")
  pprint.pprint (signal_faces_list, tracefile)

 # If requested, also print the maximum wait times.
if ((statistics >= 1) and (verbosity_level >= 1)):
  for signal_face in signal_faces_list:
    if ("max wait time" in signal_face):
      print (format_time(current_time) + " signal face " +
             signal_face["name"] + " maximum wait " +
             format_time(signal_face["max wait time"]) + " at " +
             format_time(signal_face["max wait start"]) + ".")
  
if (do_logging == 1):
  logfile.write ("\\hline \\end{longtable}\n")
  logfile.close()

if (do_trace == 1):
  tracefile.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file traffic_control_signals.py
