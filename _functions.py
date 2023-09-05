import os
import numpy as np
import random
import subprocess
import shutil
import datetime
import math

#this function will return the length in seconds of a file when given the full file path
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return round(float(result.stdout))

#this function will return a list of every file in a directory when given the path to a particular folder
def get_full_path(path):
    arr=[]
    for file in os.listdir(path):
        if not file.startswith('.'):
            location=path+file
            if os.path.isdir(location):
                continue
            else:
                arr.append(location)
    return np.array(arr)

#this function will return a list of every file in a directory when given the path to a particular folder
def get_dirs(path):
    arr=[]
    for file in os.listdir(path):
        if not file.startswith('.'):
            location=path+file
            if os.path.isdir(location):
                arr.append(location)
    return np.array(arr)

#this function takes a list of video files structured as:
# File identifier - description of file.mp4
#Ex: Acme Hour - Brought to you by Acme 2001 2002.mp4
#in blocks, promos with A LOT of ids (CCF) can clog up promo selection
#this function selects 1 promo from each id sub heading
def trim_promos(promos,lengths):
    ids=[]
    for promo in promos:
        loc1=promo.rfind('/')
        promo_name=promo[loc1+1:]
        loc2=promo_name.find(' -')
        promo_id=promo_name[:loc2]

        ids.append(promo_id)

    unique_ids=np.unique(ids)

    new_promos=[]
    new_lengths=[]
    for uid in unique_ids:
        iso_promos=promos[np.array(['/'+uid+' -' in promo for promo in promos])]
        single_promo=random.choice(iso_promos)
        new_promos.append(single_promo)
        new_lengths.append(int(lengths[promos==single_promo]))

    return np.array(new_promos),np.array(new_lengths)

#only select files with a specific year in the name
#to prevent commercials from >2000 playing in something like TOM2 or CN City blocks
def trim_years(list_fs,f_lengths,in_years):
    filtered_fs=[]
    filtered_ls=[]
    for f in list_fs:
        if np.max([yr in f for yr in in_years]):
            filtered_fs.append(f)
            filtered_ls.append(int(f_lengths[list_fs==f]))
    
    return np.array(filtered_fs),np.array(filtered_ls)

#this function will return the lengths for a series of file when given a list of file paths
def length_vids(files):
    return np.array([get_length(entry) for entry in files])

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def get_commercial_break_length(segments):
    seg_lengths=length_vids(segments)
    total_lengths_minutes=seg_lengths.sum()/60
    if total_lengths_minutes<30:
        available_time=((math.ceil(total_lengths_minutes/15)*15)-total_lengths_minutes)*60
    else:
        available_time=((math.ceil(total_lengths_minutes/30)*30)-total_lengths_minutes)*60

    #for some cartoon network shows, the intro and outro are considered
    #as segments, but we probably don't want to be consider these as
    #segments for commercial breaks since they likely will not transition
    #to a commercial break. intro should move right into the first segment
    if total_lengths_minutes<30 and len(segments)>3:
        commercial_length=round(available_time/(len(segments)-2)) 
        seg_flag=True
        return(((math.floor(commercial_length/15))*15),seg_flag)

    else:
        commercial_length=round(available_time/len(segments))
        return(((math.floor(commercial_length/15))*15))

class Block_Assembler:
    
    months=np.array(['January','February','March','April','May','June','July','August','September',
           'October','November','December'])

    mydate=datetime.datetime.now()-datetime.timedelta(hours=4)
    curmonth=mydate.strftime("%B")
    
    def __init__(self,blocktype,paths,showtypes):
        self.blocktype=blocktype
        self.allpaths=paths
        self.showtypes=showtypes
        self.possible_shows=self.get_possible_shows(self.allpaths['shows'])
        
        if self.blocktype!='Custom':
            self.paths=paths[blocktype]
            if 'bump_logs' in self.paths.keys():
                self.bumpdict=self.paths['bump_logs']
            else:
                self.bumpdict=None
        else:
            self.bumpdict=None
            self.paths=paths
                
        self.boomerang_dict={
    'Atom Ant':['Atom Ant','Precious Pupp','Hillbilly Bears'],
    'Quickdraw Mcgraw':['Quickdraw Mcgraw','Auggie Doggie','Snooper and Blabber'],
    'Magilla Gorilla':['Magilla Gorilla','Ricochet Rabbit','Punkin Puss'],
    'Huckleberry Hound':['Huckleberry Hound','Pixie Dixie and Mr Jinks','Hokey Wolf'],
    'Peter Potamus':['Peter Potamus','Breezly and Sneezly','Yippee Yappee Yahooey'],
    'Secret Squirrel':['Secret Squirrel','Squiddly Diddly','Winsome Witch'],
    'Yogi Bear':['Yogi Bear','Snagglepuss','Yakky Doodle']
}
        
    def retrieve_clips(self,clips):
        clip_dict={}
        for key in clips.keys():
            clip_dict[key]=get_full_path(clips[key])
        return clip_dict
    
    def get_possible_shows(self,paths):
        list_of_shows=[]
        for key in paths.keys():
            shows_in_folder=get_dirs(paths[key])
            for item in shows_in_folder:
                list_of_shows.append(item)
        return(np.array(list_of_shows))
        
    def correct_clip_timeofyear(self,clip_dict,curmonth,months):
        #we only want video files from the get_full_path operation above
        #in this case, those are .mp4s, so remove all entries that do not
        #contain '.mp4' in the string

        #we also want to remove all video files that are for months that do not overlap with the
        #current month
        for key in clip_dict.keys():
            clip_dict[key]=clip_dict[key][['.mp4' in entry for entry in clip_dict[key]]]

            curmonth_paths=np.array([clip for clip in clip_dict[key] if curmonth in clip])
            for month in months:
                clip_dict[key]=np.array([clip for clip in clip_dict[key] if month not in clip])
            clip_dict[key]=np.append(clip_dict[key],curmonth_paths)
        return(clip_dict)


    def remove_used_bumps(self,bump_dict,clip_dict,
                         replace=False,r_kw1='/Volumes/Media and Storage Desktop/',r_kw2='/data/media/block_media'):
        #open up a couple text files that list bumps used in prior broadcasts
        #this list will be cross-referenced against all bumps and bumps that have been used before
        #will be removed. this helps to keep things fresh. nobody wants to see the same bump every time!
        bump_recorder_folder_path=self.allpaths['past_bumps']
        bump_contents={}
        for b in bump_dict.keys():
            with open(bump_recorder_folder_path+bump_dict[b]['filename'],'r+') as f:
                f.seek(0)
                bump_contents[b]=f.readlines()

            if len(bump_contents[b])/len(clip_dict['bumps'][[bump_dict[b]['keyword'] in entry for\
                                                          entry in clip_dict['bumps']]])>0.9:
                with open(bump_recorder_folder_path+bump_dict[b]['filename'],'w') as f:
                                      f.seek(0)
            
            else:
                
                for bc in bump_contents[b]: 
                    if replace==True:
                        bc=bc.replace(r_kw1,r_kw2)

                    if bc[:-1] in clip_dict['bumps']:
                        index=np.argwhere(clip_dict['bumps']==bc[:-1])[0,0]
                        clip_dict['bumps']=np.delete(clip_dict['bumps'],index)

        return(clip_dict['bumps'])

    #this function is responsible for generating commercial blocks
    def commercial_generator(self,length,probs,master_order,
                             clip_dict,length_dict,
                             remainder_length=5
                            ):

        #initialize our commercial list as an empty list
        commercials_list=[]

        #the total size of all commercials is equal to the length parameter given to the function (in seconds)
        commercial_block_size=length

        #assign probality dictionary to a temp variable
        flag_dict=probs

        #while there's still at least remainder_length seconds left in the commercial block, continue to loop through and add more commercials
        while commercial_block_size>remainder_length:

            #calculate the probability that the next pick in the commercial block will be a commercial
            #this probability is defined as the remainder leftover when you subtract the probabilities
            #of all other types in the flag_dict
            commercial_probability=1-sum([flag_dict[key] for key in flag_dict.keys()])
            #assign all probabilities
            probabilities=[flag_dict[key] for key in flag_dict.keys()]
            probabilities.append(commercial_probability)
            #randomly select which 'type' of commercial will be next
            possible_types=list(flag_dict.keys())
            possible_types.append('commercials')
            commercial_type=random.choices(possible_types,weights=probabilities)[0]

            #check the commercial type and cross reference the selected promo against the lengths calculated earlier
            commercial=random.choice(clip_dict[commercial_type])
            #get length of selected commercial by cross referencing it in the clip dictionary
            diff=int(length_dict[commercial_type][clip_dict[commercial_type]==commercial])

            #subtract the remaining time left in the commercial block by the length of the commercial/promo just selected
            commercial_block_size=commercial_block_size-diff

            #if the addition of the new promo causes the commercial block to run 10 seconds over the specified time, then skip 
            #it and select another one
            if commercial_block_size<-10:
                commercial_block_size=commercial_block_size+diff
            #if the commercial has already been selected for the broadcast then skip it and select another one
            elif commercial in commercials_list:
                commercial_block_size=commercial_block_size+diff
            #if the commercial is part of the last 15 files in the order, toss it out for a new one to keep it fresh
            elif commercial in master_order[-15:]:
                commercial_block_size=commercial_block_size+diff

            #otherwise if the earlier criteria aren't met, add the commercial to the list
            else:
                commercials_list.append(commercial)

                #if the selected commercial type is anything other than a normal commercial, reset the probability of selecting
                #that commercial type again to zero to avoid repeats
                if commercial_type!='commercials':
                    flag_dict[commercial_type]=0

                #once a commercial is added to the list, adjust the probabilities so they tick upwards
                #currently the probability of each type in the flag_dict goes up by 1% after each
                #commercial. there's probability a more elegant way of doing this, but gets the
                #job done for now.
                for ctype in flag_dict.keys():
                    flag_dict[ctype]+=0.01

            #print(commercial_block_size,diff)
            #print(probabilities)

        #once done, this function will return a list of commercials, and the probabilities so that they can be carried
        #over as input for the next commercial break
        return(commercials_list,flag_dict)


    def remove_past_episodes(self,show,show_files,show_type,
                            replace=False,r_kw1='/Volumes/Media and Storage Desktop/',r_kw2='/Volumes/Elements/'):
        
        path_to_log=self.allpaths['past_episodes']
        
        #check to see if show file exists
        #if it doesn't, create an empty txt file with
        #the show name as the filename
        if os.path.exists(path_to_log+show+'.txt')==False:
            with open(path_to_log+show+'.txt','w') as f:
                f.seek(0)
        
        with open(path_to_log+show+'.txt','r+') as f:
            f.seek(0)
            past_episodes_used=f.readlines()

        if past_episodes_used:
            if ((len(past_episodes_used)/len(show_files))>0.9) & (show_type=='episodic'):
                with open(path_to_log+show+'.txt','w') as f:
                    f.seek(0)
            elif (show_type=='serial') & (show_files[-1]+"'\n" in past_episodes_used):
                with open(path_to_log+show+'.txt','w') as f:
                    f.seek(0)
            else:
                for past_episode in past_episodes_used:
                    if replace==True:
                        past_episode=past_episode.replace(r_kw1,r_kw2)

                    if past_episode[:-2] in show_files:
                        index=np.argwhere(show_files==past_episode[:-2])[0,0]
                        show_files=np.delete(show_files,index)

        return(show_files)

    def write_past_shows(self,master_order,shows):
        show_paths=self.allpaths['shows']
        master_path=self.allpaths['past_episodes']
        for i,key in enumerate(show_paths.keys()):
            match=np.array(master_order)[np.array([show_paths[key] in line for line in master_order])]
            if i==0:
                shows_used_in_block=match
            else:
                shows_used_in_block=np.append(shows_used_in_block,match)

        shows_to_write=[]
        for show in shows:
            if show in self.boomerang_dict:
                [shows_to_write.append(item) for item in self.boomerang_dict[show]]
            else:
                shows_to_write.append(show)
                
        for i,entry in enumerate(shows_to_write):
            #check to see if show file exists - routine already exists above
            #but copying it down here just to be safe
            if os.path.exists(master_path+entry+'.txt')==False:
                with open(master_path+entry+'.txt','w') as f:
                    f.seek(0)
            
            with open(master_path+entry+'.txt','r+') as f:
                f.seek(0)
                contents=f.readlines()
            
            with open(master_path+entry+'.txt','w+') as f:
                for used_show in shows_used_in_block:
                    if entry in used_show and used_show[10:] not in contents:
                        contents.insert(-1,used_show+"'\n")
                contents="".join(contents)
                f.write(contents)


                
    def write_past_bumps(self,master_order,bump_dict):
        
        if 'bump_logs' in self.paths.keys():
            folder=self.allpaths['past_bumps']
            for btype in bump_dict.keys():
                bumps_used=np.array(master_order)[np.array([bump_dict[btype]['keyword'] in line for\
                                                            line in master_order])]

                for i_bump in bumps_used:
                    with open(folder+bump_dict[btype]['filename'],'r+') as f:
                        f.seek(0)
                        contents=f.readlines()
                    with open(folder+bump_dict[btype]['filename'],'w+') as f:
                        if i_bump+'\n' not in contents:
                            contents.insert(-1,i_bump+"\n")
                        contents="".join(contents)
                        f.write(contents)
        else:
            print('bump_logs path not defined in dictionary. Not writing bumps...')

    def Create_Block(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        master_order=[]
        
        for showpos,show in enumerate(shows):
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            
            #sort the files so they're in correct order
            show_files=np.sort(show_files)

            #take out episodes of this show that have been played in previously generated blocks
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)

            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-5] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-5]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break
                
            output=get_commercial_break_length(show_segments)
            if type(output)==tuple:
                commercial_length,show_segs_include_intros=output
            else:
                commercial_length=output
                show_segs_include_intros=False

            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    
                    master_order.append(segment)
                    if show_segs_include_intros==False:
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                
                elif segpos==len(show_segments)-2 and show_segs_include_intros==True:
                    master_order.append(segment)
                    continue

                elif segpos<len(show_segments)-1:
                    master_order.append(segment)
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                
                else:
                    master_order.append(segment)
                    master_order.append('BREAK END OF SHOW')

        print('Done!')
        return(master_order)
    
    
    def Boomerang(self,shows,type_dict,clip_dict,flag_dict,length_dict,
                 ):
        
        master_order=[]
        master_order.append(self.paths['clips']['bumps']+'Up Next - Boomerang.mp4')
        
        for showpos,show in enumerate(shows):
            #select a lead in intro for the show
            #if a unique intro does not exist, insert a generic one
                
            if show not in self.boomerang_dict:
                show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
                show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
                
                #sort the files so they're in correct order
                show_files=np.sort(show_files)
                #take out episodes of this show that have been played in previously generated blocks
                show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)

                if type_dict[show]=='serial':
                    show_segments=show_files[np.array([show_files[0][:-5] in segment for segment in show_files])==True]
                elif type_dict[show]=='episodic':
                    ep_selector=random.choice(show_files)[:-5]
                    show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
                else:
                    print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                    print('Current show is ',show)
                    break
                    
            else:
                for placemarker,feature in enumerate(self.boomerang_dict[show]):
                    show_folder_loc=self.possible_shows[np.array([feature in ps for ps in self.possible_shows])==True][0]
                    show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
                    
                    #sort the files so they're in correct order
                    show_files=np.sort(show_files)
                    #take out episodes of this show that have been played in previously generated blocks
                    show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)

                    if type_dict[show]=='serial':
                        temporary_segment=show_files[np.array([show_files[0][:-5] in segment for segment in show_files])==True]
                    elif type_dict[show]=='episodic':
                        ep_selector=random.choice(show_files)[:-5]
                        temporary_segment=show_files[np.array([ep_selector in segment for segment in show_files])==True]
                    else:
                        print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                        print('Current show is ',show)
                        break
                        
                    if placemarker==0:
                        show_segments=temporary_segment
                    else:
                        show_segments=np.concatenate((show_segments,temporary_segment))
            
            commercial_length=get_commercial_break_length(show_segments)
                
            for segpos,segment in enumerate(show_segments):
                if segpos==0:
                    
                    show_intro=clip_dict['bumps'][np.array([show+' Intro' in bump for bump in clip_dict['bumps']])]
                    if not show_intro:
                        sel_intro_clip=clip_dict['bumps'][np.array(['Neutral Any' in bump for bump in clip_dict['bumps']])]
                        sel_intro_clip=random.choice(sel_intro_clip)
                    else:
                        sel_intro_clip=self.paths['clips']['bumps']+show+' Intro.mp4'
                        
                    length_of_other=get_length(sel_intro_clip)                    

                    if show in self.boomerang_dict:
                        #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                        #the probabilities and then append each entry in the commercial block to the master file
                        tmp_cblock,flag_dict=self.commercial_generator((commercial_length-length_of_other)*1.5,flag_dict,master_order,clip_dict,length_dict)
                    else:
                        #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                        #the probabilities and then append each entry in the commercial block to the master file
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

                        
                    master_order.append(sel_intro_clip)
                    master_order.append(segment)
                    
                    transition_bumps_in=clip_dict['bumps'][np.array([show+' Fade In' in bump for bump in clip_dict['bumps']])]
                    transition_bumps_out=clip_dict['bumps'][np.array([show+' Fade Out' in bump for bump in clip_dict['bumps']])]
                    if not transition_bumps_in:
                        transition_bumps_in=clip_dict['bumps'][np.array(['Neutral Fade In' in bump for bump in clip_dict['bumps']])]
                    if not transition_bumps_out:
                        transition_bumps_out=clip_dict['bumps'][np.array(['Neutral Fade Out' in bump for bump in clip_dict['bumps']])]

                    if show in self.boomerang_dict:
                        interstitial=clip_dict['bumps'][np.array([show+' Interstitial' in bump for bump in clip_dict['bumps']])]
                        if not interstitial:
                            interstitial=clip_dict['bumps'][np.array(['Neutral Any' in bump for bump in clip_dict['bumps']])]
                        master_order.append(random.choice(interstitial))
                        continue
                        
                    
                    sel_fadeout=random.choice(transition_bumps_out)
                    sel_fadein=random.choice(transition_bumps_in)
                    
                    length_of_other=length_vids(list((sel_fadeout,sel_fadein))).sum()
             
                    master_order.append(sel_fadeout)
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    master_order.append(sel_fadein)
                    continue
                    
                master_order.append(segment)
                    
                if segpos<len(show_segments)-1:
                    sel_fadeout=random.choice(transition_bumps_out)
                    sel_fadein=random.choice(transition_bumps_in)
                    length_of_other=length_vids(list((sel_fadeout,sel_fadein))).sum()

                    master_order.append(sel_fadeout)
                    
                    if show in self.boomerang_dict:
                        #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                        #the probabilities and then append each entry in the commercial block to the master file
                        tmp_cblock,flag_dict=self.commercial_generator((commercial_length-length_of_other)*1.5,flag_dict,master_order,clip_dict,length_dict)
                    else:
                        #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                        #the probabilities and then append each entry in the commercial block to the master file
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                        
                    master_order.append(sel_fadein)
                
                elif segpos==len(show_segments)-1:
                    ending_bump=clip_dict['bumps'][np.array([show+' End' in bump for bump in clip_dict['bumps']])]
                    if ending_bump:
                        master_order.append(random.choice(ending_bump))
                        
                    if showpos<len(shows)-1:
                        if os.path.isfile(self.paths['clips']['bumps']+'Up Next - '+shows[showpos+1]+'.mp4')==True:
                            master_order.append(self.paths['clips']['bumps']+'Up Next - '+shows[showpos+1]+'.mp4')
                            master_order.append('BREAK END OF SHOW')

                    else:
                        master_order.append(self.paths['clips']['bumps']+'Neutral End.mp4')
                        master_order.append('BREAK END OF SHOW')


        return(master_order)

            
            
    def Adult_Swim(self,shows,type_dict,clip_dict,flag_dict,length_dict,
                  ACTN_shows=['Inuyasha','Case Closed','Cowboy Bebop',
                              'Trigun']):
        
        master_order=[]
        
        tmp_cblock,flag_dict=self.commercial_generator(90,flag_dict,master_order,clip_dict,length_dict)
        for tmp_c in tmp_cblock:
            master_order.append(tmp_c)

        #add the any intro bumps you want first in the order
        master_order.append(self.paths['advisory'])
        master_order.append(self.paths['pool_intro'])
        
        remaining_multiparters=[]

        #start looping through each show in the list
        for showpos,show in enumerate(shows):
            print(show)
            #categorize the bumps
            bw_bumps=clip_dict['bumps'][np.array(['General -' in bump for bump in clip_dict['bumps']])==True]
            intro_bumps=clip_dict['bumps'][np.array(['Intro - '+show in bump for bump in clip_dict['bumps']])==True]
            pic_bumps=clip_dict['bumps'][np.array(['Bump -' in bump for bump in clip_dict['bumps']])==True]
            actn_bumps=clip_dict['bumps'][np.array(['ACTN -' in bump for bump in clip_dict['bumps']])==True]
            show_bumps=clip_dict['bumps'][np.array([show+' -' in bump for bump in clip_dict['bumps']])==True]

            #if show in specific_episode: #this may or may not work
            #    show_files=get_full_path(specific_episode[show]) #this may be broken
            #else:
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')

            #if show is in the first half of the lineup, throw in some b&w bumps
            #else, use generic pic bumps
            if showpos<=int(len(shows)/2):
                possible_bumps=np.concatenate((show_bumps,bw_bumps))
            else:
                possible_bumps=np.concatenate((show_bumps,pic_bumps))

            #sort the files so they're in correct order
            show_files=np.sort(show_files)

            #take out episodes of this show that have been played in previously generated blocks
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)

            #if a specific showpath is specified use that, otherwise 
            #if the show uses a specified episode num in the dict, use that episode num
            #otherwise select a random episode from what's available
            
            #if show in specific_episode:
            #    show_segments=show_files.copy()
            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-5] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-5]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break
                
            #if it isn't the first show in the lineup
            if showpos>0:
                #if show specific bumps exist, lead off with them before a show starts
                #otherwise throw in either a text bump or pic bump depending on where in the lineup you are
                if not intro_bumps:
                    show_starter_bump=random.sample(list(possible_bumps),1)[0]

                    if show_starter_bump in master_order:
                        while show_starter_bump in master_order: #possible infinite loop - should be fixed
                            show_starter_bump=random.sample(list(possible_bumps),1)[0]
                            
                    if 'MultiParter' in show_starter_bump and not remaining_multiparters:
                        lub_idx=show_starter_bump.find('MultiParter')
                        mp_bumps=possible_bumps[np.array([show_starter_bump[:lub_idx] in bump for bump in possible_bumps])==True]
                        mp_bumps.sort()
                        show_starter_bump=mp_bumps[0]
                        print(mp_bumps)
                        if len(mp_bumps)>1:
                            remaining_multiparters=mp_bumps[1:]
                        else:
                            remaining_multiparters=[]
                    elif len(remaining_multiparters):
                        show_starter_bump=remaining_multiparters[0]
                        if len(remaining_multiparters)>1:
                            remaining_multiparters=remaining_multiparters[1:]
                        else:
                            remaining_multiparters=[]
                                   
                elif intro_bumps:
                    show_starter_bump=random.sample(list(intro_bumps),1)[0]
                    


                master_order.append(show_starter_bump)

            commercial_length=get_commercial_break_length(show_segments)
            
            for segpos,segment in enumerate(show_segments):
                #add the first part of the show to the block order
                master_order.append(segment)

                #for segments that aren't the final segment
                if segpos<len(show_segments)-1:
                    #randomly select a matching outro bump for the show and slot it in to kick off the first commercial break
                    if show not in ACTN_shows:
                        fadeout_bumps=possible_bumps[np.array(['Fade In' not in bump for bump in possible_bumps])==True]
                    else:
                        fadeout_bumps=possible_bumps[np.array([show+' - Fade Out' in bump for bump in possible_bumps])==True]

                    fadeout=random.sample(list(fadeout_bumps),1)[0]

                    #check to see if this bump was already used this broadcast but only if its a text bump or pic bump
                    if fadeout in master_order and fadeout in np.concatenate((bw_bumps,pic_bumps)):
                        print('HEY! DUPLICATE FADEOUT! Removing...')
                        print(fadeout)
                        while fadeout in master_order:
                            fadeout=random.sample(list(fadeout_bumps),1)[0]
                    elif 'Numbers Game' in fadeout and sum(['Numbers Game' in bump for bump in master_order]):
                        print('HEY! DUPLICATE NUMBERS GAME! Removing...')
                        print(fadeout)
                        while 'Numbers Game' in fadeout:
                            fadeout=random.sample(list(fadeout_bumps),1)[0]
                            
                    #after the commercial break, randomly select an intro to fade back into the show
                    if show not in ACTN_shows:
                        fadein_bumps=possible_bumps[np.array(['Fade Out' not in bump for bump in possible_bumps])==True]
                    else:
                        fadein_bumps=possible_bumps[np.array(['Fade In' in bump for bump in possible_bumps])==True]

                    fadein=random.sample(list(fadein_bumps),1)[0]

                    #check to see if this bump was already used this broadcast but only if its a text bump or pic bump
                    if fadein in master_order and fadein in np.concatenate((bw_bumps,pic_bumps)):
                        print('HEY! DUPLICATE FADEIN! Removing...')
                        print(fadein)
                        while fadein in master_order:
                            fadein=random.sample(list(fadein_bumps),1)[0]
                    elif 'Numbers Game' in fadein and sum(['Numbers Game' in bump for bump in master_order]):
                        print('HEY! DUPLICATE NUMBERS GAME! Removing...')
                        print(fadein)
                        while 'Numbers Game' in fadein: #possible infinite loop here, fix this
                            fadein=random.sample(list(fadein_bumps),1)[0]
                                  
                    if 'MultiParter' in fadein and not remaining_multiparters: 
                        lub_idx=fadein.find('MultiParter')
                        mp_bumps=possible_bumps[np.array([fadein[:lub_idx] in bump for bump in possible_bumps])==True]
                        mp_bumps.sort()
                        print(mp_bumps)
                        if len(mp_bumps)>1:
                            fadeout=mp_bumps[0]
                            fadein=mp_bumps[1]
                            if len(mp_bumps)>2:
                                remaining_multiparters=mp_bumps[2:]
                            else:
                                remaining_multiparters=[]
                        else:
                            remaining_multiparters=[]
                    elif 'MultiParter' in fadeout and not remaining_multiparters:
                        lub_idx=fadeout.find('MultiParter')
                        mp_bumps=possible_bumps[np.array([fadeout[:lub_idx] in bump for bump in possible_bumps])==True]
                        mp_bumps.sort()
                        print(mp_bumps)
                        if len(mp_bumps)>1:
                            fadeout=mp_bumps[0]
                            fadein=mp_bumps[1]
                            if len(mp_bumps)>2:
                                remaining_multiparters=mp_bumps[2:]
                            else:
                                remaining_multiparters=[]
                        else:
                            remaining_multiparters=[]
                    elif len(remaining_multiparters):
                        show_starter_bump=remaining_multiparters[0]
                        if len(remaining_multiparters)>1:
                            fadein=remaining_multiparters[0]
                            fadeout=remaining_multiparters[1]
                            
                            if len(remaining_multiparters)>2:
                                remaining_multiparters=remaining_multiparters[2:]
                            else:
                                remaining_multiparters=[]
                        elif len(remaining_multiparters)==1:
                            fadein=remaining_multiparters[0]
                            remaining_multiparters=[]

                    length_of_other=length_vids(list((fadeout,fadein))).sum()

                    master_order.append(fadeout)

                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

                    master_order.append(fadein)

                #if the current segment is the last of the show
                elif (segpos==len(show_segments)-1):

                    #if the show is in the first half of the lineup, throw a text bump at the end
                    #otherwise, throw in a picture bump
                    if showpos<=int(len(shows)/2):
                        end_bump=random.sample(list(bw_bumps),1)[0]
                        if end_bump in master_order:
                            while end_bump in master_order:
                                end_bump=random.sample(list(bw_bumps),1)[0]
                                
                        if 'MultiParter' in end_bump and not remaining_multiparters:
                            lub_idx=end_bump.find('MultiParter')
                            mp_bumps=possible_bumps[np.array([end_bump[:lub_idx] in bump for bump in possible_bumps])==True]
                            mp_bumps.sort()
                            print(mp_bumps)
                            end_bump=mp_bumps[0]
                            if len(mp_bumps)>1:
                                remaining_multiparters=mp_bumps[1:]
                            else:
                                remaining_multiparters=[]
                        elif len(remaining_multiparters):
                            end_bump=remaining_multiparters[0]
                            if len(remaining_multiparters)>1:
                                remaining_multiparters=remaining_multiparters[1:]
                            else:
                                remaining_multiparters=[]

                    elif show!=shows[-1]:
                        end_bump=random.sample(list(pic_bumps),1)[0]
                        if end_bump in master_order:
                            while end_bump in master_order:
                                end_bump=random.sample(list(pic_bumps),1)[0]

                    else:
                        master_order.append('BREAK END OF SHOW')
                        continue
                        
                    master_order.append(end_bump)
                    length_of_other=get_length(end_bump)

                    #put in some commercials between shows but make sure to start it off first with an [as] promo
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,{'promos':1},master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    master_order.append('BREAK END OF SHOW')

        return(master_order)
    
    
    def FOX(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        
        master_order=[]
        
        for showpos,show in enumerate(shows):
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
        
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)

            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-8] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-8]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break

            show_fadeout_bumps=clip_dict['bumps'][np.array([show+' Fade Out' in bump for bump in clip_dict['bumps']])==True]

            commercial_length=get_commercial_break_length(show_segments)

            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    #throw a FOX promo for the fade back in to the show - pretty typical for this block
                    random_promo=random.choice(clip_dict['promos'])
                    while random_promo in master_order[-30:]:
                        random_promo=random.choice(clip_dict['promos'])
                    length_of_other=get_length(random_promo)

                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

                master_order.append(random_promo)
                master_order.append(segment)

                if segpos<len(show_segments)-1:
                    if len(show_fadeout_bumps)!=0 and segpos==0:
                        fadeout_bump=random.choice(show_fadeout_bumps)
                        index=np.argwhere(show_fadeout_bumps==fadeout_bump)
                        show_fadeout_bumps=np.delete(show_fadeout_bumps,index)
                        master_order.append(fadeout_bump)
                    else:
                        fadeout_bump=None

                    random_promo=random.choice(clip_dict['promos'])
                    while random_promo in master_order[-30:]:
                        random_promo=random.choice(clip_dict['promos'])
                        
                    if fadeout_bump:
                        length_of_other=length_vids(list((random_promo,fadeout_bump))).sum()
                    else:
                        length_of_other=get_length(random_promo)

                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

                elif segpos==len(show_segments)-1:
                    master_order.append('BREAK END OF SHOW')


        return(master_order)
    
    def Top_5(self,master_order,shows,showpos,clip_dict,flag_dict,length_dict,length_other,
             possible_entries=[
                 'Camp Lazlo','Codename Kids Next Door', 'Courage the Cowardly Dog',
                 'Cow and Chicken','Dexters Laboratory','Ed Edd n Eddy','Johnny Bravo',
                 'Powerpuff Girls','The Grim Adventures of Billy and Mandy'],
              possible_3parters=['Cow and Chicken','Dexters Laboratory','Johnny Bravo',
                                 'The Grim Adventures of Billy and Mandy'],
              possible_2parters=['Camp Lazlo','Codename Kids Next Door','Courage the Cowardly Dog',
                                 'Ed Edd n Eddy','Powerpuff Girls','The Grim Adventures of Billy and Mandy'],
                 ):
        
        top5_bumps=get_full_path(self.paths['top5_folder'])
        top5_bumps=top5_bumps[np.array([self.paths['top5_year'] in tb for tb in top5_bumps])==True]
        fadeout_bumps=top5_bumps[np.array(['Fadeout' in tb for tb in top5_bumps])==True]
        
        sel_3parters=[]
        for i in range(2):
            random_3parter=random.choice(possible_3parters)
            while random_3parter in sel_3parters:
                random_3parter=random.choice(possible_3parters)
            sel_3parters.append(random_3parter)
        sel_2parters=[]
        for i in range(3):
            random_2parter=random.choice(possible_2parters)
            while random_2parter in sel_2parters or random_2parter in sel_3parters:
                random_2parter=random.choice(possible_2parters)
            sel_2parters.append(random_2parter)
            
        show_segments=[]
        for random_show in sel_3parters:
            show_folder_loc=self.possible_shows[np.array([random_show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
            ep_selector=random.choice(show_files)[:-8]
            rsegments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            while len(rsegments)<5:
                ep_selector=random.choice(show_files)[:-8]
                rsegments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            rnum=str(random.choice([1,2,3])).zfill(3)
            show_segments.append(rsegments[np.array([rnum in segment for segment in rsegments])==True][0])
        for random_show in sel_2parters:
            show_folder_loc=self.possible_shows[np.array([random_show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
            show_files=show_files[np.array(['2pt' not in segment for segment in show_files])==True]
            ep_selector=random.choice(show_files)[:-8]
            rsegments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            while len(rsegments)>4:
                ep_selector=random.choice(show_files)[:-8]
                rsegments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            rnum=str(random.choice([1,2])).zfill(3)
            show_segments.append(rsegments[np.array([rnum in segment for segment in rsegments])==True][0])
        
        commercial_length=get_commercial_break_length(show_segments)

        for segpos,segment in enumerate(show_segments):    
            if commercial_length<length_other:
                length_other=length_other-commercial_length
            else:
                tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_other,flag_dict,master_order,clip_dict,length_dict)
                for tmp_c in tmp_cblock:
                    master_order.append(tmp_c)
                length_other=0
                    
            if segpos==0:
                master_order.append(self.paths['top5_folder']+self.paths['top5_year']+' Top 5 Intro.mp4')
                length_other+=get_length(self.paths['top5_folder']+self.paths['top5_year']+' Top 5 Intro.mp4')
            master_order.append(self.paths['top5_folder']+self.paths['top5_year']+' Top 5 Number '+str(5-segpos)+'.mp4')
            length_other+=get_length(self.paths['top5_folder']+self.paths['top5_year']+' Top 5 Number '+str(5-segpos)+'.mp4')
            master_order.append(segment)
            if segpos!=len(show_segments)-1:
                out_bump=random.choice(fadeout_bumps)
                master_order.append(out_bump)
                length_other+=get_length(out_bump)
            else:
                master_order.append(self.paths['top5_folder']+self.paths['top5_year']+' Top 5 Outro.mp4')
                length_other+=get_length(self.paths['top5_folder']+self.paths['top5_year']+' Top 5 Outro.mp4')
                master_order.append('BREAK END OF SHOW')
                
                if showpos<(len(shows)-2):
                    potential_schedules=clip_dict['schedules'][np.array([shows[showpos]+' '+shows[showpos+1] in entry for entry in clip_dict['schedules']])]
                    if len(potential_schedules)!=0:
                        random_schedule=random.choice(potential_schedules)
                        master_order.append(random_schedule)
                        length_other+=get_length(random_schedule)


        return(master_order,length_other)

        
        
    
    def CN_City(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        master_order=[]
        
        city_years=['2004','2005','2006']
        
        #get commercials & promos from years which TOM2 toonami aired
        clip_dict['promos_cn'],length_dict['promos_cn']=trim_years(clip_dict['promos_cn'],length_dict['promos_cn'],city_years)
        clip_dict['commercials'],length_dict['commercials']=trim_years(clip_dict['commercials'],length_dict['commercials'],city_years)
        
        #trim out CN promos so there's 1 of each type
        clip_dict['promos_cn'],length_dict['promos_cn']=trim_promos(clip_dict['promos_cn'],length_dict['promos_cn'])
        
        #select just one ccf to play
        selected_ccf=random.choice(clip_dict['promos_ccf'])
        length_dict['promos_ccf']=length_dict['promos_ccf'][clip_dict['promos_ccf']==selected_ccf]
        clip_dict['promos_ccf']=clip_dict['promos_ccf'][clip_dict['promos_ccf']==selected_ccf]
        
        #get cn city skits
        cn_skits=clip_dict['bumps'][np.array(['CN_City_Skit' in bump for bump in clip_dict['bumps']])==True]
        
        length_of_other=0

        for showpos,show in enumerate(shows):
            if show=='Top 5':
                master_order,temp_length_other=self.Top_5(master_order,shows,showpos,clip_dict,flag_dict,length_dict,length_of_other)
                length_of_other+=temp_length_other
                continue
            
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
            
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)
            
            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-8] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-8]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break
                
            output=get_commercial_break_length(show_segments)
            if type(output)==tuple:
                commercial_length,show_segs_include_intros=output
            else:
                commercial_length=output
                show_segs_include_intros=False
            
            #categorize the bumps
            show_bumps=clip_dict['bumps'][np.array([show+' -' in bump for bump in clip_dict['bumps']])==True]
            
            generic_bump=clip_dict['bumps'][np.array(['Neutral -' in bump for bump in clip_dict['bumps']])==True]
            
            if len(show_bumps)!=0:
                bumps_list=show_bumps.copy()
            else:
                bumps_list=generic_bump.copy()
                               
            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    start_id=random.choice(bumps_list)
                    length_of_other+=get_length(start_id)
                    
                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    if commercial_length<length_of_other:
                        length_of_other=length_of_other-commercial_length
                    else:
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                        length_of_other=0
                    
                    master_order.append(start_id)
                    master_order.append(segment)
                    if show_segs_include_intros==False:
                        random_bump_out=random.choice(bumps_list)
                        random_bump_in=random.choice(bumps_list)
                        
                        counter=0
                        while random_bump_out==random_bump_in:
                            if counter==5:
                                break
                            random_bump_out=random.choice(bumps_list)
                            counter+=1
                                                    
                        length_of_other+=length_vids(list((random_bump_out,random_bump_in))).sum()
                        
                        master_order.append(random_bump_out)
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                        length_of_other=0
                            
                        master_order.append(random_bump_in)
                
                elif segpos==len(show_segments)-2 and show_segs_include_intros==True:
                    #dont need to define the bump & schedule here
                    #should carry over from the earlier loop
                    #the if segpos==len(show_segments)-3 bit continues past and
                    #keeps random_bump & schedule in memory
                    master_order.append(random_bump_in)
                    master_order.append(segment)
                    continue

                #if not the final segment
                elif segpos<len(show_segments)-1:
                    master_order.append(segment)
                    random_bump_out=random.choice(bumps_list)
                    random_bump_in=random.choice(bumps_list)

                    counter=0
                    while random_bump_out==random_bump_in:
                        if counter==5:
                            break
                        random_bump_out=random.choice(bumps_list)
                        counter+=1
                    
                    if (segpos==len(show_segments)-2 and show_segs_include_intros==False) or\
                    (segpos==len(show_segments)-3 and show_segs_include_intros==True):
                        if showpos<(len(shows)-2):
                            potential_schedules=clip_dict['schedules'][np.array([shows[showpos+1]+' '+shows[showpos+2] in entry for entry in clip_dict['schedules']])]
                            if len(potential_schedules)!=0:
                                sel_sched=random.choice(potential_schedules)
                                length_of_other+=get_length(sel_sched)


                    length_of_other+=length_vids(list((random_bump_out,random_bump_in))).sum()

                            
                    master_order.append(random_bump_out)
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    length_of_other=0
                    
                    if segpos==len(show_segments)-3 and show_segs_include_intros==True:
                        if showpos<(len(shows)-2) and len(potential_schedules)!=0:
                            master_order.append(sel_sched)
                        continue
                           
                    if showpos<(len(shows)-2) and len(potential_schedules)!=0 and \
                    segpos==len(show_segments)-2 and show_segs_include_intros==False:
                        master_order.append(sel_sched)
                    master_order.append(random_bump_in)

                #else if the final segment
                else:
                    master_order.append(segment)
                    master_order.append('BREAK END OF SHOW')
                    
                    #20% chance of adding in a CN Groovies to the block
                    if showpos==len(shows)//2 and random.random()>0.8:
                        print('ADDING GROOVIES')
                        master_order.append(self.paths['groovies_intro'])
                        random_groovie=random.choice(clip_dict['groovies'])
                        master_order.append(random_groovie)
                        master_order.append(self.paths['groovies_outro'])
                        
                        length_of_other+=get_length(self.paths['groovies_intro'])
                        length_of_other+=get_length(random_groovie)
                        length_of_other+=get_length(self.paths['groovies_outro'])

        return(master_order)

    def CN_Powerhouse(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        master_order=[]
        
        powerhouse_years=['1998','1999','2000','2001','2002','2003','2004']
        
        #get commercials & promos from years which TOM2 toonami aired
        clip_dict['promos_cn'],length_dict['promos_cn']=trim_years(clip_dict['promos_cn'],length_dict['promos_cn'],powerhouse_years)
        clip_dict['commercials'],length_dict['commercials']=trim_years(clip_dict['commercials'],length_dict['commercials'],powerhouse_years)
        
        #trim out CN promos so there's 1 of each type
        clip_dict['promos_cn'],length_dict['promos_cn']=trim_promos(clip_dict['promos_cn'],length_dict['promos_cn'])
        
        #select just one ccf to play
        selected_ccf=random.choice(clip_dict['promos_ccf'])
        length_dict['promos_ccf']=length_dict['promos_ccf'][clip_dict['promos_ccf']==selected_ccf]
        clip_dict['promos_ccf']=clip_dict['promos_ccf'][clip_dict['promos_ccf']==selected_ccf]
        
        potential_schedules=clip_dict['schedules'][np.array([shows[0]+' then '+shows[1] in entry for entry in clip_dict['schedules']])]
        if len(potential_schedules)!=0:
            sel_sched=random.choice(potential_schedules)
            master_order.append(sel_sched)
            length_of_other=get_length(sel_sched)
        else:
            length_of_other=0


        for showpos,show in enumerate(shows):
            if show=='Top 5':
                master_order,temp_length_other=self.Top_5(master_order,shows,showpos,clip_dict,flag_dict,length_dict,length_of_other)
                length_of_other+=temp_length_other
                continue
            
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
            
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)
            
            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-8] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-8]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break
                
            output=get_commercial_break_length(show_segments)
            if type(output)==tuple:
                commercial_length,show_segs_include_intros=output
            else:
                commercial_length=output
                show_segs_include_intros=False
            
            #categorize the bumps
            show_bumps_in=clip_dict['bumps'][np.array(['FadeIn '+show+' -' in bump for bump in clip_dict['bumps']])==True]
            show_bumps_out=clip_dict['bumps'][np.array(['FadeOut '+show+' -' in bump for bump in clip_dict['bumps']])==True]
            
            generic_in=clip_dict['bumps'][np.array(['FadeIn CN Generic' in bump for bump in clip_dict['bumps']])==True]
            generic_out=clip_dict['bumps'][np.array(['FadeOut CN Generic' in bump for bump in clip_dict['bumps']])==True]

            if len(show_bumps_in)==0:
                bump_in=generic_in.copy()
            else:
                bump_in=show_bumps_in.copy()
                
            if len(show_bumps_out)==0:
                bump_out=generic_out.copy()
            else:
                bump_out=show_bumps_out.copy()
                
            #get an intro station id that matches the show about to be on
            matching_stations=clip_dict['station_ids'][np.array([show in bump for bump in clip_dict['station_ids']])==True]
            if len(matching_stations)==0:
                matching_stations=clip_dict['station_ids'].copy()

            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    start_id=random.choice(matching_stations)
                    length_of_other+=get_length(start_id)
                    
                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    if commercial_length<length_of_other:
                        length_of_other=length_of_other-commercial_length
                    else:
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                        length_of_other=0
                    
                    master_order.append(start_id)
                    master_order.append(segment)
                    if show_segs_include_intros==False:
                        random_bump_out=random.choice(bump_out)
                        random_bump_in=random.choice(bump_in)
                                                    
                        length_of_other+=length_vids(list((random_bump_out,random_bump_in))).sum()
                        
                        master_order.append(random_bump_out)
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                        length_of_other=0
                            
                        master_order.append(random_bump_in)
                
                elif segpos==len(show_segments)-2 and show_segs_include_intros==True:
                    #dont need to define the bump & schedule here
                    #should carry over from the earlier loop
                    #the if segpos==len(show_segments)-3 bit continues past and
                    #keeps random_bump & schedule in memory
                    master_order.append(random_bump_in)
                    master_order.append(segment)
                    continue

                #if not the final segment
                elif segpos<len(show_segments)-1:
                    master_order.append(segment)
                    random_bump_out=random.choice(bump_out)
                    random_bump_in=random.choice(bump_in)
                    
                    if (segpos==len(show_segments)-2 and show_segs_include_intros==False) or\
                    (segpos==len(show_segments)-3 and show_segs_include_intros==True):
                        if showpos<(len(shows)-2):
                            potential_schedules=clip_dict['schedules'][np.array([shows[showpos+1]+' then '+shows[showpos+2] in entry for entry in clip_dict['schedules']])]
                            if len(potential_schedules)!=0:
                                sel_sched=random.choice(potential_schedules)
                                length_of_other+=get_length(sel_sched)


                    length_of_other+=length_vids(list((random_bump_out,random_bump_in))).sum()

                            
                    master_order.append(random_bump_out)
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    length_of_other=0
                    
                    if segpos==len(show_segments)-3 and show_segs_include_intros==True:
                        continue
                           
                    master_order.append(random_bump_in)

                #else if the final segment
                else:
                    master_order.append(segment)
                    master_order.append('BREAK END OF SHOW')
                    
                    #5% chance of adding in a CN Groovies to the block
                    if showpos==len(shows)//2 and random.random()>0.8:
                        print('ADDING GROOVIES')
                        master_order.append(self.paths['groovies_intro'])
                        random_groovie=random.choice(clip_dict['groovies'])
                        master_order.append(random_groovie)
                        master_order.append(self.paths['groovies_outro'])
                        
                        length_of_other+=get_length(self.paths['groovies_intro'])
                        length_of_other+=get_length(random_groovie)
                        length_of_other+=get_length(self.paths['groovies_outro'])

                    #length is already accounted for in prior loop, no need to recalc
                    if showpos<(len(shows)-2) and len(potential_schedules)!=0:
                        master_order.append(sel_sched)


        return(master_order)

    def Toonami_TOM2(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        master_order=[]
        
        TOM2_years=['2000','2001','2002','2003']
        
        #get commercials & promos from years which TOM2 toonami aired
        clip_dict['promos_cn'],length_dict['promos_cn']=trim_years(clip_dict['promos_cn'],length_dict['promos_cn'],TOM2_years)
        clip_dict['commercials'],length_dict['commercials']=trim_years(clip_dict['commercials'],length_dict['commercials'],TOM2_years)
        
        #trim out CN promos so there's 1 of each type
        clip_dict['promos_cn'],length_dict['promos_cn']=trim_promos(clip_dict['promos_cn'],length_dict['promos_cn'])
        
        #select just one ccf to play
        selected_ccf=random.choice(clip_dict['promos_ccf'])
        length_dict['promos_ccf']=length_dict['promos_ccf'][clip_dict['promos_ccf']==selected_ccf]
        clip_dict['promos_ccf']=clip_dict['promos_ccf'][clip_dict['promos_ccf']==selected_ccf]
        
        #initialize at 0
        length_of_other=0
        
        #get schedules
        schedules=clip_dict['bumps'][np.array(['schedule - ' in bump for bump in clip_dict['bumps']])]
        
        for showpos,show in enumerate(shows):            
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
            all_show_files=show_files.copy()
            
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)
            
            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-8] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-8]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break
                
            
            #look through all possible configurations of 4 shows that contains current show
            #check to see if matching schedules exists with format 'schedule - show1 show2 show3 show4.mp4'
            #if it does, pick the one where the show is in the first half of the 4
            start=max([0,showpos-3])
            end=min([len(shows)-3,showpos+1])
            sched_orders=[]
            for x in range(start,end):
                sched_orders.append(shows[x:x+4])
            for order in sched_orders:
                if sum([" ".join(order) in bump for bump in schedules]):
                    if show in order[:len(order)//2]:
                        sel_sched=schedules[np.array([" ".join(order) in bump for bump in schedules])]
                        sel_sched_length=get_length(sel_sched[0])
                        
                
            #get the total length of all commercial breaks for the current show
            output=get_commercial_break_length(show_segments)
            if type(output)==tuple:
                commercial_length,show_segs_include_intros=output
            else:
                commercial_length=output
                show_segs_include_intros=False
            
            
            #check the episode number of the show and match it to its corresponding era in the config file
            #this is done to ensure that bumpers kinda match the current progression of the show
            #get the episode number of the show
            ep_num=int(np.where(all_show_files==show_segments[0])[0]/len(show_segments))
            #categorize the bumps
            show_bumps_in=clip_dict['bumps'][np.array(['FadeIn_'+show in bump for bump in clip_dict['bumps']])]
            show_bumps_out=clip_dict['bumps'][np.array(['FadeOut_'+show in bump for bump in clip_dict['bumps']])]
            #cross off bumps that occur in eras outside the current one of the show
            show_eras=[era for era in self.paths['eras'][show].keys()]
            for era in show_eras:
                if ep_num in self.paths['eras'][show][era]:
                    continue
                else:
                    show_bumps_in=show_bumps_in[np.array([era not in bump for bump in show_bumps_in])]
                    show_bumps_out=show_bumps_out[np.array([era not in bump for bump in show_bumps_out])]
                    

            
            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    
                    #get the toonami intro clip if one exists
                    intro_clip=clip_dict['bumps'][np.array(['Intro - '+show in bump for bump in clip_dict['bumps']])]
                    if intro_clip:
                        intro_clip=intro_clip[0]
                        length_of_other+=get_length(intro_clip)
                    else:
                        length_of_other+=0
                    
                    #start the block off with some commercials
                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    length_of_other=0
                    
                    #if this is the first segment of the first show, add the overall toonami intro
                    if showpos==0:
                        master_order.append(self.paths['intro'])

                    #add the show intro clip and then the first episode segment
                    master_order.append(intro_clip)
                    master_order.append(segment)
                    
                    #if show opening song/credits aren't separate, select some bumpers to fade in/out to commercial 
                    if show_segs_include_intros==False:
                        random_bump_out=random.choice(show_bumps_out)
                        random_bump_in=random.choice(show_bumps_in)
                         
                        #get the length of the two bumpers
                        length_of_other+=length_vids(list((random_bump_out,random_bump_in))).sum()
                        if segpos==len(show_segments)-2 and len(sel_sched):
                            length_of_other+=sel_sched_length
                        
                        #add the outgoing bumper
                        master_order.append(random_bump_out)
                        #put in commercials
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                        length_of_other=0
                        
                        
                        if segpos==len(show_segments)-2 and len(sel_sched):
                            master_order.append(sel_sched[0])
                            
                        master_order.append(random_bump_in)
                
                #leftover chunk of code from CN stuff - has not been edited for toonami yet
                elif segpos==len(show_segments)-2 and show_segs_include_intros==True:
                    if showpos<(len(shows)-1):
                        potential_schedules=clip_dict['schedules'][np.array([shows[showpos]+' '+shows[showpos+1] in entry for entry in clip_dict['schedules']])]
                        if len(potential_schedules)!=0:
                            random_bump_in=random.choice(potential_schedules)
                        else:
                            random_bump_in=random.choice(possible_bumps)
                    else:
                        random_bump_in=random.choice(possible_bumps)

                    master_order.append(random_bump_in)
                    master_order.append(segment)
                    continue
                #above is leftover chunk of code from CN stuff - largely untested - probably does not work

                elif segpos<len(show_segments)-1:
                    master_order.append(segment)
                    random_bump_out=random.choice(show_bumps_out)
                    random_bump_in=random.choice(show_bumps_in)

                    counter=0
                    while random_bump_in in master_order:
                        random_bump_in=random.choice(show_bumps_in)
                        counter+=1
                        if counter==5:
                            break
                    counter=0
                    while random_bump_out in master_order:
                        random_bump_out=random.choice(show_bumps_out)
                        counter+=1
                        if counter==5:
                            break

                            
                    length_of_other+=length_vids(list((random_bump_out,random_bump_in))).sum()
                    if segpos==len(show_segments)-2 and len(sel_sched):
                        length_of_other+=sel_sched_length

                            
                    master_order.append(random_bump_out)
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    length_of_other=0
                    
                    if segpos==len(show_segments)-3 and show_segs_include_intros==True:
                        continue
                    elif segpos==len(show_segments)-2 and len(sel_sched):
                        master_order.append(sel_sched[0])
                    master_order.append(random_bump_in)

                else:
                    master_order.append(segment)
                    
                    credit_file=clip_dict['credits'][np.array([show+' Credits' in credit for credit in clip_dict['credits']])]
                    if credit_file:
                        master_order.append(credit_file[0])
                        length_of_other+=get_length(credit_file[0])
                    
                    master_order.append('BREAK END OF SHOW')

                    #25% of blocks will have a long promo. they're unique so dont want them playing ALL the time
                    if showpos==len(shows)//2 and random.random()>0.75:
                        print('ADDING LONG PROMO')
                        
                        all_long_promos=np.append(clip_dict['long_promo'],clip_dict['vg'])
                        all_long_lengths=np.append(length_dict['long_promo'],length_dict['vg'])
                        random_long_promo=random.choice(all_long_promos)
                        length_of_other+=all_long_lengths[all_long_promos==random_long_promo]
                        master_order.append(random_long_promo)
                        
                        if showpos!=len(shows)-1:
                            transition=clip_dict['bumps'][np.array(['thats '+show+' next '+shows[showpos+1] in bump for bump in clip_dict['bumps']])]
                            if len(transition)>0:
                                random_trans=random.choice(transition)
                                master_order.append(random_trans)
                                length_of_other+=length_dict['bumps'][clip_dict['bumps']==random_trans]
                        print(random_long_promo)
                        
                    else:
                        
                        if showpos!=len(shows)-1:
                            transition=clip_dict['bumps'][np.array(['thats '+show+' next '+shows[showpos+1] in bump for bump in clip_dict['bumps']])]
                            if len(transition)>0:
                                random_trans=random.choice(transition)
                                master_order.append(random_trans)
                                length_of_other+=length_dict['bumps'][clip_dict['bumps']==random_trans]

                        
                        for key in flag_dict.keys():
                            if key=='promos_toonami':
                                flag_dict[key]=1
                            else:
                                flag_dict[key]=0

        master_order.append(self.paths['outro'])
        return(master_order)

    
    def Nick_at_Nite(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        master_order=[]
        
        for showpos,show in enumerate(shows):
            show_folder_loc=self.possible_shows[np.array([show in ps for ps in self.possible_shows])==True][0]
            show_files=get_full_path(show_folder_loc+'/mp4/Subsections/')
            show_files.sort()
        
            show_files=self.remove_past_episodes(show,show_files,type_dict[show],replace=True)

            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-8] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-8]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break

            commercial_length=get_commercial_break_length(show_segments)

            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    random_jingle=random.choice(clip_dict['bumps'])
                    while random_jingle in master_order:
                        random_jingle=random.choice(clip_dict['bumps'])
                        
                    if showpos<=len(shows)-2:
                        if showpos not in np.arange(len(shows)-2,len(shows)):
                            potential_schedules_three=clip_dict['schedules'][np.array([shows[showpos]+' '+shows[showpos+1]+' '+shows[showpos+2] in entry for entry in clip_dict['schedules']])]
                            potential_schedules_two=clip_dict['schedules'][np.array([shows[showpos]+' '+shows[showpos+1]+' End' in entry for entry in clip_dict['schedules']])]
                        elif showpos in np.arange(len(shows)-2,len(shows)-1):
                            potential_schedules_three=np.array([])
                            potential_schedules_two=clip_dict['schedules'][np.array([shows[showpos]+' '+shows[showpos+1]+' End' in entry for entry in clip_dict['schedules']])]
                        else:
                            potential_schedules_three=np.array([])
                            potential_schedules_two=np.array([])

                        if not potential_schedules_two and not potential_schedules_three:
                            pass
                        else:
                            if potential_schedules_three and not potential_schedules_two:
                                potential_schedules=potential_schedules_three
                            elif potential_schedules_two and not potential_schedules_three:
                                potential_schedules=potential_schedules_two
                            else:
                                potential_schedules=np.append(potential_schedules_three,potential_schedules_two)
                            random_schedule=random.choice(potential_schedules)

                    if potential_schedules_two or potential_schedules_three:
                        length_of_other=length_vids(list((random_schedule,random_jingle))).sum()
                    else:
                        length_of_other=get_length(random_jingle)

                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    
                    master_order.append(random_jingle)
                    
                    if showpos<=len(shows)-2 and (potential_schedules_two or potential_schedules_three):
                        master_order.append(random_schedule)


                master_order.append(segment)
                
                if segpos<len(show_segments)-1:
                    random_jingle=random.choice(clip_dict['bumps'])
                    while random_jingle in master_order:
                        random_jingle=random.choice(clip_dict['bumps'])
                    length_of_other=get_length(random_jingle)

                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    
                    master_order.append(random_jingle)
                elif segpos==len(show_segments)-1:
                    master_order.append('BREAK END OF SHOW')
                    
        print(master_order)
        return(master_order)
                


    
    def save_to_txt(self,master_order,name):
        savepath=self.allpaths['save_path']
        np.savetxt(savepath+name,np.array(['file '+"'"+entry+"'" for entry in master_order]),fmt='%s')
                    
    def generate(self,
                 showlist,
                 reuse_bumps=True,
                 use_all_commercials=False,
                 recalc_length=False,
                 user_defined_month=None
                ):
        
        #if you want to use all commercials regardless of channel separation
        if use_all_commercials==False:
            #get filepaths for all video files in each subheading under 'clips' in the channel config file
            self.clip_dict=self.retrieve_clips(self.paths['clips'])
        elif use_all_commercials==True:
            self.clip_dict=self.retrieve_clips(self.allpaths['all_commercials'])
            for i,key in enumerate(list(self.clip_dict.keys())):
                if i==0:
                    self.clip_dict['commercials']=self.clip_dict[key]
                    del self.clip_dict[key]
                else:
                    self.clip_dict['commercials']=np.append(self.clip_dict['commercials'],self.clip_dict[key])
                    del self.clip_dict[key]
        
        
        #isolate clips based on specific month. if none specified, use current month at time of generation
        if user_defined_month:
            self.clip_dict=self.correct_clip_timeofyear(self.clip_dict,user_defined_month,self.months)
        else:
            self.clip_dict=self.correct_clip_timeofyear(self.clip_dict,self.curmonth,self.months)
        
        #THIS WILL NEED TO BE CHANGED AT SOME POINT PROBABLY
        #setup probabilities for clip dictionaries that will be considered in commercials
        #make sure to exclude keywords within the 'clips' subheading that you don't want considered
        #commercials don't need probabilities since they're defined as the remainder of (1 - sum(P)) where P is probability of all promos
        self.probability_dict={}
        for key in self.clip_dict.keys():
            if key!='commercials' and key!='bumps' and key!='schedules' and key!='credits' and key!='long_promo'\
            and key!='intro' and key!='outro' and key!='vg' and key!='station_ids' and key!='groovies':
                self.probability_dict[key]=0.05
            
        #select if you want to write used bumps to a file so they don't repeat next broadcast
        #mainly applicable for Adult Swim that has unique bumper cards
        if reuse_bumps==False and 'bump_logs' in self.paths.keys():
            self.clip_dict['bumps']=self.remove_used_bumps(self.bumpdict,self.clip_dict,replace=True)
        elif reuse_bumps==False:
            print('bump_logs path not specified in filepaths dictionary. Please update this and try again.')
            print('Reusing bumps...')
        
        #get lengths of all the video clips
        self.length_dict={}
        for key in self.clip_dict.keys():
            recalc_bool=False
            #check to see if saved video length file already exists
            if os.path.exists(self.paths['clips'][key]+'_dir_lengths.npy'):#and not recalc_length:
                #check the month it was made
                made_month=(datetime.datetime.utcfromtimestamp(os.path.getmtime(self.paths['clips'][key]+'_dir_lengths.npy'))-datetime.timedelta(hours=4)).strftime('%B')
                #if month of file generation != current month, file lengths need to be recalculated to accomodate for change in considered clips
                if made_month!=self.curmonth:
                    self.length_dict[key]=length_vids(self.clip_dict[key])
                    np.save(self.paths['clips'][key]+'_dir_lengths.npy',self.length_dict[key])
                #else if the flag to manually force length recalc is on
                elif recalc_length:
                    self.length_dict[key]=length_vids(self.clip_dict[key])
                    np.save(self.paths['clips'][key]+'_dir_lengths.npy',self.length_dict[key])
                #else use the file that exists
                else:
                    self.length_dict[key]=np.load(self.paths['clips'][key]+'_dir_lengths.npy')
            #if no length file exists then make one    
            else:
                self.length_dict[key]=length_vids(self.clip_dict[key])
                np.save(self.paths['clips'][key]+'_dir_lengths.npy',self.length_dict[key])
            
        if self.blocktype=='Adult Swim':
            master_order=self.Adult_Swim(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='FOX':
            master_order=self.FOX(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='Nick at Nite':
            master_order=self.Nick_at_Nite(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='Custom':
            master_order=self.Create_Block(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='Boomerang':
            master_order=self.Boomerang(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='Cartoon Network City':
            master_order=self.CN_City(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='Cartoon Network Powerhouse':
            master_order=self.CN_Powerhouse(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
        elif self.blocktype=='Toonami TOM2':
            master_order=self.Toonami_TOM2(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
            
        print('Done!')
        return(master_order)
