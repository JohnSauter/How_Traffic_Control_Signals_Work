# file: build_video.sh, author: John Sauter, date: December 30, 2024.

# Construct an animation from the event log.

rm -rf animation_temp/
mkdir animation_temp
python3 process_events.py --events-file events.csv \
--animation animation_temp/ 

# UHD, 30 frames per second, 10 bits per color, yuv420p, x265.
rm -f traffic_animation.mkv
ffmpeg -framerate 30 -pattern_type glob \
       -i 'animation_temp/frame*.png' \
       -c:v libx265 -profile:v main10 \
       -vf "framerate=fps=30, format=pix_fmts=yuv420p10le" \
       traffic_animation.mkv

# End of file build_video.sh