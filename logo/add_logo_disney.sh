#!/bin/bash

#script is configured for the specific logo & tv rating size
#assumes a video with resolution of 640x480

#dur=$(ffprobe -loglevel error -show_entries format=duration -of default=nk=1:nw=1 ${1})
#offset=$(bc -l <<< "$dur"-60)

ffmpeg -y \
-i "${1}" \
-loop 1 -i "${2}" \
-loop 1 -i "${3}" \
-filter_complex "\
[1][0]scale2ref=w=oh*mdar:h=ih*0.25[#A logo][v];\
[2][v]scale2ref=w=oh*mdar:h=ih*0.16[tv rating][v];\
[#A logo]trim=25:${4},format=argb, fade=in:st=25:d=0.1:alpha=1,fade=out:st=${5}:d=0.1:alpha=1,\
colorchannelmixer=aa=0.6[#B logo transparent];\
[tv rating]trim=5:${4},format=argb, fade=in:st=5:d=0.1:alpha=1,fade=out:st=20:d=0.1:alpha=1,\
colorchannelmixer=aa=0.8[tv rating transparent];\
[v][#B logo transparent]overlay\
=30:H-h-0[v];\
[v][tv rating transparent]overlay\
=25:25" \
-video_track_timescale 90000 -ar 48000 \
-profile:v main -level:v 4.0 \
-preset veryfast \
-c:a copy /data/media/block_media/Broadcast_Shows/temp/clip_${6}.mp4
