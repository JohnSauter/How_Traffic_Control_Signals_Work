# File: Makefile.am, author: John Sauter, date: December 25, 2024.
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
fig4d_01.gif \
fig4d_02.gif \
fig4d_06.gif \
fig4d_07.gif \
fig4d_08.gif \
fig4d_09.gif \
fig4d_10.gif \
fig4d_11.gif \
fig4d_12.gif \
fig4d_13.gif \
fig4d_14.gif \
fig4d_15.gif \
fig4d_16.gif \
fig4d_17.gif \
fig4d_18.gif \
fig4d_19.gif \
fig4d_20_1.gif \
fig4d_20_2.gif \
fig4d_20_3.gif \
traffic_signal_3_lamps.svg \
fix_files.sh autogen.sh \
left_turn_script.txt \
legalcode.txt mutcd11thedition.pdf \
multiple_script.txt \
MUTCD_Ped_Signal_-_Hand_with_timer.svg \
MUTCD_Ped_Signal_-_Steady_hand.svg \
MUTCD_Ped_Signal_-_Walk.svg \
pedestrian_and_left_turn_script.txt \
pedestrian_script.txt \
references.bib \
Signal_Timing_Manual_Second_Edition_22097.pdf \
traffic_control_signals.py \
traffic_control_signals.tex \
traffic_control_signals_state_diagram.txt 

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
traffic_control_signals_state_diagram.eps red_state_table.tex \
green_state_table.tex yellow_state_table.tex lamp_map_names.tex \
sensor_map.tex idle_log.tex left_turn_log.tex \
pedestrian_log.tex pedestrian_and_left_turn_log.tex multiple_log.tex \
fig4d_02.eps fig4d_09.eps fig4d_12.eps fig4d_17.eps \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf traffic_signal_3_lamps.pdf
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
LICENSE legalcode.txt traffic_control_signals_state_diagram.eps \
red_state_table.tex green_state_table.tex yellow_state_table.tex \
lamp_map_names.tex sensor_map.tex idle_log.tex left_turn_log.tex \
pedestrian_log.tex pedestrian_and_left_turn_log.tex multiple_log.tex \
fig4d_02.eps fig4d_09.eps fig4d_12.eps fig4d_17.eps \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf traffic_signal_3_lamps.pdf
	echo " " >${builddir}/traffic_control_signals.bbl
	TEXINPUTS=${TEXINPUTS}:${builddir}:${srcdir} lualatex -shell-escape \
${srcdir}/traffic_control_signals.tex
	BIBINPUTS=${TEXINPUTS}:${builddir}:${srcdir} bibtex \
${builddir}/traffic_control_signals.aux

# Build a chart of states of the finite state machines
traffic_control_signals_state_diagram.eps : \
traffic_control_signals_state_diagram.txt
	neato -Teps ${srcdir}/traffic_control_signals_state_diagram.txt \
-o ${builddir}/traffic_control_signals_state_diagram.eps

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

# Generate the log files which summarize the finite state machines operation.
idle_log.tex : traffic_control_signals.py
	python3 ${srcdir}/traffic_control_signals.py --log-level 4 \
--log-file ${builddir}/idle_log.tex --duration 200  \
--log-caption "Power On to Idle State"

left_turn_log.tex : traffic_control_signals.py left_turn_script.txt
	python3 ${srcdir}/traffic_control_signals.py --log-level 4 \
--log-file ${builddir}/left_turn_log.tex --duration 400 --log-start 199 \
--script ${srcdir}/left_turn_script.txt --log-caption "Left Turn"

pedestrian_log.tex : traffic_control_signals.py pedestrian_script.txt
	python3 ${srcdir}/traffic_control_signals.py --log-level 3 \
--log-file ${builddir}/pedestrian_log.tex --duration 400 --log-start 199 \
--script ${srcdir}/pedestrian_script.txt --log-caption "Pedestrian Crosses"

pedestrian_and_left_turn_log.tex : traffic_control_signals.py \
pedestrian_and_left_turn_script.txt
	python3 ${srcdir}/traffic_control_signals.py --log-level 3 \
--log-file ${builddir}/pedestrian_and_left_turn_log.tex --duration 400 \
--log-start 199 --script ${srcdir}/pedestrian_and_left_turn_script.txt \
--log-caption "Pedestrian then Left Turn"

multiple_log.tex : traffic_control_signals.py multiple_script.txt
	python3 ${srcdir}/traffic_control_signals.py --log-level 2 \
--log-file ${builddir}/multiple_log.tex --duration 400 --log-start 199 \
--script ${srcdir}/multiple_script.txt --log-caption "Many Events"

fig4d_02.eps : fig4d_02.gif
	magick ${srcdir}/fig4d_02.gif ${builddir}/fig4d_02.eps

fig4d_09.eps : fig4d_09.gif
	magick ${srcdir}/fig4d_09.gif ${builddir}/fig4d_09.eps

fig4d_12.eps : fig4d_12.gif
	magick ${srcdir}/fig4d_12.gif ${builddir}/fig4d_12.eps

fig4d_17.eps : fig4d_17.gif
	magick ${srcdir}/fig4d_17.gif ${builddir}/fig4d_17.eps

%.pdf : %.svg ; inkscape --export-type=pdf ${srcdir}/$(<F) -o ${builddir}/$(@F)

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
traffic_control_signals_state_diagram.eps \
traffic_control_signals_state_diagram-eps-converted-to.pdf \
red_state_table.tex \
green_state_table.tex \
yellow_state_table.tex \
lamp_map_names.tex \
sensor_map.tex \
fig4d_*.eps \
fig4d_*-eps-converted-to.pdf \
MUTCD_Ped_Signal_-_Hand_with_timer.pdf \
MUTCD_Ped_Signal_-_Steady_hand.pdf \
MUTCD_Ped_Signal_-_Walk.pdf \
traffic_signal_3_lamps.pdf \
*_log.tex \
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
