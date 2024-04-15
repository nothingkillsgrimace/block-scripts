#!/bin/bash

echo "$1"

docker exec -i anaconda3 /unraid-scripts/python_scripts/block-scripts/create_block.py "$1" "$2"

cd /mnt/user/data/media/plex_media/blocks

echo CONCATENATING FILES
./concat.sh "$1"

for file in "${1}"*txt; do

echo APPLYING HIGHPASS AND LOWPASS FILTER TO "${file%.*}".mp4...
ffmpeg -y -i "${file%.*}".mp4 -af "highpass=f=20, lowpass=f=4000" -ar 22050 -c:v copy -preset veryfast filtered.mp4

#remove original file
rm "${file%.*}".mp4

#rename filtered file to match original
mv filtered.mp4 "${file%.*}".mp4

#echo UPLOADING "${file%.*}".mp4...
rclone copy "${file%.*}".mp4 gdrive:/Completed\ Broadcasts/Share/Blocks/ 
done

mv *.txt archived_txt/
