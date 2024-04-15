#!/bin/bash

#script is configured for the specific logo & tv rating size
#assumes a video with resolution of 640x480

#dur=$(ffprobe -loglevel error -show_entries format=duration -of default=nk=1:nw=1 ${1})
#offset=$(bc -l <<< "$dur"-60)

ffmpeg -y \
-i "${1}" \
-loop 1 -i "${2}" \
-i "${3}" \
-filter_complex "\
[1][0]scale2ref=w=oh*mdar:h=ih*0.2[#A logo][v];\
[#A logo]trim=60:${8},format=argb, fade=in:st=60:d=0.2:alpha=1,fade=out:st=${9}:d=0.2:alpha=1,\
colorchannelmixer=aa=0.6[#B logo transparent];\
[v][#B logo transparent]overlay\
=W-w-30:H-h-0;\
[0:a]volume=enable='between(t,${4},${5})':volume='1 - 0.9 * (t - ${4})':eval=frame, \
volume=enable='between(t,${5},${6})':volume='0.1':eval=frame, \
volume=enable='between(t,${6},${7})':volume='.1 + 0.9 * (t - ${6})':eval=frame[overa]; \
[2:a]adelay=${4}s:all=true[bga]; \
[overa][bga]amix=inputs=2:normalize=0[aout]" \
-map "[aout]" -video_track_timescale 90000 -ar 48000 \
-profile:v main -level:v 4.0 \
-preset veryfast \
/data/media/block_media/Broadcast_Shows/temp/clip_${10}.mp4
