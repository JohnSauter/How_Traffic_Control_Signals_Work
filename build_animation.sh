#!/bin/bash
# file: build_animation.sh, author: John Sauter, date: March 23, 2025.

# Construct an animation from an event log.

source="${1}"
animation_temp="${2}"

# Start time is in seconds.
start_time="200"

# Frame rate is the number of frames per second.
frame_rate="30"

# Batch size and count are in numbers of frames.
# two minutes (120 seconds) seconds means 120*30 = 3,600 frames.
batch_size="100"
batch_count="36"

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
	     ${frame_rate} ";"
done
parallel --semaphore --wait

# End of file build_animation.sh
