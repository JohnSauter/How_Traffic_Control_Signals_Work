# File: Makefile.am, author: John Sauter, date: November 27, 2025.
#
# Build traffic_control_signals.pdf and animations.

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

# The main target is the file traffic_control_signals.pdf
all: traffic_control_signals.pdf
.PHONEY: all

# Inkscape fails if many copies are run in parallel.
.NOTPARALLEL:

# Include the following documentation files in the distribution.
dist_doc_DATA = \
	README \
	COPYING \
	LICENSE \
	AUTHORS \
	ChangeLog \
	INSTALL \
	NEWS

# Also distribute these files, used to build the PDF.
EXTRA_DIST = \
signal_ccc.svg \
signal_ccu.svg \
signal_rrr.svg \
signal_cccl.svg \
signal_llll.svg \
fix_files.sh autogen.sh \
left_turn_script.txt \
left_turn_delayed_script.txt \
legalcode.txt \
multiple_script.txt \
MUTCD_Ped_Signal_-_Hand_with_timer.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-00.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-01.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-02.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-03.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-04.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-05.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-06.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-07.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-08.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-09.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-10.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-11.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-12.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-13.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-14.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-15.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-16.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-17.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-18.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-19.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-20.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-21.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-22.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-23.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-24.svg \
MUTCD_Ped_Signal_-_Hand_with_timer-25.svg \
MUTCD_Ped_Signal_-_Steady_hand.svg \
MUTCD_Ped_Signal_-_Walk.svg \
pedestrian_and_left_turn_script.txt \
pedestrian_script.txt \
references.bib \
define_traffic_control_signals.py \
display_traffic_control_signals.py \
define_complex_intersection.py \
define_one_way_bridge.py \
bridge_one_car_script.txt \
bridge_two_cars_script.txt \
four_corners_many_script.txt \
define_four_corners.py \
display_intersection.py \
simulate_traffic.py \
draw_background.py \
smooth_travel_paths.py \
traffic_control_signals.tex \
state_diagram.txt 

# These files are used by the renderer.
EXTRA_DIST += \
signal_ccc_Green.svg \
signal_ccc_Red.svg \
signal_ccc_Yellow.svg \
signal_ccu_Green.svg \
signal_ccu_Red.svg \
signal_ccu_Yellow.svg \
signal_Dark_3.svg \
signal_Dark_4.svg \
signal_cccl_Green.svg \
signal_cccl_Red.svg \
signal_cccl_Yellow.svg \
signal_llll_Flashing_Yellow.svg \
signal_llll_Green.svg \
signal_llll_Red.svg \
signal_llll_Yellow.svg \
signal_rrr_Green.svg \
signal_rrr_Red.svg \
signal_rrr_Yellow.svg \
car-38800411-right.svg \
car-38800411-up.svg \
truck-51893967-up.svg \
truck-51893967-right.svg \
man_walking_right.svg \
process_events.py 

# Distribute the shell scripts which build the RPMs and the video animations.
EXTRA_DIST += build_RPMs.sh build_animation.sh build_animation_serial.sh \
render_animation.sh build_video.sh

# Build the RPM if the developer types "make RPMs".
.phoney: RPMs
RPMs:
	bash build_RPMs.sh

# The spec file is ueed to build RPMs for RPM-based distributions
# of GNU/Linux.
EXTRA_DIST += How_Traffic_Control_Signals_Work.spec

# Building the PDF depends on the bbl file, which is built below.
# When the bbl file is available, run LaTeX four times to be sure
# the forward references are resolved and the pdf byte count is correct.
# There is a slight chance that this process will be unstable,
# with the size of a reference changing the pagination, thus changing
# the size of a reference to that page.
# Perhaps someday we will check that this is not happening
# by verifying that the size of the last and next-to-last runs match.
traffic_control_signals.pdf : traffic_control_signals.tex \
traffic_control_signals.bbl LICENSE legalcode.txt \
state_diagram.eps red_state_table.tex \
green_state_table.tex yellow_state_table.tex \
lamp_map_names_01.tex lamp_map_names_02.tex lamp_map_names_03.tex \
sensor_map_01.tex sensor_map_02.tex sensor_map_03.tex \
timer_durations_01.tex timer_durations_02.tex timer_durations_03.tex \
idle_01_table.tex idle_03_table.tex left_turn_table.tex \
left_turn_delayed_table.tex \
pedestrian_table.tex pedestrian_and_left_turn_table.tex multiple_table.tex \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-00.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-01.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-02.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-03.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-04.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-05.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-06.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-07.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-08.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-09.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-10.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-11.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-12.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-13.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-14.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-15.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-16.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-17.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-18.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-19.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-20.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-21.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-22.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-23.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-24.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-25.pdf \
MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf signal_ccc.pdf signal_ccu.pdf signal_rrr.pdf \
signal_cccl.pdf signal_llll.pdf background_01.png background_02.png \
background_03.png \
bridge_one_car_animation_01.mkv bridge_one_car_table.tex \
bridge_two_cars_animation_01.mkv bridge_two_cars_table.tex \
four_corners_many_animation_02.mkv four_corners_many_table.tex \
pedestrian_and_left_turn_animation_03.mkv pedestrian_and_left_turn_table.tex \
multiple_animation_03.mkv multiple_table.tex  
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex \
--draftmode -draftmode -shell-escape ${srcdir}/traffic_control_signals.tex
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex \
--draftmode -draftmode -shell-escape ${srcdir}/traffic_control_signals.tex
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex \
--draftmode -draftmode -shell-escape ${srcdir}/traffic_control_signals.tex
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex \
-shell-escape "${srcdir}/traffic_control_signals.tex"

# Build the bbl file by running LaTeX without it, then running bibtex.
traffic_control_signals.bbl : traffic_control_signals.tex references.bib \
LICENSE legalcode.txt state_diagram.eps \
red_state_table.tex green_state_table.tex yellow_state_table.tex \
lamp_map_names_01.tex lamp_map_names_02.tex lamp_map_names_03.tex \
sensor_map_01.tex sensor_map_02.tex sensor_map_03.tex \
timer_durations_01.tex timer_durations_02.tex timer_durations_03.tex \
idle_01_table.tex idle_03_table.tex left_turn_table.tex \
left_turn_delayed_table.tex \
pedestrian_table.tex pedestrian_and_left_turn_table.tex multiple_table.tex \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-00.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-01.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-02.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-03.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-04.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-05.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-06.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-07.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-08.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-09.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-10.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-11.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-12.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-13.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-14.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-15.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-16.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-17.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-18.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-19.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-20.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-21.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-22.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-23.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-24.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer-25.pdf \
MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf signal_ccc.pdf signal_ccu.pdf signal_rrr.pdf \
signal_cccl.pdf signal_llll.pdf background_01.png background_02.png \
background_03.png \
bridge_one_car_animation_01.mkv bridge_one_car_table.tex \
bridge_two_cars_animation_01.mkv bridge_two_cars_table.tex \
four_corners_many_animation_02.mkv four_corners_many_table.tex \
pedestrian_and_left_turn_animation_03.mkv pedestrian_and_left_turn_table.tex \
multiple_animation_03.mkv multiple_table.tex 
	echo " " >"${builddir}/traffic_control_signals.bbl"
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex \
--draftmode -draftmode -shell-escape "${srcdir}/traffic_control_signals.tex"
	BIBINPUTS=${TEXINPUTS}:${builddir}:${srcdir} bibtex \
"${builddir}/traffic_control_signals.aux"

# Build a chart of the important states of the finite state machines.
state_diagram.eps : state_diagram.txt
	neato -Teps "${srcdir}/state_diagram.txt" \
-o "${builddir}/state_diagram.eps"

# Create a JSON file which describes the finite state machine template.
finite_state_machine.json : define_traffic_control_signals.py
	python3 "${srcdir}/define_traffic_control_signals.py" \
--output="${builddir}/finite_state_machine.json"

# Generate the state tables from the implementation's finite state machine.
red_state_table.tex : display_traffic_control_signals.py \
finite_state_machine.json
	python3 "${srcdir}/display_traffic_control_signals.py" \
--input="${builddir}/finite_state_machine.json" \
--red="${builddir}/red_state_table.tex"

yellow_state_table.tex : display_traffic_control_signals.py \
finite_state_machine.json
	python3 "${srcdir}/display_traffic_control_signals.py" \
--input="${builddir}/finite_state_machine.json" \
--yellow="${builddir}/yellow_state_table.tex"

green_state_table.tex : display_traffic_control_signals.py \
finite_state_machine.json
	python3 "${srcdir}/display_traffic_control_signals.py" \
--input="${builddir}/finite_state_machine.json" \
--green="${builddir}/green_state_table.tex"

# Create a JSON file which describes the one-way bridge example.
one_way_bridge.json : define_one_way_bridge.py \
finite_state_machine.json smooth_travel_paths.py
	python3 "${srcdir}/define_one_way_bridge.py" \
--input="${builddir}/finite_state_machine.json" \
--output="${builddir}/one_way_bridge_unsmoothed.json"
	python3 "${srcdir}/smooth_travel_paths.py" \
"${builddir}/one_way_bridge_unsmoothed.json" \
"${builddir}/one_way_bridge.json"

# Create a JSON file which describes the four corners example.
four_corners.json : define_four_corners.py \
finite_state_machine.json smooth_travel_paths.py
	python3 "${srcdir}/define_four_corners.py" \
--input="${builddir}/finite_state_machine.json" \
--output="${builddir}/four_corners_unsmoothed.json"
	python3 "${srcdir}/smooth_travel_paths.py" \
"${builddir}/four_corners_unsmoothed.json" \
"${builddir}/four_corners.json"

# Create a JSON file which describes the complex intersection example.
complex_intersection.json : define_complex_intersection.py \
finite_state_machine.json smooth_travel_paths.py
	python3 "${srcdir}/define_complex_intersection.py" \
--input="${builddir}/finite_state_machine.json" \
--output="${builddir}/complex_intersection_unsmoothed.json"
	python3 "${srcdir}/smooth_travel_paths.py" \
"${builddir}/complex_intersection_unsmoothed.json" \
"${builddir}/complex_intersection.json"

lamp_map_names_01.tex : display_intersection.py one_way_bridge.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/one_way_bridge.json" \
--table-label "lamp_map_01" \
--lamp-map="${builddir}/lamp_map_names_01.tex" 

lamp_map_names_02.tex : display_intersection.py four_corners.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/four_corners.json" \
--table-label "lamp_map_02" \
--lamp-map="${builddir}/lamp_map_names_02.tex" 

lamp_map_names_03.tex : display_intersection.py complex_intersection.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/complex_intersection.json" \
--table-label "lamp_map_03" \
--lamp-map="${builddir}/lamp_map_names_03.tex" 

sensor_map_01.tex : display_intersection.py one_way_bridge.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/one_way_bridge.json"  \
--table-label "sensor_map_01" --only-important \
--sensor-map="${builddir}/sensor_map_01.tex"

sensor_map_02.tex : display_intersection.py four_corners.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/four_corners.json"  \
--table-label "sensor_map_02" --only-important \
--sensor-map="${builddir}/sensor_map_02.tex" 

sensor_map_03.tex : display_intersection.py complex_intersection.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/complex_intersection.json"  \
--table-label "sensor_map_03" \
--sensor-map="${builddir}/sensor_map_03.tex" 

timer_durations_01.tex : display_intersection.py one_way_bridge.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/one_way_bridge.json"  \
--table-label "timer_duratons_01" --only-important \
--timer-durations="${builddir}/timer_durations_01.tex" 

timer_durations_02.tex : display_intersection.py four_corners.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/four_corners.json" \
--table-label "timer_durations_02" --only-important \
--timer-durations="${builddir}/timer_durations_02.tex" 

timer_durations_03.tex : display_intersection.py complex_intersection.json
	python3 "${srcdir}/display_intersection.py" \
"${builddir}/complex_intersection.json"  \
--table-label "timer_durations_03" \
--timer-durations="${builddir}/timer_durations_03.tex" 

# Generate the table files which detail the operation of the
# finite state machines for the various scenarios.  In case
# we wish to show an animation also create the events csv file
# and the last events time files that the animation renderer needs.
idle_01_table.tex : simulate_traffic.py one_way_bridge.json
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/one_way_bridge.json" --clock-step 0.001 \
--explain-state-transitions --only-important \
--table-level 4 --table-file "${builddir}/idle_01_table.tex" --duration 200  \
--table-caption "Power On to Idle Condition, example 01"

idle_03_table.tex : simulate_traffic.py complex_intersection.json
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" --clock-step 0.001 \
--explain-state-transitions --show-substates \
--table-level 4 --table-file "${builddir}/idle_03_table.tex" --duration 200  \
--table-caption "Power On to Idle Condition, example 03"

bridge_one_car_table.tex bridge_one_car_animation_01.csv &: \
simulate_traffic.py one_way_bridge.json bridge_one_car_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/one_way_bridge.json" --clock-step 0.001 \
--table-level 4 --table-file "${builddir}/bridge_one_car_table.tex" \
--duration 400 \
--explain-state-transitions --only-important \
--table-start 199 --script "${srcdir}/bridge_one_car_script.txt" \
--events-file "$(builddir)/bridge_one_car_animation_01.csv" \
--last-event-time "${builddir}/last_event_time_bridge_one_car_animation.txt" \
--table-caption "One Car Passes Over the Single-lane Bridge"

bridge_two_cars_table.tex bridge_two_cars_animation_01.csv &: \
simulate_traffic.py one_way_bridge.json bridge_two_cars_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/one_way_bridge.json" --clock-step 0.001 \
--table-level 4 --table-file "${builddir}/bridge_two_cars_table.tex" \
--duration 400 \
--explain-state-transitions --only-important \
--table-start 199 --script "${srcdir}/bridge_two_cars_script.txt" \
--events-file "$(builddir)/bridge_two_cars_animation_01.csv" \
--last-event-time "${builddir}/last_event_time_bridge_two_cars_animation.txt" \
--table-caption "Two Cars Pass Over the Single-lane Bridge"

four_corners_many_table.tex four_corners_many_animation_02.csv &: \
simulate_traffic.py four_corners.json four_corners_many_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/four_corners.json" --clock-step 0.001 \
--table-level 4 --table-file "${builddir}/four_corners_many_table.tex" \
--duration 400 --explain-state-transitions --only-important \
--table-start 199 --script "${srcdir}/four_corners_many_script.txt" \
--events-file "$(builddir)/four_corners_many_animation_02.csv" \
--last-event-time \
"${builddir}/last_event_time_four_corners_many_animation.txt" \
--table-caption "Traffic from All Directions"

left_turn_delayed_table.tex left_turn_delayed_animation_03.csv &: \
simulate_traffic.py complex_intersection.json  \
left_turn_delayed_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" --clock-step 0.001 \
--table-level 4 --table-file "${builddir}/left_turn_delayed_table.tex" \
--events-file "$(builddir)/left_turn_delayed_animation_03.csv" \
--last-event-time \
"${builddir}/last_event_time_left_turn_delayed_animation.txt" \
--duration 400 --table-start 199 --explain-state-transitions --show-substates \
--script "${srcdir}/left_turn_delayed_script.txt" \
--table-caption "Left Turn Delayed"

left_turn_table.tex left_turn_animation_03.csv &: \
simulate_traffic.py complex_intersection.json  \
left_turn_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" --clock-step 0.001 \
--table-level 4 --table-file "${builddir}/left_turn_table.tex" \
--events-file "$(builddir)/left_turn_animation_03.csv" \
--last-event-time \
"${builddir}/last_event_time_left_turn_animation.txt" \
--duration 400 --table-start 199 --explain-state-transitions --show-substates \
--script "${srcdir}/left_turn_script.txt" \
--table-caption "Left Turn"

pedestrian_table.tex pedestrian_animation.csv &: simulate_traffic.py \
complex_intersection.json pedestrian_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" --table-level 4 \
--table-file "${builddir}/pedestrian_table.tex" --duration 400 \
--events-file "$(builddir)/pedestrian_animation_03.csv" \
--last-event-time "${builddir}/last_event_time_pedestrian_animation.txt" \
--clock-step 0.001 --explain-state-transitions --show-substates \
--table-start 199 --script "${srcdir}/pedestrian_script.txt" \
--table-caption "Pedestrian Crosses"

pedestrian_and_left_turn_table.tex \
pedestrian_and_left_turn_animation_03.csv &: simulate_traffic.py \
complex_intersection.json pedestrian_and_left_turn_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" --table-level 4 \
--table-file "${builddir}/pedestrian_and_left_turn_table.tex" --duration 400 \
--events-file "$(builddir)/pedestrian_and_left_turn_animation_03.csv" \
--last-event-time \
"${builddir}/last_event_time_pedestrian_and_left_turn_animation.txt" \
--clock-step 0.001 --explain-state-transitions --show-substates \
--table-start 199 --script "${srcdir}/pedestrian_and_left_turn_script.txt" \
--table-caption "Pedestrian then Left Turn"

multiple_table.tex multiple_animation_03.csv &: simulate_traffic.py \
complex_intersection.json multiple_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" \
--table-level 2 --clock-step 0.001 \
--explain-state-transitions --show-substates \
--events-file "$(builddir)/multiple_animation_03.csv" \
--last-event-time "${builddir}/last_event_time_multiple_animation.txt" \
--table-file "${builddir}/multiple_table.tex" --duration 400 \
--table-start 199 --script "${srcdir}/multiple_script.txt" \
--table-caption "Multiple Arrivals"

# Some of the pictures have been created in inkscape.  Convert them
# to PDF files for the document or to png files for the renderer.

%.pdf : %.svg ; inkscape --export-type=pdf --export-dpi=4800 \
"${srcdir}/$(<F)" -o "${builddir}/$(@F)"

%.png : %.svg ; inkscape --export-type=png --export-png-color-mode=RGBA_16 \
--export-dpi=4800 "${srcdir}/$(<F)" -o "${builddir}/$(@F)"

# Buld the PDF on demand, if requested.
pdf-local: traffic_control_signals.pdf
.PHONEY: pdf-local

# Include the PGP signature file in the repository.  Create it using
# "make signature".
signature : ${PACKAGE}-${VERSION}.tar.gz.asc
.PHONEY: signature

${PACKAGE}-${VERSION}.tar.gz.asc : ${PACKAGE}-${VERSION}.tar.gz
	rm -f ${PACKAGE}-*.tar.gz.asc
	gpg2 --detach-sign --armor ${PACKAGE}-${VERSION}.tar.gz

# Support make check and make distcheck
dist_check_DATA = check_expected_output.txt left_turn_script.txt
dist_check_SCRIPTS = verify_files_template.sh

TESTS = verify_files.sh
verify_files.sh : verify_files_template.sh check_output.txt 
	cp "$(srcdir)/verify_files_template.sh" verify_files.sh
	if [ ! -r "check_expected_output.txt" ] ; then cp "$(srcdir)/check_expected_output.txt" check_expected_output.txt ; touch copied_from_srcdir ; fi
	chmod +x verify_files.sh

check_output.txt : simulate_traffic.py complex_intersection.json \
left_turn_script.txt
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" \
--script "${srcdir}/left_turn_script.txt" --clock-step 0.001 \
--explain-state-transitions --show-substates \
--duration 1200 --verbose 2 | tee "${builddir}/check_output.txt"

# Animations illustrate a scenario.  The csv file describes where each
# object is located with the passage of time.
# When building an animation, indicate which example intersection the
# script applies to by following the name of the script with "animation_01"
# for the one-way bridge example, "animation_02" for the four corners example,
# and "animation_03" for the complex intersection example.
#
# Some of the animation CSV files are produced as a byproduct of creating
# the corresponding events table.  The following CSV rules are for those
# that aren't.
%_animation_01.csv : %_script.txt simulate_traffic.py one_way_bridge.json
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/one_way_bridge.json" --clock-step 0.001 \
--script "$<" --duration 1200 --events-file "$@" \
--last-event-time "${builddir}/last_event_time_$(*F)_animation.txt"

%_animation_02.csv : %_script.txt simulate_traffic.py four_corners.json
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/four_corners.json" --clock-step 0.001 \
--script "$<" --duration 1200 --events-file "$@" \
--last-event-time "${builddir}/last_event_time_$(*F)_animation.txt"

%_animation_03.csv : %_script.txt simulate_traffic.py complex_intersection.json
	python3 "${srcdir}/simulate_traffic.py" \
--intersection "${builddir}/complex_intersection.json" --clock-step 0.001 \
--script "$<" --duration 1200 --events-file "$@" \
--last-event-time "${builddir}/last_event_time_$(*F)_animation.txt"

# Create the background image for the animations.
background_01.png : draw_background.py one_way_bridge.json
	python3 "${srcdir}/draw_background.py" \
--intersection "${builddir}/one_way_bridge.json" \
--background "${builddir}/background_01.png"

background_02.png : draw_background.py four_corners.json
	python3 "${srcdir}/draw_background.py" \
--intersection "${builddir}/four_corners.json" \
--background "${builddir}/background_02.png"

background_03.png : draw_background.py complex_intersection.json
	python3 "${srcdir}/draw_background.py" \
--intersection "${builddir}/complex_intersection.json" \
--background "${builddir}/background_03.png"

# Render the animation as individual images.

# One-way bridge example.
%_animation_01.pdf : %_animation_01.csv \
background_01.png \
process_events.py build_animation.sh build_animation_serial.sh \
render_animation.sh \
signal_ccc_Green.png signal_ccc_Red.png \
signal_ccc_Yellow.png signal_ccu_Green.png signal_ccu_Red.png \
signal_ccu_Yellow.png signal_Dark_3.png signal_Dark_4.png \
signal_cccl_Green.png signal_cccl_Red.png signal_cccl_Yellow.png \
signal_llll_Flashing_Yellow.png signal_llll_Green.png signal_llll_Red.png \
signal_llll_Yellow.png signal_rrr_Green.png signal_rrr_Red.png \
signal_rrr_Yellow.png MUTCD_Ped_Signal_-_Hand_with_timer.png \
MUTCD_Ped_Signal_-_Hand_with_timer-00.png \
MUTCD_Ped_Signal_-_Hand_with_timer-01.png \
MUTCD_Ped_Signal_-_Hand_with_timer-02.png \
MUTCD_Ped_Signal_-_Hand_with_timer-03.png \
MUTCD_Ped_Signal_-_Hand_with_timer-04.png \
MUTCD_Ped_Signal_-_Hand_with_timer-05.png \
MUTCD_Ped_Signal_-_Hand_with_timer-06.png \
MUTCD_Ped_Signal_-_Hand_with_timer-07.png \
MUTCD_Ped_Signal_-_Hand_with_timer-08.png \
MUTCD_Ped_Signal_-_Hand_with_timer-09.png \
MUTCD_Ped_Signal_-_Hand_with_timer-10.png \
MUTCD_Ped_Signal_-_Hand_with_timer-11.png \
MUTCD_Ped_Signal_-_Hand_with_timer-12.png \
MUTCD_Ped_Signal_-_Hand_with_timer-13.png \
MUTCD_Ped_Signal_-_Hand_with_timer-14.png \
MUTCD_Ped_Signal_-_Hand_with_timer-15.png \
MUTCD_Ped_Signal_-_Hand_with_timer-16.png \
MUTCD_Ped_Signal_-_Hand_with_timer-17.png \
MUTCD_Ped_Signal_-_Hand_with_timer-18.png \
MUTCD_Ped_Signal_-_Hand_with_timer-19.png \
MUTCD_Ped_Signal_-_Hand_with_timer-20.png \
MUTCD_Ped_Signal_-_Hand_with_timer-21.png \
MUTCD_Ped_Signal_-_Hand_with_timer-22.png \
MUTCD_Ped_Signal_-_Hand_with_timer-23.png \
MUTCD_Ped_Signal_-_Hand_with_timer-24.png \
MUTCD_Ped_Signal_-_Hand_with_timer-25.png \
MUTCD_Ped_Signal_-_Steady_hand.png MUTCD_Ped_Signal_-_Walk.png \
car-38800411-right.png \
car-38800411-up.png truck-51893967-up.png truck-51893967-right.png \
man_walking_right.png
	bash "${srcdir}/build_animation.sh" "${srcdir}/render_animation.sh" \
"${srcdir}/process_events.py" \
"$<" "${builddir}/last_event_time_$(*F)_animation.txt" \
"${builddir}/animation_$(*F)_temp" \
"${builddir}/one_way_bridge.json" "${builddir}/background_01.png" 30
	find "${builddir}/animation_$(*F)_temp/" -type f -print0 | \
xargs --null realpath --zero | sort -z \
> "${builddir}/frames_of_$(*F)_animation.txt"
	img2pdf -o "$@" --from-file "${builddir}/frames_of_$(*F)_animation.txt"

%_animation_01.mkv : %_animation_01.pdf
	bash "${srcdir}/build_video.sh" "$@" \
"${builddir}/animation_$(*F)_temp" 30

# Four corners example.
%_animation_02.pdf : %_animation_02.csv \
background_02.png \
process_events.py build_animation.sh build_animation_serial.sh \
render_animation.sh \
signal_ccc_Green.png signal_ccc_Red.png \
signal_ccc_Yellow.png signal_ccu_Green.png signal_ccu_Red.png \
signal_ccu_Yellow.png signal_Dark_3.png signal_Dark_4.png \
signal_cccl_Green.png signal_cccl_Red.png signal_cccl_Yellow.png \
signal_llll_Flashing_Yellow.png signal_llll_Green.png signal_llll_Red.png \
signal_llll_Yellow.png signal_rrr_Green.png signal_rrr_Red.png \
signal_rrr_Yellow.png MUTCD_Ped_Signal_-_Hand_with_timer.png \
MUTCD_Ped_Signal_-_Hand_with_timer-00.png \
MUTCD_Ped_Signal_-_Hand_with_timer-01.png \
MUTCD_Ped_Signal_-_Hand_with_timer-02.png \
MUTCD_Ped_Signal_-_Hand_with_timer-03.png \
MUTCD_Ped_Signal_-_Hand_with_timer-04.png \
MUTCD_Ped_Signal_-_Hand_with_timer-05.png \
MUTCD_Ped_Signal_-_Hand_with_timer-06.png \
MUTCD_Ped_Signal_-_Hand_with_timer-07.png \
MUTCD_Ped_Signal_-_Hand_with_timer-08.png \
MUTCD_Ped_Signal_-_Hand_with_timer-09.png \
MUTCD_Ped_Signal_-_Hand_with_timer-10.png \
MUTCD_Ped_Signal_-_Hand_with_timer-11.png \
MUTCD_Ped_Signal_-_Hand_with_timer-12.png \
MUTCD_Ped_Signal_-_Hand_with_timer-13.png \
MUTCD_Ped_Signal_-_Hand_with_timer-14.png \
MUTCD_Ped_Signal_-_Hand_with_timer-15.png \
MUTCD_Ped_Signal_-_Hand_with_timer-16.png \
MUTCD_Ped_Signal_-_Hand_with_timer-17.png \
MUTCD_Ped_Signal_-_Hand_with_timer-18.png \
MUTCD_Ped_Signal_-_Hand_with_timer-19.png \
MUTCD_Ped_Signal_-_Hand_with_timer-20.png \
MUTCD_Ped_Signal_-_Hand_with_timer-21.png \
MUTCD_Ped_Signal_-_Hand_with_timer-22.png \
MUTCD_Ped_Signal_-_Hand_with_timer-23.png \
MUTCD_Ped_Signal_-_Hand_with_timer-24.png \
MUTCD_Ped_Signal_-_Hand_with_timer-25.png \
MUTCD_Ped_Signal_-_Steady_hand.png MUTCD_Ped_Signal_-_Walk.png \
car-38800411-right.png \
car-38800411-up.png truck-51893967-up.png truck-51893967-right.png \
man_walking_right.png
	bash "${srcdir}/build_animation.sh" "${srcdir}/render_animation.sh" \
"${srcdir}/process_events.py" \
"$<" "${builddir}/last_event_time_$(*F)_animation.txt" \
"${builddir}/animation_$(*F)_temp" \
"${builddir}/four_corners.json" "${builddir}/background_02.png" 30
	find "${builddir}/animation_$(*F)_temp/" -type f -print0 | \
xargs --null realpath --zero | sort -z \
> "${builddir}/frames_of_$(*F)_animation.txt"
	img2pdf -o "$@" --from-file "${builddir}/frames_of_$(*F)_animation.txt"

%_animation_02.mkv : %_animation_02.pdf
	bash "${srcdir}/build_video.sh" "$@" \
"${builddir}/animation_$(*F)_temp" 30

# Complex intersection example
%_animation_03.pdf : %_animation_03.csv \
background_03.png \
process_events.py build_animation.sh build_animation_serial.sh \
render_animation.sh \
signal_ccc_Green.png signal_ccc_Red.png \
signal_ccc_Yellow.png signal_ccu_Green.png signal_ccu_Red.png \
signal_ccu_Yellow.png signal_Dark_3.png signal_Dark_4.png \
signal_cccl_Green.png signal_cccl_Red.png signal_cccl_Yellow.png \
signal_llll_Flashing_Yellow.png signal_llll_Green.png signal_llll_Red.png \
signal_llll_Yellow.png signal_rrr_Green.png signal_rrr_Red.png \
signal_rrr_Yellow.png MUTCD_Ped_Signal_-_Hand_with_timer.png \
MUTCD_Ped_Signal_-_Hand_with_timer-00.png \
MUTCD_Ped_Signal_-_Hand_with_timer-01.png \
MUTCD_Ped_Signal_-_Hand_with_timer-02.png \
MUTCD_Ped_Signal_-_Hand_with_timer-03.png \
MUTCD_Ped_Signal_-_Hand_with_timer-04.png \
MUTCD_Ped_Signal_-_Hand_with_timer-05.png \
MUTCD_Ped_Signal_-_Hand_with_timer-06.png \
MUTCD_Ped_Signal_-_Hand_with_timer-07.png \
MUTCD_Ped_Signal_-_Hand_with_timer-08.png \
MUTCD_Ped_Signal_-_Hand_with_timer-09.png \
MUTCD_Ped_Signal_-_Hand_with_timer-10.png \
MUTCD_Ped_Signal_-_Hand_with_timer-11.png \
MUTCD_Ped_Signal_-_Hand_with_timer-12.png \
MUTCD_Ped_Signal_-_Hand_with_timer-13.png \
MUTCD_Ped_Signal_-_Hand_with_timer-14.png \
MUTCD_Ped_Signal_-_Hand_with_timer-15.png \
MUTCD_Ped_Signal_-_Hand_with_timer-16.png \
MUTCD_Ped_Signal_-_Hand_with_timer-17.png \
MUTCD_Ped_Signal_-_Hand_with_timer-18.png \
MUTCD_Ped_Signal_-_Hand_with_timer-19.png \
MUTCD_Ped_Signal_-_Hand_with_timer-20.png \
MUTCD_Ped_Signal_-_Hand_with_timer-21.png \
MUTCD_Ped_Signal_-_Hand_with_timer-22.png \
MUTCD_Ped_Signal_-_Hand_with_timer-23.png \
MUTCD_Ped_Signal_-_Hand_with_timer-24.png \
MUTCD_Ped_Signal_-_Hand_with_timer-25.png \
MUTCD_Ped_Signal_-_Steady_hand.png MUTCD_Ped_Signal_-_Walk.png \
car-38800411-right.png \
car-38800411-up.png truck-51893967-up.png truck-51893967-right.png \
man_walking_right.png
	bash "${srcdir}/build_animation.sh" "${srcdir}/render_animation.sh" \
"${srcdir}/process_events.py" \
"$<" "${builddir}/last_event_time_$(*F)_animation.txt" \
"${builddir}/animation_$(*F)_temp" \
"${builddir}/complex_intersection.json" "${builddir}/background_03.png" 30
	find "${builddir}/animation_$(*F)_temp/" -type f -print0 | \
xargs --null realpath --zero | sort -z \
> "${builddir}/frames_of_$(*F)_animation.txt"
	img2pdf -o "$@" --from-file "${builddir}/frames_of_$(*F)_animation.txt"

%_animation_03.mkv : %_animation_03.pdf
	bash "${srcdir}/build_video.sh" "$@" \
"${builddir}/animation_$(*F)_temp" 30

# When removing files, also remove the followins:
CLEANFILES = \
_minted-traffic_control_signals \
svg-inkscape \
traffic_control_signals.aux \
traffic_control_signals.bbl \
traffic_control_signals.blg \
traffic_control_signals.brf \
traffic_control_signals.log \
traffic_control_signals.out \
traffic_control_signals.pdf \
state_diagram.eps \
state_diagram-eps-converted-to.pdf \
finite_state_machine.json \
complex_intersection.json \
one_way_bridge.json \
four_corners.json \
complex_intersection_unsmoothed.json \
one_way_bridge_unsmoothed.json \
four_corners_unsmoothed.json \
red_state_table.tex \
green_state_table.tex \
yellow_state_table.tex \
lamp_map_names_*.tex\
sensor_map_*.tex \
timer_durations_*.tex \
MUTCD_Ped_Signal_-_Hand_with_timer*.pdf \
MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer*.png \
MUTCD_Ped_Signal_-_Steady_hand.png \
MUTCD_Ped_Signal_-_Walk.png \
signal_*.pdf \
signal_*.png \
car-38800411-right.png \
car-38800411-up.png \
truck-51893967-right.png \
truck-51893967-up.png \
pedestrian.png \
man_walking_right.png \
background_*.png \
*_table.tex \
*_animation_*.csv \
*_animation_*.mkv \
*_animation_*.pdf \
last_event_time_*_animation.txt \
check_output.txt \
verify_files.sh \
files.txt \
frames_of_*_animation.txt \
*trace.txt 

clean-local: clean-local-check
.PHONEY: clean-local-check
clean-local-check:
	if [ -e "copied_from_srcdir" ] ; then rm -f check_expected_output.txt ; rm copied_from_srcdir ; fi
	rm -rf autom4te.cache
	rm -rf animation_*_temp
	rm -f trace*.txt
	rm -f *~

# end of file Makefile.am
