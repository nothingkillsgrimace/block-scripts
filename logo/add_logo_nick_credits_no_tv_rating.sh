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
[#A logo]trim=60:${10},format=argb, fade=in:st=60:d=0.2:alpha=1,fade=out:st=${11}:d=0.2:alpha=1,\
colorchannelmixer=aa=0.6[#B logo transparent];\
[v][#B logo transparent]overlay\
=W-w-30:H-h-0[v];\
[2:v]scale=640x480,setpts=PTS-STARTPTS[bg];\
[bg]tpad=start_duration=${4}[bg];\
[bg]tpad=stop_duration=1[bg];\
[0:a]volume=enable='between(t,${4},${5})':volume='1 - 0.99 * (t - ${4})':eval=frame, \
volume=enable='between(t,${5},${6})':volume='0.01':eval=frame, \
volume=enable='between(t,${6},${7})':volume='.01 + 0.90 * (t - ${6})':eval=frame[overa]; \
[2:a]adelay=${4}s:all=true[bga]; \
[overa][bga]amix=inputs=2:normalize=0[aout]; \
[v]setpts=PTS-STARTPTS, scale='if(lte(t,${4}),iw,if(between(t,${4},${8}),\
iw-iw*.65*abs(sin((t-2)*4*PI/8)),if(between(t,${8},${7}),iw-iw*.65,if(lte(t,${9}),\
iw-iw*.65*abs(sin((t-2)*4*PI/8))))))':ih:eval=frame[top]; \
[bg][top]overlay" \
-map "[aout]" -video_track_timescale 90000 -ar 48000 \
-profile:v main -level:v 4.0 \
-preset veryfast \
/data/media/block_media/Broadcast_Shows/temp/clip_${12}.mp4
