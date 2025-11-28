#!/usr/bin/python3
# -*- coding: utf-8
#
# define_traffic_control_signals.py defines the control logic for a traffic
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
import json
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Define a traffic control ' + 
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
                     version='define_traffic_control_signals 0.62 2025-11-22',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--output-file', metavar='output_file',
                     help='write the definition as a JSON file')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_output = False
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

if (arguments ['output_file'] != None):
  do_output = True
  output_file_name = arguments ['output_file']
  outputfile_name = pathlib.Path(output_file_name)
  output_file = open (output_file_name, 'w')

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])
  
# Construct the template finite state machine.  This template
# contains the states, actions, transitions, timers and toggles.
# All of the signal faces use it.

finite_state_machine = dict()

states = dict()

red_state = list()

substate = dict()
substate["name"] = "Waiting for Clearance"
substate["note"] = ("Come here when the traffic control signal powers up " +
                    "and when we have finished flashing.")
substate["actions" ] = list()
actions_list = substate["actions"]
action = ("set lamp", "Steady Circular Red")
actions_list.append(action)
action=("clear toggle", "Cleared")
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
substate["note"] = ("We have waited long enough for all vehicles which " +
                     "passed through this signal face when it was green " +
                     "to have cleared the intersection.  Conflicting signal " +
                     "faces may now turn green.")
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
action = ("clear toggle", "Flash Red")
actions_list.append(action)
action = ("clear toggle", "Flash Yellow")
actions_list.append(action)
action=("clear toggle", "Request Green")
actions_list.append(action)
action = ("clear toggle", "Request Partial Clearance")
actions_list.append(action)
actions_list = substate["actions"]
action = ("clear toggle", "Request Clearance")
actions_list.append(action)
action=("clear toggle", "Green Request Granted")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

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
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 1a" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 1p" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Going Green 4")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Going Green 4")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Force")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit  = ( conditional_tests, "Red", "Force")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Red Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 4")
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Force"
substate["note"] = ("The signal face is being forced to turn red and " +
                    "stay red until the force is removed.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("clear toggle", "Preempt Red")
actions_list.append(action)
action = ("clear toggle", "Manual Red")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Force" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Force" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Delay Green 1a"
substate["note"] = ("There is traffic approaching; we would like " +
                    "to turn green but wait to make sure the traffic " +
                    "does not disappear by turning right.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("start timer", "Green Delay Approaching")
actions_list.append(action)
action = ("start timer", "Green Delay Present")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2a" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Delay Green 1p"
substate["note"] = ("There is traffic present; we would like " +
                    "to turn green but wait to make sure the traffic " +
                    "does not disappear by turning right.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("start timer", "Green Delay Present")
actions_list.append(action)
action = ("start timer", "Green Delay Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2p" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Delay Green 2a"
substate["note"] = ("Wait for the approaching traffic to clear the sensor.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Delay Approaching")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2a" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 3a" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Delay Green 2p"
substate["note"] = ("Wait for the present traffic to clear the sensor.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("clear toggle", "Traffic Present")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Delay Present")
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
exit = ( conditional_tests, "Red", "Delay Green 2p" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 3p" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Delay Green 3a"
substate["note"] = ("There is no vehicle on the Traffic Approaching " +
                    "sensor.  If that remains true do not turn green.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Delay Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2a" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2p" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Delay Green 3p"
substate["note"] = ("There is no vehicle on the Traffic Present " +
                    "sensor.  If that remains true do not turn green.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("clear toggle", "Traffic Present")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Delay Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2p" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Delay Green 2a" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Going Green 1"
substate["note"] = ("Turn green unless the conflicting traffic disappears.  " +
                    "Wait until other lanes have had an opportunity to turn " +
                    "green so two lanes cannot exchange green time between " +
                    "each other and starve a third.")
substate["actions"] = list()
actions_list = substate["actions"]

action = ("set toggle", "Request Green")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Green Request Granted")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 2" )
exits_list.append(exit)

red_state.append(substate)

substate=dict()
substate["name"] = "Going Green 2"
substate["note"] = ("This lane has permission to turn green.  " +
                    "Ask conflicting signal faces to turn red.")
substate["actions"] = list()
actions_list = substate["actions"]

action=("clear toggle", "Request Green")
actions_list.append(action)
action = ("set toggle", "Request Partial Clearance")
actions_list.append(action)
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Partial Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "No Traffic" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Going Green 4"
substate["note"] = ("Come here to turn green even though there is no " +
                    "traffic in this lane.")
substate["actions"] = list()
actions_list = substate["actions"]
action=("set toggle", "Request Green")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Green Request Granted")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Going Green 5" )
exits_list.append(exit)

red_state.append(substate)

substate=dict()
substate["name"] = "Going Green 5"
substate["note"] = ("This lane has permission to turn green even though it " +
                    "has no traffic.")
substate["actions"] = list()
actions_list = substate["actions"]
action=("clear toggle", "Request Green")
actions_list.append(action)
action = ("set toggle", "Request Partial Clearance")
actions_list.append(action)
substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Red", "Travel Path is Clear")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Partial Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "No Traffic" )
exits_list.append(exit)

red_state.append(substate)

substate = dict()
substate["name"] = "Flashing"
substate["note"] = ("Come here to flash the signal face red.")
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

states["Red"] = red_state

green_state = list()

substate = dict()
substate["name"] = "No Traffic"
substate["note"] = ("This lane shows the green lamp on its signal face.  " +
                    "As long as there is no traffic at the intersection " +
                    "the finite state machine stays in this substate.")
substate["actions"] = list()
actions_list = substate["actions"]
action=("set lamp", "Steady Circular Green")
actions_list.append(action)
action=("clear toggle", "Green Request Granted")
actions_list.append(action)
action = ("clear toggle", "Cleared")
actions_list.append(action)
action = ("clear toggle", "Request Partial Clearance")
actions_list.append(action)
action = ("clear toggle", "Request Clearance")
actions_list.append(action)
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)
action = ("start timer", "Minimum Green")
actions_list.append(action)
action = ("start timer", "Green Limit")
actions_list.append(action)
action = ("start timer", "Passage")
actions_list.append(action)
action = ("set toggle", "Traffic Flowing")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Clearance Requested")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Force 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Force 1")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Clearance Requested"
substate["note"] = ("A conflicting travel path has asked this lane " +
                    "to turn red but there is not presently a gap " +
                    "in the traffic.")

substate["actions"] = list()
actions_list = substate["actions"]
action = ("start timer", "Maximum Green")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Waiting for Gap 1")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Force 1"
substate["note"] = ("This signal face is being forced to turn green " +
                    "and stay green until the force is removed.")

substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Force 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Force 1" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Green", "Force 2")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Force 2"
substate["note"] = ("The requirement that this signal face be green " +
                    "is lifted.")
substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Clearance Requested")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Force 1")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Force 1")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Waiting for Gap 1"
substate["note"] = ("This lane has been asked to turn red but there is " +
                    "traffic entering the intersection from this lane " +
                    "so we wait for a gap in the traffic.")

substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Waiting for Gap 2")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Waiting for Gap 1")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Waiting for Gap 2"
substate["note"] = ("The vehicle has cleared the sensor so start measuring " +
                    "the time until the next vehicle triggers it.")

substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
actions_list.append(action)
action = ("start timer", "Passage")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Passage")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Maximum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Waiting for Gap 1")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Looking for Gap 1"
substate["note"] = ("There is traffic in this lane.  " +
                    "There is currently no need to turn red " +
                    "but there may be such a need in the future, " +
                    "so keep track of gaps in the traffic.  "+
                    "Wait for the vehicle to finish passing over the sensor.")

substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Clearance Requested")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is false", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap 2")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap 1")
exits_list.append(exit)

green_state.append(substate)

substate = dict()
substate["name"] = "Looking for Gap 2"
substate["note"] = ("The vehicle has cleared the sensor so look for " +
                    "a gap in the traffic.")

substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
actions_list.append(action)
action = ("start timer", "Passage")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Going Red")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
conditional_test = ("timer is completed", "Minimum Green")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Flashing")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Green Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Clearance Requested")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Traffic Approaching")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "Looking for Gap 1")
exits_list.append(exit)

green_state.append(substate)

states["Green"] = green_state

yellow_state = list()
substate = dict()
substate["name"] = "Going Red"
substate["note"] = ("The signal face is passing through yellow on its way " +
                    " to turning red.")
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
substate["note"] = ("Flash the lower left arrow in the signal face " +
                    "to indicate that the vehicle may make a permissive " +
                    "left turn.")

actions_list = substate["actions"]
action = ("set lamp", "Flashing Left Arrow Yellow")
actions_list.append(action)
action=("clear toggle", "Green Request Granted")
actions_list.append(action)
action = ("clear toggle", "Cleared")
actions_list.append(action)
action=("clear toggle", "Request Partial Clearance")
actions_list.append(action)
action=("clear toggle", "Request Clearance")
actions_list.append(action)
action=("clear toggle", "Manual Green")
actions_list.append(action)
action=("clear toggle", "Preempt Green")
actions_list.append(action)
action=("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("start timer", "Minimum Left Flashing Yellow")
actions_list.append(action)
action = ("start timer", "Left Flashing Yellow Limit")
actions_list.append(action)
action = ("start timer", "Left Flashing Yellow Waiting")
actions_list.append(action)
action=("set toggle", "Traffic Flowing")
actions_list.append(action)

substate["exits"] = list()
exits_list = substate["exits"]

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Minimum Left Flashing Yellow")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Yellow", "Left Flashing 2")
exits_list.append(exit)

yellow_state.append(substate)

substate = dict()
substate["name"] = "Left Flashing 2"
substate["note"] = ("The signal face has been showing a left flashing " +
                    "arrow long enough for the traffic to start moving.  ")
substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Traffic Present")
actions_list.append(action)
action = ("clear toggle", "Traffic Approaching")
actions_list.append(action)
action = ("clear toggle", "Manual Green")
actions_list.append(action)
action = ("clear toggle", "Preempt Green")
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
conditional_test = ("toggle is true", "Clearance Requested")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = (conditional_tests, "Green", "No Traffic")
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("timer is completed", "Left Flashing Yellow Limit")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Manual Green")
conditional_tests.append(conditional_test)
conditional_test = ("toggle is false", "Preempt Green")
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
conditional_test = ("toggle is true", "Traffic Present")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Green" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 2" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Left Flashing 2" )
exits_list.append(exit)

yellow_state.append(substate)

substate = dict()
substate["name"] = "Flashing"
substate["actions"] = list()
substate["note"] = ("Flash yellow until told to stop.")
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
substate["note"] = ("The vehicle is unable to make a permissive left turn " +
                    "so stop the oncoming traffic.")
substate["actions"] = list()
actions_list = substate["actions"]
action = ("clear toggle", "Request Green")
actions_list.append(action)
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
conditional_test = ("toggle is true", "Manual Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Preempt Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "No Traffic" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Manual Green")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "No Traffic" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Red")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Going Red" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Flash Yellow")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Yellow", "Flashing" )
exits_list.append(exit)

conditional_tests = list()
conditional_test = ("toggle is true", "Conflicting Paths are Clear")
conditional_tests.append(conditional_test)
exit = ( conditional_tests, "Green", "No Traffic" )
exits_list.append(exit)

yellow_state.append(substate)

states["Yellow"] = yellow_state

finite_state_machine["states"] = states

toggle_names = ( "Clearance Requested", "Cleared",
                 "Conflicting Paths are Clear", "Flash Red", "Flash Yellow",
                 "Green Request Granted",
                 "Manual Green", "Manual Red",
                 "Partial Conflicting Paths are Clear", "Preempt Green",
                 "Preempt Red", "Request Clearance",
                 "Request Green", "Request Partial Clearance",
                 "Traffic Approaching", "Traffic Flowing", "Traffic Present" )
finite_state_machine["toggles"] = toggle_names

timer_names = ( "Red Clearance", "Yellow Change", "Minimum Green",
                "Passage", "Maximum Green",
                "Green Limit", "Green Delay Approaching", \
                "Green Delay Present",
                "Left Flashing Yellow Waiting", "Left Flashing Yellow Limit",
                "Minimum Left Flashing Yellow", "Red Limit")

finite_state_machine["timer names"] = timer_names

if (do_trace):
  trace_file.write ("Finite State Machine template:\n")
  pprint.pprint (finite_state_machine, trace_file)
  trace_file.write ("\n")

if (do_output):
  json.dump (finite_state_machine, output_file, indent=" ")
  output_file.close()

if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file define_traffic_control_signals.py
