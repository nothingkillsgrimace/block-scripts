import os
import numpy as np
import random
import subprocess
import shutil
import datetime

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

#this function will return the lengths for a series of file when given a list of file paths
def length_vids(files):
    return np.array([get_length(entry) for entry in files])

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

class Block_Assembler:
    
    months=np.array(['January','February','March','April','May','June','July','August','September',
           'October','November','December'])

    mydate=datetime.datetime.now()
    curmonth=mydate.strftime("%B")
    
    def __init__(self,blocktype,paths,showlist,showtypes,bumpdict):
        self.blocktype=blocktype
        self.allpaths=paths
        self.paths=paths[blocktype]
        self.showlist=showlist
        self.showtypes=showtypes
        self.bumpdict=bumpdict
        
    def retrieve_clips(self,blocktype,clips): #feed it self.blocktype & self.paths
        clip_dict={}
        for key in clips.keys():
            clip_dict[key]=get_full_path(clips[key])
        return clip_dict
        
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
                          bump_recorder_folder_path=self.allpaths['past_bumps'],
                         replace=False,r_kw1='/Volumes/Media and Storage Desktop/',r_kw2='/Users/bwal/Desktop'):
        #open up a couple text files that list bumps used in prior broadcasts
        #this list will be cross-referenced against all bumps and bumps that have been used before
        #will be removed. this helps to keep things fresh. nobody wants to see the same bump every time!

        bump_contents={}
        for b in bump_dict.keys():
            with open(bump_recorder_folder_path+bump_dict[b]['filename'],'r+') as f:
                f.seek(0)
                bump_contents[b]=f.readlines()

            for bc in bump_contents[b]: 
                if replace==True:
                    bc=bc.replace(r_kw1,r_kw2)

                if bc[:-1] in clip_dict['bumps']:
                    index=np.argwhere(clip_dict['bumps']==bc[:-1])[0,0]
                    clip_dict['bumps']=np.delete(clip_dict['bumps'],index)

            #if the past bumps used exceed 90% of the total amount of bumps, 
            #they're all thrown back into the possible selection pool and 
            #the text file recording past bumps used is whiped clean
            if len(bump_contents)/len(clip_dict['bumps'][[bump_dict[b]['keyword'] in entry for\
                                                          entry in clip_dict['bumps']]])>0.9:
                with open(bump_recorder_folder_path+bump_dict[b]['filename'],'w') as f:
                                      f.seek(0)


        return(clip_dict['bumps'])

    #this function is responsible for generating commercial blocks
    def commercial_generator(self,length,probs,master_order,
                             clip_dict,length_dict
                            ):

        #initialize our commercial list as an empty list
        commercials_list=[]

        #the total size of all commercials is equal to the length parameter given to the function (in seconds)
        commercial_block_size=length

        #assign probality dictionary to a temp variable
        flag_dict=probs

        #while there's still at least 10 seconds left in the commercial block, continue to loop through and add more commercials
        while commercial_block_size>10:

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
                             path_to_log=self.allpaths['past_episodes'],
                            replace=False,r_kw1='/Volumes/Media and Storage Desktop/',r_kw2='/Volumes/Elements/'):
        with open(path_to_log+show+'.txt','r+') as f:
            f.seek(0)
            past_episodes_used=f.readlines()

        if len(past_episodes_used)>0:
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

    def write_past_shows(self,master_order,shows,
                        show_keyword=self.paths['shows'],
                        master_path=self.allpaths['past_episodes']):

        past_shows=np.array(master_order)[np.array([show_keyword in line for line in master_order])]
        show_uqid=np.array([])
        for i,entry in enumerate(past_shows):

            if i==0:
                show_uqid=np.append(show_uqid,shows[i])
                j=0
            else:
                if entry[:-5]==past_shows[i-1][:-5]:
                    show_uqid=np.append(show_uqid,shows[j])
                else:
                    j+=1
                    show_uqid=np.append(show_uqid,shows[j])

        for i,uqid in enumerate(show_uqid):
            with open(master_path+uqid+'.txt','r+') as f:
                f.seek(0)
                contents=f.readlines()

            with open(master_path+uqid+'.txt','w+') as f:
                if past_shows[i][6:] not in contents:
                    contents.insert(-1,past_shows[i]+"'\n")
                contents = "".join(contents)
                f.write(contents)

                
    def write_past_bumps(self,master_order,bump_dict,
                        folder=self.allpaths['past_bumps']):
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
                    
    def Custom_Block(self,shows,type_dict,clip_dict,flag_dict,length_dict,
                    commercial_start=True):
        
        master_order=[]
        
        if commercial_start=True:
            tmp_cblock,flag_dict=self.commercial_generator(210,flag_dict,master_order,clip_dict,length_dict)
            for tmp_c in tmp_cblock:
                master_order.append(tmp_c)
        
        for showpost,show in enumerate(shows):
            show_files=get_full_path(self.paths['shows']+show)
            
            if type_dict[show]=='serial':
                show_segments=show_files[np.array([show_files[0][:-5] in segment for segment in show_files])==True]
            elif type_dict[show]=='episodic':
                ep_selector=random.choice(show_files)[:-5]
                show_segments=show_files[np.array([ep_selector in segment for segment in show_files])==True]
            else:
                print('ERROR: Show type not specified properly. Show type must either be "serial" or "episodic" if a specific episode is not defined')
                print('Current show is ',show)
                break

            if showpos>0:
                tmp_cblock,flag_dict=self.commercial_generator(210,flag_dict,master_order,clip_dict,length_dict)
                for tmp_c in tmp_cblock:
                    master_order.append(tmp_c)
                
                intro_bump=random.sample(list(clip_dict['bumps']),1)[0]
                master_order.append(intro_bump)

            for segpos,segment in enumerate(show_segments):
                master_order.append(segment)

                if segpos<len(show_segments)-1:
                    fadeout_bump=random.sample(list(clip_dict['bumps']),1)[0]
                    master_order.append(fadeout_bump)

                    tmp_cblock,flag_dict=self.commercial_generator(210,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

                    fadein_bump=random.sample(list(clip_dict['bumps']),1)[0]
                    master_order.append(fadein_bump)

                    
    def Adult_Swim(self,shows,type_dict,clip_dict,flag_dict,length_dict,
                  ACTN_shows=['Inuyasha','Case Closed','Cowboy Bebop',
                              'Trigun']):
        
        master_order=[]

        #add the any intro bumps you want first in the order
        master_order.append('/Users/bwal/Desktop/Archived Bumps & Commercials/AdultSwim/Adult Swim Advisory.mp4')
        master_order.append('/Users/bwal/Desktop/Archived Bumps & Commercials/AdultSwim/Bumps/Pool - Intro.mp4')

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
            show_files=get_full_path(self.paths['shows']+show+'/mp4/Subsections/')

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
                if len(intro_bumps)<1:
                    show_starter_bump=random.sample(list(possible_bumps),1)[0]

                    if show_starter_bump in master_order:
                        while show_starter_bump in master_order: #possible infinite loop - should be fixed
                            show_starter_bump=random.sample(list(possible_bumps),1)[0]
                    master_order.append(show_starter_bump)

                else:
                    random_intro_bump=random.sample(list(intro_bumps),1)[0]
                    master_order.append(random_intro_bump)

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

                    master_order.append(fadeout)

                    #generate a commercial break using the function above, specificying the length of the block in seconds followed by
                    #the probabilities and then append each entry in the commercial block to the master file
                    tmp_cblock,flag_dict=self.commercial_generator(210,flag_dict,master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

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

                        master_order.append(end_bump)

                    elif show!=shows[-1]:
                        end_bump=random.sample(list(pic_bumps),1)[0]
                        if end_bump in master_order:
                            while end_bump in master_order:
                                end_bump=random.sample(list(pic_bumps),1)[0]

                        master_order.append(end_bump)

                    else:
                        continue

                    #put in some commercials between shows but make sure to start it off first with an [as] promo
                    tmp_cblock,flag_dict=self.commercial_generator(90,{'promos':1},master_order,clip_dict,length_dict)
                    for tmp_c in tmp_cblock:
                        master_order.append(tmp_c)

        print('Done!')
        return(master_order)
    
    def save_to_txt(self,master_order,name,
                    savepath=self.allpaths['save_path']):
        np.savetxt(savepath+name,np.array(['file '+"'"+entry+"'" for entry in master_order]),fmt='%s')
                    
    def generate(self):
        clip_dict=self.retrieve_clips(self.blocktype,self.paths['clips'])
        clip_dict=self.correct_clip_timeofyear(clip_dict,self.curmonth,self.months)
        
        #THIS WILL NEED TO BE CHANGED AT SOME POINT PROBABLY
        probability_dict={}
        for key in clip_dict.keys():
            if key!='commercials' and key!='bumps':
                probability_dict[key]=0.05
        clip_dict['bumps']=self.remove_used_bumps(self.bumpdict,clip_dict,replace=True)
        
        length_dict={}
        for key in clip_dict.keys():
            length_dict[key]=length_vids(clip_dict[key])
            
        if self.blocktype=='Adult Swim':
            master_order=self.Adult_Swim(self.showlist,self.showtypes,clip_dict,probability_dict,length_dict)
            
        return(master_order)