#edit later

Requirements:

Python 3

Modules
- requests
- guessit
- untangle
- docopt

https://github.com/sharkdp/fd/releases

Note: Instructions say you need root to install the binary. But you don't need root to run it so I've included a version of it in the repo


How to use

scanning:cross.py scan --txt=<txtlocation> --type <type> --root <root_folders_to_scan>

    Adds the names of files to a txt file.
    type movie or m: This will go to root folder, then add every file within the subfolder, meant for radarr
    type tv or t:This will go to root folder, then go to the TV show folders, then 1 depth down the season folders.Since every release has 
    multiple files 1 file per release is added, meant for sonarr

