#!/usr/bin/env python3

import numpy as np

import sys

import _functions
from _functions import Block_Assembler

import config

import datetime
from calendar import monthrange
import subprocess

import random

block_type=sys.argv[1]
ndays=int(sys.argv[2])

if not ndays:
    ndays=1 

days_of_week={
    1:'Monday',
    2:'Tuesday',
    3:'Wednesday',
    4:'Thursday',
    5:'Friday',
    6:'Saturday',
    7:'Sunday',
}

alldays=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

now=datetime.datetime.now()-datetime.timedelta(hours=4)
tomorrow=(datetime.datetime.now()-datetime.timedelta(hours=4))+datetime.timedelta(days=ndays)

dates=np.arange(datetime.datetime(now.year,now.month,now.day),datetime.datetime(tomorrow.year,tomorrow.month,tomorrow.day),datetime.timedelta(days=1))

days_you_want=alldays

list_of_selected_dates,name_of_selected_dates=[],[]
for loopdate in dates:
    idate=loopdate.astype(datetime.datetime)
    dnum=days_of_week[idate.isoweekday()]
    
    str_date=str(idate.year)+str(idate.month).zfill(2)+str(idate.day).zfill(2)
    
    if dnum in days_you_want:
        list_of_selected_dates.append(str_date)
        name_of_selected_dates.append(dnum)
        
block=Block_Assembler(
    block_type,
    config.filepaths,
    config.type_dict,
)

for i,x in enumerate(list_of_selected_dates):
    print(x)
    
    if block_type=='Adult Swim':
        shows=[random.choice(config.show_groups['Adult Swim_1']),
               random.choice(config.show_groups['Adult Swim_1']),
               random.choice(config.show_groups['Adult Swim_2']),
               random.choice(config.show_groups['Adult Swim_2']),
               'Inuyasha','Cowboy Bebop',
               random.choice(config.show_groups['Adult Swim_3'])]
    elif block_type=='Nick at Nite':
        shows=[random.choice(config.show_groups['Nick at Nite_1']),
               random.choice(config.show_groups['Nick at Nite_1']),
               random.choice(config.show_groups['Nick at Nite_1']),
               random.choice(config.show_groups['Nick at Nite_1']),
               random.choice(config.show_groups['Nick at Nite_1']),
               random.choice(config.show_groups['Nick at Nite_1'])]
    elif block_type=='FOX':
        shows=['Simpsons','King of the Hill',
               'Malcom in the Middle','X Files']
    elif block_type=='Cartoon Network City':
        shows=['Samurai Jack','Top 5']
    elif block_type=='Cartoon Network Powerhouse':
        shows=['Courage the Cowardly Dog','Powerpuff Girls','Dexters Laboratory']
    elif block_type=='Toonami TOM2':
        shows=['Sailor Moon','Yu Yu Hakusho','Batman Beyond','Dragonball','DBZ','Gundam Wing']


    master_order=block.generate(shows,use_all_commercials=False,reuse_bumps=False,recalc_length=False)

    no_break_order=[entry for entry in master_order if not entry.startswith('BREAK END')]
    no_break_order=[entry.replace('/data/media/block_media','/mnt/user/data/media/block_media') for entry in no_break_order]
    
    #takes care of logo insertion - should probably make this a function later
    #clips_used=np.array(no_break_order)[np.array(['Broadcast_Shows' in clip for clip in no_break_order])]
    #clips_used=np.array([clip[9:] for clip in clips_used])
    #for cplace,cu in enumerate(clips_used):
        #cut off the /mnt/user string to run command
    #    durr=_functions.get_length(cu)
    #    offset=durr-60 #fadeout for logo is 1 minute before clip end
    #    if offset<0:
    #        offset=0
        #command for the subprocess operation - NEED DOUBLE BRACKET QUOTES!
    #    cmd = f'/unraid-scripts/logo/add_logo.sh "{cu}" "{config.filepaths[block_type]["logo"]}" "{str(durr)}" "{str(offset)}" "{str(cplace)}"'
    #    process=subprocess.Popen(cmd, shell=True)
    #    process.wait()
    #    for content_place,content in enumerate(no_break_order):
    #        if cu in content:
    #            no_break_order[content_place]=no_break_order[content_place].replace(cu,'/data/media/block_media/Broadcast_Shows/temp/clip_'+str(cplace)+'.mp4')

    
    #block.write_past_shows(master_order,shows)
    #block.write_past_bumps(master_order,block.bumpdict)
    block.save_to_txt(no_break_order,block_type+'_'+x+'_'+name_of_selected_dates[i]+'.txt')
