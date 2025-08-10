#!/bin/bash
# file: build_animation.sh, author: John Sauter, date: July 20, 2025.

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

# Batch size and count are in numbers of frames.
# Each batch processes 100 frames.
batch_size="100"

# Compute the number of batches from the duration of the animation.

# Duration in seconds.
let "temp = ${last_event_time} - ${start_time}"
# Duration in frames
let "temp = ${temp} * ${frame_rate}"
#Number of batches, rounded down
let "temp = ${temp} / ${batch_size}"
# Round up.
let "batch_count = ${temp} + 1"
echo "batch count "  ${batch_count}

rm -rf ${animation_temp}/
mkdir ${animation_temp}

for (( counter=0; counter<=${batch_count}; counter+=1 )); do
    let "temp = ${counter} * ${batch_size}"
    let "start_frame = ${temp}"
    let "temp= ${counter} + 1"
    let "temp= ${temp} * ${batch_size}"
    let "end_frame= ${temp} - 1"
    parallel --semaphore --ungroup --halt now,fail=1 --jobs 25 --quote \
	     bash "render_animation.sh" "${source}" "${animation_temp}" \
	     ${start_time} ${start_frame} ${end_frame} \
	     ${frame_rate} ${background_image} ${intersection_file} ";"
done
parallel --semaphore --wait

# End of file build_animation.sh
