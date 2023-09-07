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
    config.tv_ratings,
)

for i,x in enumerate(list_of_selected_dates):
    print(x)
    
    if block_type=='Adult Swim':
        shows=[]
        for poss_show in range(2):
            rand_show=random.choice(config.show_groups['Adult Swim_1'])
            while rand_show in shows:
                rand_show=random.choice(config.show_groups['Adult Swim_1'])
            shows.append(rand_show)
        for poss_show in range(2):
            rand_show=random.choice(config.show_groups['Adult Swim_2'])
            while rand_show in shows:
                rand_show=random.choice(config.show_groups['Adult Swim_2'])
            shows.append(rand_show)
        shows.append('Inuyasha')
        shows.append('Wolfs Rain')
        shows.append(random.choice(config.show_groups['Adult Swim_3']))
    elif block_type=='Nick at Nite':
        shows=[]
        possible_shows=config.show_groups['Nick at Nite_1'].copy()
        for poss_show in range(6):
            rand_show=random.choice(possible_shows)
            possible_shows=list(filter((rand_show).__ne__, possible_shows))
            shows.append(rand_show)
    elif block_type=='FOX':
        shows=['Simpsons','King of the Hill',
               'Malcom in the Middle','X Files']
    elif block_type=='Cartoon Network Powerhouse':
        possible_shows=['Courage the Cowardly Dog','Powerpuff Girls','Ed Edd n Eddy','Cow and Chicken','Johnny Bravo','Dexters Laboratory']
        shows=[]
        for poss_show in range(len(possible_shows)):
            rand_show=random.choice(possible_shows)
            possible_shows=list(filter((rand_show).__ne__, possible_shows))
            shows.append(rand_show)
    elif block_type=='Cartoon Network City':
        shows=['Courage the Cowardly Dog','The Grim Adventures of Billy and Mandy','Ed Edd n Eddy','Dexters Laboratory']
    elif block_type=='Toonami TOM2':
        shows=['Sailor Moon','Yu Yu Hakusho','Batman Beyond','Dragonball','DBZ','Gundam Wing']


    master_order=block.generate(shows,use_all_commercials=False,reuse_bumps=False,recalc_length=False)

    no_break_order=[entry for entry in master_order if not entry.startswith('BREAK END')]
    no_break_order=[entry.replace('/data/media/block_media','/mnt/user/data/media/block_media') for entry in no_break_order]
    
    #takes care of logo insertion - should probably make this a function later
    clips_used=np.array(no_break_order)[np.array(['Broadcast_Shows' in clip for clip in no_break_order])]
    clips_used=np.array([clip[9:] for clip in clips_used])
    
    fixed_paths=np.array([entry.replace('/mnt/user/data/media/block_media','/data/media/block_media') for entry in no_break_order])
    cu_locs=np.array([np.argwhere(fixed_paths==temp_clip)[0][0] for temp_clip in clips_used])
    cu_rel_place=np.insert(np.diff(cu_locs),0,999)

    no_break_order=block.add_logo(no_break_order,shows,i)
    
    block.write_past_shows(master_order,shows)
    block.write_past_bumps(master_order,block.bumpdict)
    block.save_to_txt(no_break_order,block_type+'_'+x+'_'+name_of_selected_dates[i]+'.txt')
