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
                     version='process_events 0.1 2024-12-29',
                     help='print the version number and exit')
parser.add_argument ('--trace-file', metavar='trace_file',
                     help='write trace output to the specified file')
parser.add_argument ('--events-file', metavar='events_file',
                     help='read event output from the traffic simulator')
parser.add_argument ('--verbose', type=int, metavar='verbosity_level',
                     help='control the amount of output from the program: ' +
                     '1 is normal, 0 suppresses summary messages')

do_trace = False
trace_file_name = ""
do_events_input = False
event_file_name = ""
verbosity_level = 1
error_counter = 0

# Parse the command line.
arguments = parser.parse_args ()
arguments = vars(arguments)

if (arguments ['trace_file'] != None):
  do_trace = True
  trace_file_name = arguments ['trace_file']
  trace_file = open (trace_file_name, 'wt')

if (arguments ['events_file'] != None):
  do_events_input = True
  events_file_name = arguments ['events_file']

start_time = decimal.Decimal("0.000")
current_time = fractions.Fraction(start_time)
  

# Read the events file, if one was specified.
events = dict()

if (do_events_input):
  with open (events_file_name, 'rt') as events_file:
    reader = csv.DictReader (events_file)
    for row in reader:
      the_time = fractions.Fraction (row['time'])
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

      events[the_time] = the_event

  if (do_trace):
    trace_file.write ("Events:\n")
    pprint.pprint (events, trace_file)
    trace_file.write ("\n")
  
# TODO

if (do_trace):
  trace_file.close()

if (error_counter > 0):
  print ("Encountered " + str(error_counter) + " errors.")

# End of file traffic_control_signals.py
