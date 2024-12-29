# File: Makefile.am, author: John Sauter, date: December 27, 2024.
#
# Build traffic_control_signals.pdf

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

# The main target is the file traffic_control_signals.pdf
all: traffic_control_signals.pdf
.PHONEY: all

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
legalcode.txt mutcd11thedition.pdf \
multiple_script.txt \
MUTCD_Ped_Signal_-_Hand_with_timer.svg \
MUTCD_Ped_Signal_-_Steady_hand.svg \
MUTCD_Ped_Signal_-_Walk.svg \
pedestrian_and_left_turn_script.txt \
pedestrian_script.txt \
events_script.txt \
references.bib \
Signal_Timing_Manual_Second_Edition_22097.pdf \
traffic_control_signals.py \
traffic_control_signals.tex \
state_diagram.txt 

# Distribute the shell script which builds the RPMs.
EXTRA_DIST += build_RPMs.sh

# Run it if the developer types "make RPMs".
.phoney: RPMs
RPMs:
	bash build_RPMs.sh

# The spec file is ueed to build RPMs for RPM-based distributions
# of GNU/Linux, including RHEL, CENTOS and Fedora.
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
green_state_table.tex yellow_state_table.tex lamp_map_names.tex \
sensor_map.tex idle_table.tex left_turn_table.tex \
pedestrian_table.tex pedestrian_and_left_turn_table.tex multiple_table.tex \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf signal_ccc.pdf signal_ccu.pdf signal_rrr.pdf \
signal_cccl.pdf signal_llll.pdf
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex -shell-escape \
${srcdir}/traffic_control_signals.tex
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex -shell-escape \
${srcdir}/traffic_control_signals.tex
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex -shell-escape \
${srcdir}/traffic_control_signals.tex
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex -shell-escape \
${srcdir}/traffic_control_signals.tex

# Build the bbl file by running LaTeX without it, then running bibtex.
traffic_control_signals.bbl : traffic_control_signals.tex references.bib \
LICENSE legalcode.txt state_diagram.eps \
red_state_table.tex green_state_table.tex yellow_state_table.tex \
lamp_map_names.tex sensor_map.tex idle_table.tex left_turn_table.tex \
pedestrian_table.tex pedestrian_and_left_turn_table.tex multiple_table.tex \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf signal_ccc.pdf signal_ccu.pdf signal_rrr.pdf \
signal_cccl.pdf signal_llll.pdf
	echo " " >${builddir}/traffic_control_signals.bbl
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex -shell-escape \
${srcdir}/traffic_control_signals.tex
	BIBINPUTS=${TEXINPUTS}:${builddir}:${srcdir} bibtex \
${builddir}/traffic_control_signals.aux

# Build a chart of states of the finite state machines
state_diagram.eps : state_diagram.txt
	neato -Teps ${srcdir}/state_diagram.txt \
-o ${builddir}/state_diagram.eps

# Generate the state tables from the implementation's finite state machine.
red_state_table.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py \
--red=${builddir}/red_state_table.tex

green_state_table.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py \
--green=${builddir}/green_state_table.tex 

yellow_state_table.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py \
--yellow=${builddir}/yellow_state_table.tex 

lamp_map_names.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py \
--lamp-map=${builddir}/lamp_map_names.tex 

sensor_map.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py \
--sensor-map=${builddir}/sensor_map.tex 

# Generate the table files which detail the finite state machines operation.
idle_table.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py --table-level 4 \
--table-file ${builddir}/idle_table.tex --duration 200  \
--table-caption "Power On to Idle State"

left_turn_table.tex : traffic_control_signals.py left_turn_script.txt
	python3 ${srcdir}/traffic_control_signals.py --table-level 4 \
--table-file ${builddir}/left_turn_table.tex --duration 400 --table-start 199 \
--script ${srcdir}/left_turn_script.txt --table-caption "Left Turn"

pedestrian_table.tex : traffic_control_signals.py pedestrian_script.txt
	python3 ${srcdir}/traffic_control_signals.py --table-level 3 \
--table-file ${builddir}/pedestrian_table.tex --duration 400 \
--table-start 199 --script ${srcdir}/pedestrian_script.txt \
--table-caption "Pedestrian Crosses"

pedestrian_and_left_turn_table.tex : traffic_control_signals.py \
pedestrian_and_left_turn_script.txt
	python3 ${srcdir}/traffic_control_signals.py --table-level 3 \
--table-file ${builddir}/pedestrian_and_left_turn_table.tex --duration 400 \
--table-start 199 --script ${srcdir}/pedestrian_and_left_turn_script.txt \
--table-caption "Pedestrian then Left Turn"

multiple_table.tex : traffic_control_signals.py multiple_script.txt
	python3 ${srcdir}/traffic_control_signals.py --table-level 2 \
--table-file ${builddir}/multiple_table.tex --duration 400 --table-start 199 \
--script ${srcdir}/multiple_script.txt --table-caption "Many Events"

# Some of the diagrams have been created in inkscape.  Convert them
# to PDF files for the document.

%.pdf : %.svg ; inkscape --export-type=pdf --export-dpi=4800 \
${srcdir}/$(<F) -o ${builddir}/$(@F)

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
dist_check_DATA = check_expected_output.txt heavy_script.txt
dist_check_SCRIPTS = verify_files_template.sh

TESTS = verify_files.sh
verify_files.sh : verify_files_template.sh check_output.txt 
	cp $(srcdir)/verify_files_template.sh verify_files.sh
	if [ ! -r "check_expected_output.txt" ] ; then cp $(srcdir)/check_expected_output.txt check_expected_output.txt ; touch copied_from_srcdir ; fi
	chmod +x verify_files.sh

check_output.txt : traffic_control_signals.py heavy_script.txt
	python3 ${srcdir}/traffic_control_signals.py \
--script ${srcdir}/heavy_script.txt \
--duration 1000 --verbose 4 | tee ${builddir}/check_output.txt

# A secondary target is the event output, for post-processing.
events: events.csv
.PHONEY: events

events.csv : traffic_control_signals.py events_script.txt
	python3 ${srcdir}/traffic_control_signals.py \
--script ${srcdir}/events_script.txt \
--duration 1000 --events-file events.csv

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
red_state_table.tex \
green_state_table.tex \
yellow_state_table.tex \
lamp_map_names.tex \
sensor_map.tex \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf \
MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf \
signal_ccc.pdf \
signal_ccu.pdf \
signal_rrr.pdf \
signal_cccl.pdf \
signal_llll.pdf \
*_table.tex \
events.csv \
check_output.txt \
verify_files.sh \
*trace.txt 

clean-local: clean-local-check
.PHONEY: clean-local-check
clean-local-check:
	if [ -e "copied_from_srcdir" ] ; then rm -f check_expected_output.txt ; rm copied_from_srcdir ; fi
	rm -rf autom4te.cache
	rm -f trace*.txt
	rm -f *~

# end of file Makefile.am
