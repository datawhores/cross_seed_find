# Install
## Clone the repository
git clone https://github.com/excludedBittern8/cross_seed

cd cross_seed

## Creating a virtual enviroment
A Virtual environment is recommended. Please Make sure you are on python3 and NOT python 2

##### install virtualenv
On macOS and Linux:

python3 -m pip install --user virtualenv

On Windows:

py -m pip install --user virtualenv

##### create the virtualenv
On Linux:

python3 -m venv venv

On Windows:
python3 -m venv venv
or
py -m venv venv
##### Add required modules
On Linux:

./venv/bin/pip3 install -r requirements.txt

On Windows:

venv\Scripts\pip3.exe install -r requirements.txt

##### running python from venv
On Linux
/venv/bin/python3

on Windows
venv\Scripts\python
# Create Config
A config file is highly recommended. There are two easy ways to create one
1. run the program in interactive mode(please see below)
2. copy or rename example.config to cross.txt. It must be in the same folder. Fill it out with your values

# Quick Guide
Please start here for a general overview of how to run this program. 
## Scanning Directory

`cross.py scan [arguments]` 

scan a directory will write the paths to a txt document
    required
    --txt this is where the txt file will be saved
    --root at least one root is needed
    
    optional
    --delete ; -d This will delete the txt file otherwise the file is just appeneded
    --ignored ; -i this folder will be ignored completly, appends to .fdignore, so this should only need to be done once. 
    --fd fd program location
    

## Grabbing Downloads
`cross.py grab [arguments]` 

grab downloads using a list of the directories/files. Files can be generated manually or with this programs scanning function. If Scanning please note that 

    
    [Must pick at least 1]
    --torrent ; -t this is where matching files will be saved
    --output ; -o
    
    required
    --txt find files in folders, searches for possible cross seeds
    --api ; -a  your passkey key
    --sites ; -s A comma seperated list of jackett site-names
    --url ; u Jackett url default is localhost:9117. 

    optional
    --date  restrict downloads only newer then this amount of days, should be an int
    --exclude ; -e For any directory this type of file will not be checked for possible cross seeds
    --fd fd program location
    --wget wget program location


## Find Files to Upload to A Site
`cross.py missing [arguments]`

Will scan a directory and find any file that hasn't been uploaded to a tracker site. 
This is experiemental
    required
    --missingtxt write paths to this txt file
    --api ; -a  your passkey key
    --sites ; -s A comma seperated list of jackett site-names
    --url ; u Jackett url default is localhost:9117. 


    optional
    --exclude <source_excluded>... For any directory this type of file will not be checked for possible cross seeds
    --fd fd program location

## Interactive Mode
`cross.py [arguments]` or `cross.py interactive [arguments]` 

Start a gui version of the program






















# Arguments 
A more in-depth overview of some of the argument that can be passed to the program

## --fd
If you want to use your own fd file use this argument is is for convience and to make running the program easier
The reason you might want to do this is that this program will provide an version of fd.T his is for convience and to make running the program easier But it is not guaranted to be the newest/most optimized version. 

## Errors
Their are numerous reason for errors. Somes Python just can't get the size of a file if it is moutned. Other times jackett has network issues, and the api won't work. We try to skip over these errors and move onto the next file. If for some reason something happens. We have the errors file which is created when the program starts, and is updated until it ends.

## Courtesy
Running this everyday would be excessive especially on a large library. I would recommend using a scheduler. Linux has cron(not a big fan), jobber, cronicle. 
Windows has the task scheduler. With any you used be able to set the program to run every week

## Config vs arguments
Config is recommend to set a base. With that you only need to call -c [config file path]
However, any commandline option you pick will overide the config option


## scan
`cross.py scan [arguments]` 
You need to generate a list of files and Directories. The output is controled by either 
* --txt in the commandline or
* txt: in the config file

#### --ignore
Ignore is used by fd to find what directories to disregard.
Ignore folders will never be added as a directory during a scan. However sub-folders of a ignore folder be added if the ignore folder is chosen as root. 
If we chose a file to be ignored, then since we can't cd into a file that file will always be ignored. 


#### --root:
This  folder(s) will be scan much the same as the ls or dir command. So every file or directory will be added to the scanning list. As they appear in the directory chosen. 

Note: If you have a sonnar or raddar file please check these repos out [placeholder]

## grab
`cross.py grab [arguments]` 

You will need to provide a txt file of directories/folders. Either generated manually or with the scan command

#### Folder vs File
##### Folder
When the grabber sees a folder in the txt list. It will start a folder scan.
This should normally only apply to TV folders
A folder scan will scan every type of file i.e web-dl web-rip individually. The size calculated will be based on that type of file. This goes down to the resolution so 
* WEB-Dl 1080p
* WEB-DL 2160p 
will both be consider to be two different release. However if you had 
* Framestor 1080p Remux
* Epislon 1080p Remux in the same folder. 
That could lead to issues as now the sescond type of matching would not work. As the size match would be off

#### File
File scans are much the same as folder scan. If the information matches then the torrent is downloaded or output to file. However the check is based on the path on the txt file


## missing
`cross.py missing [arguments]` 
You have two ways to generate a output txt file for output. 
* --missingtxt in the commandline or
* missingtxt: in the config file

How it works is if for example we have a avengers remux, and the site has no avengers remux uploaded, then that will be written to the misstxt file.
Also if we have an encode that has not been upload. Even if an encode already exist your encode will be added to the list.
The result is that one will now have an easy to use list of potential files to upload





   
    
    
    
    
    
    
 
    
    
    
    


