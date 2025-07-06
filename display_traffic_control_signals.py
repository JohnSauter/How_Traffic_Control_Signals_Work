#!/usr/bin/python3
# -*- coding: utf-8
#
# display_traffic_control_signals.py outputs the control logic for a traffic
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
                     version='traffic_control_signals 0.39 2025-07-06',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--input-file', metavar='input_file',
                     help='read the finite state machine template as JSON')
parser.add_argument ('--red-state-file', metavar='red_state_file',
                     help='write the red state description as a LaTex file')
parser.add_argument ('--yellow-state-file', metavar='yellow_state_file',
                     help=('write the yellow state description ' + 
                           'as a LaTex file'))
parser.add_argument ('--green-state-file', metavar='green_state_file',
                     help='write the green state description as a LaTex file')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_input = False
do_red_state_output = False
do_yellow_state_output = False
do_green_state_output = False
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

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

# Read the definition of the finite state machine as a JSON file.

if (do_input):
  input_file = open (input_file_name, 'r')
  finite_state_machine = json.load (input_file)
else:
  finite_state_machine = dict()
  
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

states = finite_state_machine["states"]

if (do_red_state_output):
  red_state = states["Red"]
  write_out_state (red_state, red_state_output_file_name)

if (do_green_state_output):
  green_state = states["Green"]
  write_out_state (green_state, green_state_output_file_name)

if (do_yellow_state_output):
  yellow_state = states ["Yellow"]
  write_out_state (yellow_state, yellow_state_output_file_name)

if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file display_traffic_control_signals.py
