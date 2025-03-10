#!/bin/bash
# file: build_animation.sh, author: John Sauter, date: March 9, 2025.

# Construct an animation from an event log.

source="${1}"
animation_temp="${2}"
start_time="200"
duration="100"
batch_size="50"
batch_count="60"
frame_rate=30

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
	     ${start_time} ${duration} ${start_frame} ${end_frame} \
	     ${frame_rate} ";"
done
parallel --semaphore --wait

# End of file build_animation.sh
