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

    mydate=datetime.datetime.now()
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

        #while there's still at least 10 seconds left in the commercial block, continue to loop through and add more commercials
        while commercial_block_size>remainder_length:

            #calculate the probability that the next pick in the commercial block will be a commercial
            #this probability is defined as the remainder leftover when you subtract the probabilities
            #of all other types in the flag_dict
            commercial_probability=1-sum([flag_dict[key] for key in flag_dict.keys()])
            #assign all probabilities
            probabilities=[flag_dict[key] for key in flag_dict.keys()]
            probabilities.append(commercial_probability)
            #randomly select which 'type' of commercial will be next from these 4 specific options - this can be modified accordingly
            possible_types=list(flag_dict.keys())
            possible_types.append('commercials')
            commercial_type=random.choices(possible_types,weights=probabilities)[0]

            #check the commercial type and cross reference the selected promo against the lengths calculated earlier
            commercial=random.choice(clip_dict[commercial_type])
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
            #if the commercial is part of the last 30 files in the order, toss it out for a new one to keep it fresh
            elif commercial in master_order[-30:]:
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
        master_order.append('/data/media/block_media/Archived Bumps & Commercials/AdultSwim/Adult Swim Advisory.mp4')
        master_order.append('/data/media/block_media/Archived Bumps & Commercials/AdultSwim/Bumps/Pool - Intro.mp4')

        #start looping through each show in the list
        for showpos,show in enumerate(shows):

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

                else:
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
                    elif 'Numbers Game' in fadeout and fadeout in master_order:
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
                    elif 'Numbers Game' in fadein and fadein in master_order:
                        print('HEY! DUPLICATE NUMBERS GAME! Removing...')
                        print(fadein)
                        while 'Numbers Game' in fadein: #possible infinite loop here, fix this
                            fadein=random.sample(list(fadein_bumps),1)[0]
                            
                            
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
                    if show in shows[:int(len(shows)/2)]:
                        end_bump=random.sample(list(bw_bumps),1)[0]
                        if end_bump in master_order:
                            while end_bump in master_order:
                                end_bump=random.sample(list(bw_bumps),1)[0]


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
    
    def Top_5(self,master_order,shows,showpos,clip_dict,flag_dict,length_dict,
             possible_entries=[
                 'Camp Lazlo','Codename Kids Next Door', 'Courage the Cowardly Dog',
                 'Cow and Chicken','Dexters Laboratory','Ed Edd n Eddy','Johnny Bravo',
                 'Powerpuff Girls','The Grim Adventures of Billy and Mandy'],
              possible_3parters=['Cow and Chicken','Dexters Laboratory','Johnny Bravo',
                                 'The Grim Adventures of Billy and Mandy'],
              possible_2parters=['Camp Lazlo','Codename Kids Next Door','Courage the Cowardly Dog',
                                 'Ed Edd n Eddy','Powerpuff Girls','The Grim Adventures of Billy and Mandy'],
              top5_folder='/data/media/block_media/Archived Bumps & Commercials/Cartoon Network/Bumps/Top 5/',
              top5_year='2002'
                 ):
        
        top5_bumps=get_full_path(top5_folder)
        top5_bumps=top5_bumps[np.array([top5_year in tb for tb in top5_bumps])==True]
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
            show_files=show_files[np.array(['pt1' not in segment for segment in show_files])==True]
            show_files=show_files[np.array(['pt2' not in segment for segment in show_files])==True]
            ep_selector=random.choice(show_files)[:-8]
            rsegments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            while len(rsegments)>4:
                ep_selector=random.choice(show_files)[:-8]
                rsegments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            rnum=str(random.choice([1,2])).zfill(3)
            show_segments.append(rsegments[np.array([rnum in segment for segment in rsegments])==True][0])
        
        commercial_length=get_commercial_break_length(show_segments)

        for segpos,segment in enumerate(show_segments):
            tmp_cblock,flag_dict=self.commercial_generator(commercial_length,flag_dict,master_order,clip_dict,length_dict)
            for tmp_c in tmp_cblock:
                master_order.append(tmp_c)
            
            
            if showpos<(len(shows)-2) and segpos==(len(show_segments)-2):
                potential_schedules=clip_dict['schedules'][np.array([shows[showpos]+' '+shows[showpos+1] in entry for entry in clip_dict['schedules']])]
                if len(potential_schedules)!=0:
                    random_schedule=random.choice(potential_schedules)
                    master_order.append(random_schedule)
            if segpos==0:
                master_order.append(top5_folder+top5_year+' Top 5 Intro.mp4')
            master_order.append(top5_folder+top5_year+' Top 5 Number '+str(5-segpos)+'.mp4')
            master_order.append(segment)
            if segpos!=len(show_segments)-1:
                master_order.append(random.choice(fadeout_bumps))
            else:
                master_order.append(top5_folder+top5_year+' Top 5 Outro.mp4')
                master_order.append('BREAK END OF SHOW')

        return(master_order)

        
        
    
    def Cartoon_Network(self,shows,type_dict,clip_dict,flag_dict,length_dict):
        master_order=[]
        
        for showpos,show in enumerate(shows):
            if show=='Top 5':
                master_order=self.Top_5(master_order,shows,showpos,clip_dict,flag_dict,length_dict)
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
            show_bumps=clip_dict['bumps'][np.array([show+' - ' in bump for bump in clip_dict['bumps']])==True]
            neutral_bumps=clip_dict['bumps'][np.array(['Neutral - ' in bump for bump in clip_dict['bumps']])==True]
            
            if len(show_bumps)==0:
                possible_bumps=neutral_bumps
            elif len(show_bumps)<4:
                possible_bumps=np.concatenate((show_bumps,neutral_bumps))
            else:
                possible_bumps=show_bumps

            for segpos,segment in enumerate(show_segments):

                if segpos==0:
                    random_bump_in=random.choice(possible_bumps)
                    length_of_other=get_length(random_bump_in)
                    
                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    
                    master_order.append(random_bump_in)
                    master_order.append(segment)
                    if show_segs_include_intros==False:
                        random_bump=random.choice(possible_bumps)
                        random_bump_out=random.choice(possible_bumps)
                        random_bump_in=random.choice(possible_bumps)
                        
                        counter=0
                        while random_bump_in==random_bump_out:
                            random_bump_in=random.choice(possible_bumps)
                            counter+=0
                            if counter==10:
                                break
                            
                        length_of_other=length_vids(list((random_bump_out,random_bump_in))).sum()
                        
                        master_order.append(random_bump_out)
                        tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                        for tmp_c in tmp_cblock:
                            master_order.append(tmp_c)
                            
                        master_order.append(random_bump_in)
                
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

                elif segpos<len(show_segments)-1:
                    master_order.append(segment)
                    random_bump_out=random.choice(possible_bumps)
                    random_bump_in=random.choice(possible_bumps)

                    counter=0
                    while random_bump_in==random_bump_out:
                        random_bump_in=random.choice(possible_bumps)
                        counter+=0
                        if counter==10:
                            break
                            
                    length_of_other=length_vids(list((random_bump_out,random_bump_in))).sum()

                            
                    master_order.append(random_bump_out)
                    tmp_cblock,flag_dict=self.commercial_generator(commercial_length-length_of_other,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)
                    
                    if segpos==len(show_segments)-3:
                        continue
                    master_order.append(random_bump_in)

                else:
                    master_order.append(segment)
                    random_bump=random.choice(possible_bumps)
                    master_order.append(random_bump)
                    master_order.append('BREAK END OF SHOW')


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
        
        if use_all_commercials==False:
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
        
        if user_defined_month:
            self.clip_dict=self.correct_clip_timeofyear(self.clip_dict,user_defined_month,self.months)
        else:
            self.clip_dict=self.correct_clip_timeofyear(self.clip_dict,self.curmonth,self.months)
        
        #THIS WILL NEED TO BE CHANGED AT SOME POINT PROBABLY
        self.probability_dict={}
        for key in self.clip_dict.keys():
            if key!='commercials' and key!='bumps' and key!='schedules':
                self.probability_dict[key]=0.05
            
        if reuse_bumps==False and 'bump_logs' in self.paths.keys():
            self.clip_dict['bumps']=self.remove_used_bumps(self.bumpdict,self.clip_dict,replace=True)
        elif reuse_bumps==False:
            print('bump_logs path not specified in filepaths dictionary. Please update this and try again.')
            print('Reusing bumps...')
        
        self.length_dict={}
        for key in self.clip_dict.keys():
            if os.path.exists(self.paths['clips'][key]+'_dir_lengths.npy') and not recalc_length:
                self.length_dict[key]=np.load(self.paths['clips'][key]+'_dir_lengths.npy')
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
        elif self.blocktype=='Cartoon Network':
            master_order=self.Cartoon_Network(showlist,self.showtypes,self.clip_dict,self.probability_dict,self.length_dict)
            
        print('Done!')
        return(master_order)