

**Requirements:**

Python 3

Modules
- requests
- guessit
- untangle
- docopt

https://github.com/sharkdp/fd/releases

Note: Instructions say you need root to install the binary. But you don't need root to run it so I've included a version of it in the repo


**How to use**

scanning:cross.py scan --txt=<txtlocation> --type <type> --root <root_folders_to_scan>

    Adds the names of files to a txt file.
    
    --root this is the folder whoses subfolders will be scanned
    In the case that it is set as a root also the subfolders of ignored folder will be scanned.
    
    --type (movie or m) This will go to root folder, then add every file within the subfolder, meant for radarr
    --type (tv or t) This will go to root folder, then go to the TV show folders, then 1 depth down the season folders.Since every release has 
    multiple files 1 file per release is added, meant for sonarr
    
    --txt this is where the txt file will be saved
    
    
    
    optional
    --delete This will delete the txt file otherwise the file is just appeneded
    --exclude Exclude certain types of videos from being added to txt file blu=encode,remux=remux,web=web-dl or web-rip orweb,tv=hdtv,other=badly named files
    --ignored If this folder is a **subfolder of a root** it will be ignored. For now the path should be /home/folder and not /home/folder/ as the latter will not work
    
Downloading:cross.py grab --txt=<txtlocation> --torrent <torrents_download>  --api <apikey> --site <jackett_sitename>
    
    Searches files on jackett using a txt file. txt file should have acceptable scene names/tracker names i.e "Better.Call.Saul.S04E01.Smoke.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-EPSiLON.mkv"
    Otherwise it will probably just end up downloading the first hit for any search. Files are label with the sitename from jackett and put into the torrent folder
    For each search if a match is found no other results are checked
    
    --txt scanned and each line is sent to jackett
    --torrent this is where matching files will be saved
    --api your jackett api key
    --site sitename from jackett
    
    optional
    --date  restrict downloads only newer then this amount of days, should be an int
    --filter 
    [1:Video + Season(TV) + resolution + source][2:Video + Season(TV) + source]
    [3:Video + Season(TV) + resolution][4:Video + Season(TV)][5:Video]
    Unfortuntly restricting the amount of results per search is not always possible for every site. For example UHDbits only seems to work with option 5. To get around this
    Here you can change the type of searches done. Default is option 2
    Note: For options with season it is only added to url if seasons is part of filename
    
    --url this is the url used to access jacketts main page default is http://127.0.0.1:9117
    note: you should only need to change the port if needed as 127.0.0.1 is for localhost and would only be acceple if your accessing it from the server. 
    Or connecting to your server via a vpn or proxy
    
    --fd fd is a program for finding files if you can't install to system path you can put the location of the binary using this option. Note: a binary is included in this repo
    
dedupe:
    runs every time you scan a folder, after the scan has finished.
    Can be ran seperately if for example you exit out a scan or it crashes
    
     --txt file to dedupe
   
    
    
    
    
    
    
 
    
    
    
    

