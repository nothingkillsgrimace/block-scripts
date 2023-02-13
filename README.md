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
Currently this only supports:
	- Adult Swim
	- Nick at Nite
	- FOX

Calling a block keyword also requires some additional steps. This mainly involves
specifying the paths to your 'commercials' and 'bumps' folders within the
'clips' heading in the dictionary corresponding to the keyword name.

It's good practice to separate all your clips into individual folders based on 
channel and type. 
