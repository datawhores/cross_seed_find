from datetime import date,timedelta, datetime
from classes import *
import requests
import xmltodict
import subprocess
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import checkboxlist_dialog
import os
import re
"""
General Functions
"""
def get_matches(site,errorfile,arguments,files):
    wget=arguments['--wget']
    torrentfolder=arguments['--torrent']
    datefilter=(date.today()- timedelta(int(arguments['--date'])))
    file=files.get_first()
    if file=="No Files":
        return
    filesize=files.get_size()
    fileguessit=guessitinfo(file)
    fileguessit.set_values()
    title=fileguessit.get_name().lower()
    search=get_url(arguments,site,fileguessit)
    print("Searching For",files.type,"with:",search)
    try:
        response = requests.get(search, timeout=300)
    except:
        errorpath=open(errorfile,"a+")
        errorstring=title +": Could not find Get a response from"+ site +": +search +"  +files.get_type() + " - " +datetime.now().strftime("%m.%d.%Y_%H%M") + "\n"
        errorpath.write(errorstring)
        errorpath.close()
        print("Issue getting response:",search)
        return
    try:
        results=xmltodict.parse(response.content)
    except:
        errorpath=open(errorfile,"a+")
        errorstring=title + ": Could not find parse"+ site + " response URL: "+search+" " +files.get_type() + " - " +datetime.now().strftime("%m.%d.%Y_%H%M") + "\n"
        errorpath.write(errorstring)
        errorpath.close()
        print("unable to parse xml")
        return
    try:
        results['rss']['channel']['item'][1]['title']
        loop=True
        max=len(results['rss']['channel']['item'])
    except KeyError as key:
        print(key)
        if str(key)=="1":
            element=results['rss']['channel']['item']
            max=1
            loop=False
        else:
            print("Probably no results")
            return
    for i in range(max):
        titlematch=False
        filedate=False
        group=False
        resolution=False
        source=False
        sizematch=False
        if loop: element = results['rss']['channel']['item'][i]
        querytitle=element['title']
        if querytitle==None:
            continue
        querydate=datetime.strptime(element['pubDate'], '%a, %d %b %Y %H:%M:%S %z').date()
        querysize=int(element['size'])
        queryguessit=guessitinfo(querytitle)
        queryguessit.set_values()
        if re.sub(":","",queryguessit.get_name())==re.sub(":","",fileguessit.get_name()):
            titlematch=True
        if queryguessit.get_source()==fileguessit.get_source():
            source=True
        if queryguessit.get_group()==fileguessit.get_group() or re.search(queryguessit.get_group(),fileguessit.get_group(),re.IGNORECASE)!=None \
        or re.search(fileguessit.get_group(),queryguessit.get_group(),re.IGNORECASE)!=None or arguments["--sites"]=="animebytes":
            group=True
        if queryguessit.get_resolution()==fileguessit.get_resolution():
            resolution=True
        if queryguessit.get_season_num()!=fileguessit.get_season_num():
            season=True
        if datefilter < querydate:
            filedate=True
        if difference(querysize,filesize)<.01:
            sizematch=True
        if (titlematch is True and source is True and group is True and resolution is True and filedate is True and (sizematch is True or filesize==0)):
            pass
        else:
            continue
        if arguments['--output']!=None and arguments['--output']!="" :
            t=open(arguments['--output'],'a')
            print("writing to file:",arguments['--output'])
            t.write(link+'\n')
        if arguments['--torrent']!=None and arguments['--torrent']!="" :
            torrentfile=(f"[{site}{querytitle}.torrent")
            torrentfile=re.sub("/",".",torrentfile)
            torrent=os.path.join(torrentfolder,torrentfile)
            print(torrent)
            link=element['link']
            try:
                subprocess.run(['wget',link,'-O',torrent])
            except:
                print("Error Downloading")
                errorpath=open(errorfile,"a+")
                errorstring=title + ": Could not find Download:"+ link  + " - " +datetime.now().strftime("%m.%d.%Y_%H%M") + "\n"
                errorpath.write(errorstring)
                errorpath.close()
def get_missing(site,errorfile,arguments,files,encode=None):
    if encode==None:
        encode==False
    output=arguments['--misstxt']
    datefilter=(date.today()- timedelta(int(arguments['--date'])))
    file=files.get_first()
    if file=="No Files":
        return
    filesize=files.get_size()
    fileguessit=guessitinfo(file)
    fileguessit.set_values()
    title=fileguessit.get_name().lower()
    search=get_url(arguments,site,fileguessit)
    print("Searching For",files.type,"with:",search)
    try:
        response = requests.get(search, timeout=300)
    except:
        errorpath=open(errorfile,"a+")
        errorstring=title +": Could not find Get a response from"+ site +": +search +"  +files.get_type() + " - " +datetime.now().strftime("%m.%d.%Y_%H%M") + "\n"
        errorpath.write(errorstring)
        errorpath.close()
        print("Issue getting response:",search)
        return
    try:
        results=xmltodict.parse(response.content)
    except:
        errorpath=open(errorfile,"a+")
        errorstring=title + ": Could not find parse"+ site + " response URL: "+search+" " +files.get_type() + " - " +datetime.now().strftime("%m.%d.%Y_%H%M") + "\n"
        errorpath.write(errorstring)
        errorpath.close()
        print("unable to parse xml")
        return
    try:
        results['rss']['channel']['item'][1]['title']
        loop=True
        max=len(results['rss']['channel']['item'])
    except KeyError as key:
        print(key)
        if str(key)=="1":
            element=results['rss']['channel']['item']
            max=1
            loop=False
        else:
            print("Probably no results")
            addmissing(output,site,files,file)
            return
    for i in range(max):
        titlematch=False
        filedate=False
        group=False
        resolution=False
        source=False
        sizematch=False
        if loop: element = results['rss']['channel']['item'][i]
        querytitle=element['title']
        if querytitle==None:
            continue
        querydate=datetime.strptime(element['pubDate'], '%a, %d %b %Y %H:%M:%S %z').date()
        querysize=int(element['size'])
        queryguessit=guessitinfo(querytitle)
        queryguessit.set_values()
        if re.sub(":","",queryguessit.get_name())==re.sub(":","",fileguessit.get_name()):
            titlematch=True
        if queryguessit.get_source()==fileguessit.get_source():
            source=True
        if queryguessit.get_group()==fileguessit.get_group() or re.search(queryguessit.get_group(),fileguessit.get_group(),re.IGNORECASE)!=None \
        or re.search(fileguessit.get_group(),queryguessit.get_group(),re.IGNORECASE)!=None or arguments["--sites"]=="animebytes":
            group=True
        if queryguessit.get_resolution()==fileguessit.get_resolution():
            resolution=True
        if queryguessit.get_season_num()!=fileguessit.get_season_num():
            season=True
        if datefilter < querydate:
            filedate=True
        if difference(querysize,filesize)<.01:
            sizematch=True
        if ((titlematch is True and source is True and group is True and resolution is True \
        and sizematch is True) and filesize!=0):
                return
        addmissing(output,site,files,file)





def addmissing(output,site,files,file):
    print("Adding Potential Upload to File")
    output=open(output,"a+")
    output.write(site)
    output.write(":")
    if files.get_dir()!=0:
        output.write(files.get_dir())
        output.write(":")
    output.write(file)
    output.write('\n')
    output.close()

def get_url(arguments,site,guessitinfo):
    jackett=arguments['--url'] +"jackett/api/v2.0/indexers/"
    apikey=arguments['--api']
    filter=arguments['--filter']
    name=guessitinfo.get_name()
    season=guessitinfo.get_season()
    if season!="":
        season=season+ ' '
    source=guessitinfo.get_source()
    resolution=guessitinfo.get_resolution()
    try:
        url=jackett+ site +"/results/torznab/api?apikey=" + apikey + "&t=search&extended=1&q=" + \
            {"1":name + ' ' + season + source  + ' ' + resolution, \
            "2":name + ' ' + season +  source, \
            "3":name + ' ' +season  +resolution, \
            "4":name + ' ' +season, \
            "5":name}.get(filter)
        url=url.replace(" ", "+")
    except:
        return
    return url
def difference(value1,value2):
    dif=abs((value2-value1)/((value1+value2)/2))
    return dif
def lower(input):
    if input==None:
        return input
    else:
        input=input.lower()
        return input
def createconfig(config):
    configpath=os.path.dirname(os.path.abspath(__file__))+"/cross.txt"
    config.read(configpath)


    if config.has_section('general') ==False:
        config.add_section('general')
    if config.has_section('grab') ==False:
        config.add_section('grab')
    if config.has_section('scan') ==False:
        config.add_section('scan')
    message_dialog(
        title="Config Creator",
        text="Welcome to the Config Creator.\nA config File is recommended to run this program\nWe will Start by adding root or Folders to Scan\nNote You'll need at least one root\nNote:This will overright cross.txt if you confirm at the end",
    ).run()

    newroot =True
    root=None
    rootstr=""
    ignorestr=""
    while newroot:
        if root==None:
            root = input_dialog(title='Getting Root Directories ',text='Please Enter the Path to a Root Directory:').run()
        if root==None:
            break
        addstring="Adding:"+root + " is this Okay? "
        option = button_dialog(
             title=addstring,
             buttons=[("Yes", True), ("No", False)],
        ).run()
        if option==False:
            root=None
            pass
        else:
            rootstr=rootstr+root+","
            root=None
        newroot= button_dialog(
                 title="Add Another Root Folder ",
                 buttons=[("Yes", True), ("No", False)],
        ).run()
    config.set('scan', "root", rootstr)

    confirm = button_dialog(
                 title="Add a Folder or File to ignore ",
                 buttons=[("Yes", True), ("No", False),("Info", None)],
    ).run()
    while confirm!=False:
        if confirm==None:
            message_dialog(
                    title="Ignore Folders and Files",
                    text="Ignored Directories will not be scanned As a subdirectory of another Root Folder.\nHowever note that a ignored Folder can still be added as a root .\nIn that case the subdirectories of the ignore folder would be added\nIgnored Files will not be added at all",
            ).run()
        if confirm:
            ignorepath = input_dialog(title='Getting ignore Path ',text='Please Enter the Path to ignore:').run()
        if ignorepath==None:
            break
        addstring="Adding:"+ignorepath + " is this Okay? "
        option = button_dialog(
             title=addstring,
             buttons=[("Yes", True), ("No", False)],
        ).run()
        if addstring==True:
             ignorestr= ignorestr+ignorepath
        confirm = button_dialog(
                     title="Add Another Folder to ignore ",
                     buttons=[("Yes", True), ("No", False)],
        ).run()

    config.set('scan', "ignore", ignorestr)
    newsite=True
    sitestr=""
    while newsite:
        site = input_dialog(title='Add a Site to search ',text="You'll have to get the name from jackett\nYou can get this by doing search with the desired site\nBy clicking the green search icon\n Name will appear on the addressbar next to tracker").run()
        if site==None:
            break
        addstring="Adding:"+site + " is this Okay? "
        option = button_dialog(
            title=addstring,
            buttons=[("Yes", True), ("No", False)],
        ).run()
        if option==False:
            root=None
            pass
        else:
            sitestr=sitestr+site+","
            site=None
        newsite = button_dialog(
             title="Add Another Site ",
             buttons=[("Yes", True), ("No", False)],
        ).run()
    config.set('grab', "sites", sitestr)

    confirm=False

    while confirm==False:
        filter= radiolist_dialog(
        values=[
            ("1", "Name + Season(TV) + Resolution + Source"),
            ("2", "Name + Season(TV) + Source"),
            ("3", "Name + Season(TV) + Resolution"),
            ("4", "Name + Season(TV)" ),
            ("5", "Name"),
        ],
        title="Filter",
        text="Pick the Source How you would like Searches to be done\nUnfortuntely some sites don't work with restrictive searching\nSo you should test this out yourself  \
        A search method that is not restrictive could slow down the searches with lots of results\nOr lead to false positives",
        ).run()
        if filter==None:
            break
        confirm= button_dialog(
            title="Is this okay",
            buttons=[("Yes", True), ("No", False)],
        ).run()
    config.set('grab', "filter", filter)

    #setup next few options as empty
    config.set('general', "txt", "")
    config.set('grab', "api", "")
    config.set('grab', "cookie", "")
    config.set('grab', "output", "")
    config.set('general', "misstxt", "")
    config.set('grab', "torrent", "")
    config.set('grab', "filter", "")


#filter and jacket url

    confirm=False
    while confirm==False:
        txtpath = input_dialog(title='Scanner TXT File',text='Please Enter the Path for scanner and grabber.\nFile Paths will Writen Here and is required ').run()
        if txtpath==None:
            break
        config.set('general', "txt", txtpath)
        confirmtxt="You entered:"+txtpath+" is this Okay?"
        confirm = button_dialog(
                 title=confirmtxt,
                 buttons=[("Yes", True), ("No", False)],
            ).run()
    confirm=False
    while confirm==False:
        torrent = input_dialog(title='Torrent Folder',text='Please Enter the Path for downloading Torrents\nIf you leave this blank make sure to set Output\nThat step will come up later in this setup\nIt is okay to setup Both Torrent and Output\nHowever if None are selected then Nothing will happen when Downloader finds a match').run()
        if torrent==None:
            break
        config.set('grab', "torrent", torrent)
        confirmtxt="You entered:"+torrent+" is this Okay?"
        confirm = button_dialog(
             title=confirmtxt,
             buttons=[("Yes", True), ("No", False)],
        ).run()



    confirm=False
    while confirm==False:
        key = input_dialog(title='Jackett Apikey',text='Please Enter your Jackett Apikey.\n   This will be used to Download Torrent Files and Scan Jackett\nThis is Required').run()
        if key==None:
            break
        config.set('grab', "api", key)
        confirmtxt="You entered:"+key+" is this Okay?"
        confirm = button_dialog(
                 title=confirmtxt,
                 buttons=[("Yes", True), ("No", False)],
            ).run()

    confirm= button_dialog(
        title="Do you want to Exclude Certain Sources\nFor example all blu-ray encodes,etc\nThese will be ignored during grabbing/matching\nNote: Other are Files that don't fit in other selectors\nPress Cancel to Leave Blank",
        buttons=[("Yes", True), ("No", False)],
    ).run()
    excludestr=""
    if confirm:
        exclude= checkboxlist_dialog(
        values=[
            ("remux", "Remux"),
            ("blu", "Blu-Ray Encode"),
            ("tv", "HDTV"),
            ("web", "WEB"),
            ("other", "Other"),
        ],
        title="Exclude",
        text="Pick the Source Types you would like to ignore ",
        ).run()

        for type in exclude:
            excludestr=excludestr+type+","
    config.set('grab', "exclude", excludestr)

    confirm=False
    while confirm==False:
        outpath = input_dialog(title='Download Links Output TXT',text='Please Enter a path for Writing Matched Links to.\nWith This Every Time a Match is found a download url will be written here\nPress Cancel to Leave Blank').run()
        if txtpath==None:
            break
        config.set('grab', "output", outpath)
        confirmtxt="You entered:"+outpath+" is this Okay?"
        confirm = button_dialog(
                 title=confirmtxt,
                 buttons=[("Yes", True), ("No", False)],
            ).run()

    confirm=False
    while confirm==False:
        missingpath = input_dialog(title='Missing Files Output TXT',text='Please Enter a path for Writing Potential Missing Files.\nDuring a "Missing Scan"  Every File is Compared to The Site Libary if the Slot is not already filled or your file is a encode.\nThe Path will be written to this TXT File\nThis is Required if you want to Find Files to upload').run()
        if txtpath==None:
            break
        config.set('general', "misstxt", missingpath)
        confirmtxt="You entered:"+outpath+" is this Okay?"
        confirm = button_dialog(
                 title=confirmtxt,
                 buttons=[("Yes", True), ("No", False)],
            ).run()






    fd=""
    config.set('general', "fd", fd)
    confirm=False
    while confirm==False:
        fd = input_dialog(title='FD' ,text='FD is required for Program\nDownloads Can be found here https://github.com/sharkdp/fd/releases\nBy Default the program comes with a version of fd for your OS\nIf you want to use your own binary, you can enter your choice here \nPress Cancel to use the Default  ').run()
        if txtpath==None:
            break
        config.set('general', "fd", fd)
        confirmtxt="You entered:"+fd+" is this Okay?"
        confirm = button_dialog(
                 title=confirmtxt,
                 buttons=[("Yes", True), ("No", False)],
            ).run()

    wget=""
    config.set('general', "wget", wget)
    confirm=False
    while confirm==False:
        wget = input_dialog(title='WGET' ,text='WGET is required for Program\nLinux comes with this Preinstalled usually for windows:https://eternallybored.org/misc/wget/\nBy Default the program comes with a version of wget for Windows\nIf you want to use your own binary, you can enter your choice here \nPress Cancel to use the Default  ').run()
        if txtpath==None:
            break
        config.set('general', "wget", wget)
        confirmtxt="You entered:"+wget+" is this Okay?"
        confirm = button_dialog(
                 title=confirmtxt,
                 buttons=[("Yes", True), ("No", False)],
            ).run()








    sections = config.sections()
    config_string=""
    for section in sections:
        options = config.options(section)
        for option in options:
              temp_dict={}
              temp_dict[option] = config.get(section,option)
              config_string=config_string+str(temp_dict)+"\n"






    txt="These are the Options that will be written to the configfile\nPlease Confirm if you want to save these Options\n Current File wil be overwritten\n\n"+config_string



    option = button_dialog(
             title="Confirm Options",
             text=txt,
             buttons=[("Yes", True), ("No", False)],
    ).run()
    if option==False:
        return
    with open(configpath, 'w') as configfile:
      print("Writing to configfile")
      config.write(configfile)
