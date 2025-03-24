#!/bin/bash
# File: render_animation.sh, author: John Sauter, date: March 23, 2025.

# Argument 1 is the source file for the events, 2 is the directory into which
# we write the frames of the animation, 3 is the start time,
# 4 is the number# of the first frame,
# 5 is the number of the last frame, 6 is the frame rate.
python3 process_events.py --events-file ${1} --animation ${2} \
	--start-time ${3} --start-frame ${4} \
	--end-frame ${5} --FPS ${6} --verbose 3

# End of file render_animation.sh
