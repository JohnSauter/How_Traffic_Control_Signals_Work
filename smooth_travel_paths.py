#!/usr/bin/python3
# -*- coding: utf-8
#
# smooth_travel_paths.py smooths the curved travel paths.

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

import time
import numpy as np
import scipy.interpolate
import math
import json
import pprint
import decimal
import fractions
import pathlib
import argparse

parser = argparse.ArgumentParser (
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description=('Smooth the curved travel paths.'),
  epilog=('Copyright © 2025 by John Sauter' + '\n' +
          'License GPL3+: GNU GPL version 3 or later; ' + '\n' +
          'see <http://gnu.org/licenses/gpl.html> for the full text ' +
          'of the license.' + '\n' +
          'This is free software: ' + 
          'you are free to change and redistribute it. ' + '\n' +
          'There is NO WARRANTY, to the extent permitted by law. ' + '\n' +
          '\n'))

parser.add_argument ('--version', action='version', 
                     version='draw_background 0.61 2025-11-15',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('input-file', metavar='input_file',
                     help='read the intersection description from this ' +
                     'JSON file.')
parser.add_argument ('output-file', metavar='background_file',
                     help='write the intersection description to this file')
parser.add_argument ('--parts', type=int, metavar='parts',
                     help='number of parts in each curve')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

error_counter = 0
verbosity_level = 1
do_trace = False
trace_file_name = ""
do_input = False
input_file_name = ""
do_output = False
background_file_name = ""

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_level = 1
  trace_file_name = arguments ['trace_file']
  trace_file_name = pathlib.Path(trace_file_name)
  trace_file = open (trace_file_name, 'w')

if (arguments ['input-file'] != None):
  do_input = True
  input_file_name = arguments ['input-file']
  input_file_name = pathlib.Path(input_file_name)

if (arguments ['output-file'] != None):
  do_output = True
  output_file_name = arguments ['output-file']
  output_file_name = pathlib.Path(output_file_name)
  
if (arguments ['parts'] != None):
  num_parts = int(arguments ['parts'])
else:
  num_parts = 15

if (arguments ['verbose'] != None):
  verbosity_level = int(arguments ['verbose'])

if (do_input):
  input_file = open (input_file_name, 'r')
  intersection_info = json.load (input_file)
  input_file.close()
else:
  intersection_info = dict()

if (do_trace):
  trace_file.write ("intersection info:\n")
  pprint.pprint (intersection_info, trace_file)

lanes_info = intersection_info ["lanes info"]
travel_paths = intersection_info ["travel paths"]

def smooth_travel_path (the_milestones, num_parts):
  new_milestones = list()
  num_segments = len(the_milestones)

  # Create a B_spline that covers the travel path.
  name_values = list()
  x_values = list()
  y_values = list()
  for seg_index in range (num_segments):
    the_milestone = the_milestones [seg_index]
    name_values.append (the_milestone[0])
    x_values.append (the_milestone[1])
    y_values.append (the_milestone[2])

  (B_spline, u) = scipy.interpolate.make_splprep ((x_values, y_values),
                                                  s= 0.1)
  # The B-spline is indexed by a value between 0 and 1, where 0
  # is the first point and 1 is the last.
  (new_x, new_y) = B_spline (0)
  new_milestones.append ((name_values[0], new_x, new_y))

  for seg_index in range(num_segments-1):
    # Whenever the line between two milestones is not
    # horizontal or vertical, add points using the B_spline
    this_milestone = the_milestones [seg_index]
    next_milestone = the_milestones [seg_index+1]
    this_name = this_milestone[0]
    this_x = this_milestone[1]
    this_y = this_milestone[2]
    next_name = next_milestone[0]
    next_x = next_milestone[1]
    next_y = next_milestone[2]
    this_u = u [seg_index]
    next_u = u [seg_index+1]
    delta_u = next_u - this_u
    if ((this_x != next_x) and (this_y != next_y)):
      for u_index in range(1,num_parts):
        u_val = this_u + (u_index*(delta_u/num_parts))
        (new_x, new_y) = B_spline (u_val)
        new_milestones.append ((this_name, new_x, new_y))
    (new_x, new_y) = B_spline (next_u)
    new_x = float(str(new_x))
    new_y = float(str(new_y))
    new_milestones.append ((next_name, new_x, new_y))

  return (new_milestones)

for travel_path_name in travel_paths:
  travel_path = travel_paths[travel_path_name]
  the_milestones = travel_path ["milestones"]
  new_milestones = smooth_travel_path (the_milestones, num_parts)
  travel_path ["milestones"] = new_milestones
  
# Output the information about the intersection for the simulator.
if (do_output):
    output_file = open (output_file_name, 'w')
    json.dump (intersection_info, output_file, indent = " ")
    output_file.close()
  

if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file smooth_travel_paths.py
