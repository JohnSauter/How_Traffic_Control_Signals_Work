#!/bin/bash
# file: build_animation_serial.sh, author: John Sauter,
# date: September 10, 2025.

# Construct an animation from an event log.

renderer="${1}"
processor="${2}"
source="${3}"
last_event_time_file=${4}
animation_temp="${5}"
intersection_file="${6}"
background_image="${7}"
frame_rate="${8}"

last_event_time=$(<${last_event_time_file})
echo "last event time " ${last_event_time}

# Start time is in seconds.
start_time="200"

rm -rf ${animation_temp}/
mkdir ${animation_temp}

let "start_frame = 0"
# Duration in seconds.
let "temp = ${last_event_time} - ${start_time}"
# Duration in frames
let "end_frame = ${temp} * ${frame_rate}"

bash "${renderer}" "${processor}" "${source}" "${animation_temp}" \
     ${start_time} ${start_frame} ${end_frame} \
     ${frame_rate} ${background_image} ${intersection_file}

# End of file build_animation_serial.sh
