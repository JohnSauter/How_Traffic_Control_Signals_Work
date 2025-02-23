#!/bin/bash
# file: build_video.sh, author: John Sauter, date: February 23, 2025.

# Construct an animation from the event log.

source="events.csv"
animation_temp="animation_temp"
start_time="200"
duration="100"
batch_size="50"
batch_count="60"
animation_file="animation.mkv"

rm -rf ${animation_temp}/
mkdir ${animation_temp}

for (( counter=0; counter<=${batch_count}; counter+=1 )); do
    let "temp = ${counter} * ${batch_size}"
    let "start_frame = ${temp}"
    let "temp= ${counter} + 1"
    let "temp= ${temp} * ${batch_size}"
    let "end_frame= ${temp} - 1"
    parallel --semaphore --ungroup --halt now,fail=1 --jobs 20 --quote \
	     bash "render_animation.sh" "${source}" "${animation_temp}" \
	     ${start_time} ${duration} ${start_frame} ${end_frame} ";"
done
parallel --semaphore --wait

# UHD, 30 frames per second, 10 bits per color, yuv420p, x265.
rm -f ${animation_file}
ffmpeg -hide_banner -framerate 12 -pattern_type glob \
       -i "${animation_temp}/frame*.png" \
       -c:v libx265 -profile:v main10 \
       -vf "framerate=fps=30, format=pix_fmts=yuv420p10le" \
       ${animation_file}

# End of file build_video.sh
