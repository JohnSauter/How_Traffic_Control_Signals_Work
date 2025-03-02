#!/bin/bash
# File: render_animation.sh, author: John Sauter, date: March 2, 2025.

# Argument 1 is the source file for the events, 2 is the directory into which
# we write the frames of the animation, 3 is the start time,
# 4 is the duration, 5 is the number# of the first frame,
# 6 is the number of the last frame, 7 is the frame rate.
python3 process_events.py --events-file ${1} --animation ${2} \
	--start-time ${3} --duration ${4} --start-frame ${5} \
	--end-frame ${6} --FPS ${7} --verbose 3 \
	--trace-file foo_${5}_trace.txt

# End of file render_animation.sh
