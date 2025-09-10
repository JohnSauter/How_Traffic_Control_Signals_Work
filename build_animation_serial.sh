#!/bin/bash
# file: build_animation_serial.sh, author: John Sauter, date: August 17, 2025.

# Construct an animation from an event log.

source="${1}"
last_event_time_file=${2}
animation_temp="${3}"
intersection_file="${4}"
background_image="${5}"

last_event_time=$(<${last_event_time_file})
echo "last event time " ${last_event_time}

# Start time is in seconds.
start_time="200"

# Frame rate is the number of frames per second.
frame_rate="30"

rm -rf ${animation_temp}/
mkdir ${animation_temp}

let "start_frame = 0"
# Duration in seconds.
let "temp = ${last_event_time} - ${start_time}"
# Duration in frames
let "end_frame = ${temp} * ${frame_rate}"

bash "render_animation.sh" "${source}" "${animation_temp}" \
     ${start_time} ${start_frame} ${end_frame} \
     ${frame_rate} ${background_image} ${intersection_file}

# End of file build_animation_serial.sh
