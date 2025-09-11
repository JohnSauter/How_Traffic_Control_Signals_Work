#!/bin/bash
# File: render_animation.sh, author: John Sauter, date: September 10, 2025.

# 1 is the name of the events-processing script,
# 2 is the source file for the events,
# 3 is the directory into which we write the frames of the animation,
# 4 is the start time,
# 5 is the number of the first frame,
# 6 is the number of the last frame,
# 7 is the frame rate,
# 8 is the name of the background file.
# 9 is the name of the intersection file.
python3 "${1}" --events-file "${2}" --animation "${3}" \
	--start-time ${4} --start-frame ${5} \
	--end-frame ${6} --FPS ${7} --background "${8}" --intersection "${9}" \
	--verbose 1

# End of file render_animation.sh
