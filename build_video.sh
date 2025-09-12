#!/bin/bash
# file: build_video.sh, author: John Sauter, date: September 11, 2025.

# Turn the frames of an animation into a movie.
# Construct an animation from an event log.

animation_file="${1}"
animation_temp="${2}"
frame_rate="${3}"

start_time="200"
duration="100"
batch_size="50"
batch_count="60"

# UHD, 30 frames per second, 10 bits per color, yuv420p, AV1.
rm -f ${animation_file}
ffmpeg -hide_banner -framerate ${frame_rate} -pattern_type glob \
       -i "${animation_temp}/frame*.png" \
       -c:v libsvtav1 -crf 30 -g 150 -keyint_min 150 \
       -tune animation \
       -vf "framerate=fps=30, format=pix_fmts=yuv420p10le" \
       ${animation_file}

# End of file build_video.sh
