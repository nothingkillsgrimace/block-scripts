# block-scripts
Series of files used to generate custom TV blocks

Currently there are two methods for generating blocks:

1. Generic
2. Specific


Generic blocks are created using the 'Custom' command.
These blocks can only support shows & commercials, and do not discriminate clips by
type unlike the Specific blocks. Running these are fairly straightforward. First,
you link to the folders containing all of your shows in your main filepaths
dictionary. Next, you do the same with your various commercial folders.
You'll also need to create a list of the shows you want to include in the 
block in their order of appearance. Finally, specify the type
of each show within the type_dict variable. This lets the script know if
the show episodes should be played in order (serial) or randomly (episodic).

Specific blocks are created by calling the keyword of the specific block you'd like to make.
Currently supported Specific blocks are:
1. FOX
2. Nick at Nite
3. Cartoon Network
4. Boomerang
5. Adult Swim

At the moment, I haven't found a good way of making Specific blocks more flexible so they require a very specific folder structure and file-naming convention. 

I'll do my best to list them for each block type here:
# 1. FOX
Only one specific naming convention here (and it's optional). FOX traditionally puts a show-specific sponsor bump during the first fade to commercial for a show. These scripts are currently set to throw a random one of these into the broadcast if they contain the keywords "[SHOW NAME] Fade Out" somewhere in the filename. So, for instance, a file named "Simpsons Fade Out Taco Bell.mp4" is eligible to be inserted automatically at the start of the first commercial break for a show titled "Simpsons" since it contains the necessary keyword. The name of the show in the file needs to match the name of the show folder & show in the lineup, so make sure these are consistent.

# 2. Nick at Nite
Nick at Nite also has only one optional filename dependency. Nick at Nite blocks in the early 90s would usually include a 5-10 second jingle followed by a "schedule" bump that will list the upcoming show and either one or two of the following shows. These schedule bumps require a specific keyword in order to be inserted properly. The naming convention is:
If the schedule bumper covers three shows, the name needs to include "[SHOW NAME 1] [SHOW NAME 2] [SHOW NAME 3]" in the filename. Here, words in brackets are meant to be stand-ins for actual show titles used in your block. They all need to be one space apart from each other. An instance of this being done properly is: "Schedule - Happy Days The Wonder Years End Woman Reclining.mp4"
If the schedule bumper covers two shows, it's the same as above except after [SHOW NAME 2] you include the word "End". An example of this is: "Schedule - The Wonder Years The Munsters End Waiter.mp4".

# 3. Cartoon Network
For unique bumpers, files in the bump folder should be labeled "[SHOW NAME] - ". You also need several neutral bumpers (these are bumpers that aren't applicable to any specific show) titled "Neutral - ".

Additionally, the schedule naming applied to Nick at Nite blocks is the same here (although this is optional). 
# 4. Boomerang
For Boomerang, you'll need a few specifically named bumps. Boomerang typically had fades to commercial that were unique to the show playing. They also made a few neutral bumps for shows that did not have unique bumpers.

You should either have a few bumps in your folder for each show that cover "[SHOW NAME] Fade In", "[SHOW NAME] Fade Out", "[SHOW NAME] Interstitial", "[SHOW NAME] Intro", and "[SHOW NAME] Outro". Alternatively, you can just have some bumps that replace [SHOW NAME] in each of the previously listed filenames with "Neutral". The script will detect and use these in instances where a specific show bumpers cannot be found. If neither exists, the script will likely crash.

You will also need files called "Up Next - Boomerang.mp4" and "Neutral End.mp4" in your Boomerang bumps folder.
# 5. Adult Swim
This is the hardest one because of the various unique bumps used by Adult Swim. You need a few things here:
1. A file named "Adult Swim Advisory.mp4" with correct path specified in the def Adult_Swim() function in _functions.py. This can safely be commented out if you don't want the AS advisory on startup.
2. A file named "Pool - Intro.mp4" in the same folder. This can also be commented out if you don't want an intro.
3. Bumps in your bump folder that have "General - " in their filename for the standard black & white titlecard Adult Swim bumps.
4. Bumps in your bump folder that have "Bump - " in their filename for picture bumps typically played on Adult Swim.
