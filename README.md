**Requirements:**

Python 3

Modules
- requests
- guessit
- docopt
- xmltodict

https://github.com/sharkdp/fd/releases - Note: Instructions say you need root to install the binary. But you don't need root to run it so I've included a version of it in the repo


**How to use**

commandline options can be loaded with --config or -x config. If using a config file and commandline, the latter option overwrites what is in the config

scanning:cross.py scan --txt=txtlocation --mvr folder(s) and or --tvr folder(s)
note: you need to put a mvt or tvr for each different folder 

    Adds the names of files to a txt file.
    
    --mvr this is the folder whoses subfolders will be scanned: This is a radarr type folder which ends in the (****)
    --tvr this is the folder whoses subfolders will be scanned: This is a sonarr type folder which ends in the "Season **"
    --fd fd is a program for finding files if you can't install to system path you can put the location of the binary using this option. Note: a binary is included in this repo
    --txt this is where the txt file will be saved
    
    optional
    --delete ; -d This will delete the txt file otherwise the file is just appeneded
    --exclude ; -e Exclude certain types of videos from being added to txt file blu=encode,remux=remux,web=web-dl or web-rip orweb,tv=hdtv,other=badly named files
    --ignored ; -i this folder will be ignored completly, appends to .fdignore, so this should only need to be done once. 
    
Downloading:cross.py grab --txt=(txtlocation) --torrent (torrents_download)  --api (apikey) --site (jackett_sitename)
    
    In short you should have a list of the directories from radarr where the movies are stored. So that the movie files are in that folder, and not any subfolder of that folder. 
    Along with the folder where the season files for a tv show are held. i.e season 01.. season 02 etc.
    
    
    pick either --torrent or --output option
    --torrent ; -t this is where matching files will be saved
    --output ; -o
    
    
    --txt scanned and each line is sent to jackett
    --api ; -a  your jackett api key
    --site ; -s  sitename from jackett
    
    optional
    --date  restrict downloads only newer then this amount of days, should be an int
    --size ; -z  set whether a search should be done by name only or include file size restriction. If true then an additonal check will be added to see if all the matching
    "1080p Remux Files,2160 Remux Files" in a directory match the size of the jackett response
    
    --filter 
    [1:Video + Season(TV) + resolution + source][2:Video + Season(TV) + source]
    [3:Video + Season(TV) + resolution][4:Video + Season(TV)][5:Video]
    Unfortuntly restricting the amount of results per search is not always possible for every site. For example UHDbits only seems to work with option 5. To get around this
    Here you can change the type of searches done. Default is option 2
    Note: For options with season it is only added to url if seasons is part of filename
    --exclude ; -e For any directory this type of file will not be checked for possible cross seeds
    
    --url this is the url used to access jacketts main page default is http://127.0.0.1:9117
    note: you should only need to change the port if needed as 127.0.0.1 is for localhost and would only be acceple if your accessing it from the server. 
    Or connecting to your server via a vpn or proxy
    
    --fd fd is a program for finding files if you can't install to system path you can put the location of the binary using this option. Note: a binary is included in this repo
    
dedupe:
    runs every time you scan a folder, after the scan has finished.
    Can be ran seperately if for example you exit out a scan or it crashes
    
     --txt file to dedupe
   
    
    
    
    
    
    
 
    
    
    
    

