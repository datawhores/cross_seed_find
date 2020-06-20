
#! /usr/bin/env python3
"""NOTE: READ DOCUMENTATION BEFORE USAGE.
Usage:
    cross.py (-h | --help)
    cross.py scan --txt=<txtlocation>
    [--delete][--fd <binary_fd>][--ignore <sub_folders_to_ignore> --mvr <movie_root(s)> --tvr <tv_root(s)>]...
    cross.py grab --txt=<txtlocation> (--torrent <torrents_download>|--output <output>)   --api <apikey> --site <jackett_sitename>
    [--date <int> --filter <reduce_query> --url <jacketturl_port> --fd <binary_fd> --size <t_or_f> ]
    [--exclude <source_excluded>]...
    cross.py dedupe --txt=<txtlocation>



Options:
  -h --help     Show this screen.
  scan scan tv or movie folders root folder(s) create a list of directories. 'txt file creator'

  roots

--tvr <tv_root(s)> These are sonnarr type folders with the files with in a "season **" type folders
--mvr <movie_root(s)> These are radarr type folders with the files in a file that ends in the year

--delete; -d  Will delete the old txt file(optional)
--ignore ; -i <sub_folders_to_ignore>  folder will be ignored for scan (optional) [default: ""]

 grab downloads torrents using txt file
 pick 1 of the following torrent or output:
 --torrent ; -t <torrents_download>  Here are where the torrent files will download  [default: None]
 --output ; -o <output>  Here are where the torrentlinks will be weritte  [default: None]

  --site ; -s <jackett_sitename>  This is the site name from Jackett
  --date ; -r <int> only download torrents newer then this input should be int, and represents days. By default it is set to around 25 years(optional)  [default: 10000 ]
  --api ; -a <apikey> This is the apikey from jackett
  --filter ; -f <reduce_query> Some sites don't allow for much filtering in searches: [1:Video + Season(TV) + resolution + source][2:Video + Season(TV) + source]
  --exclude ; -e <source_excluded>  This file type will not be scanned blu,tv,remux,other,web.(optional)  [default: []]
  [3:Video + Season(TV) + resolution][4:Video + Season(TV)][5:Video]
  Note:Season only matters for TV(optional)  [default: 2]

  --url ; -u <jacketturl_port> This is the url used to access jackett main page(optional)  [default: http://127.0.0.1:9117/]
  --size ; -z <t_or_f> set whether a search should be done by name only or include file size restriction. If true then an additonal check will be added to see if all the matching
  "1080p Remux Files,2160 Remux Files" in a directory match the size of the jackett response(optional)   [default: t]


  dedupe
  Just a basic script to remove duplicate entries from the list. scan will automatically run this after it finishes

  --txt <txtlocation>  txt file with all the file names(required for all commands)
  --fd <binary_fd> fd is a program to scan for files, use this if you don't have fd in path,(optional)   [default: fd]
  """
import requests
import subprocess
from pathlib import Path
import os
from guessit import guessit
from datetime import date,timedelta, datetime
from docopt import docopt
import tempfile
import urllib.parse
import xmltodict


class guessitinfo():
    """
    A class for guessit parse on a file
    """
    def __init__(self,file):
        self.info=guessit(file)
        self.name=""
        self.resolution=""
        self.encode=""
        self.source=""
        self.group=""
        self.season_num=""
        self.season=""
    def set_values(self):
        self.set_name()
        self.set_resolution()
        self.set_season_num()
        self.set_season()
        self.set_group()
        self.set_source()
        self.set_encode()

    def get_info(self):
        return self.info

    def set_name(self):
        self.name=self.get_info().get('title',"")
        try:
            self.name=self.name.lower()
        except:
            pass
    def set_resolution(self):
        self.resolution=self.get_info().get('screen_size',"")
    def set_encode(self):
        self.encode=self.get_info().get('video_codec',"")
    def set_source(self):
        self.source=self.get_info().get('source',"")
        remux=self.get_info().get('other',"")
        try:
            self.source=self.source.lower()
        except:
            pass

        try:
            remux=remux.source.lower()
        except:
            pass
        if remux=="remux" or self.source=="hd-dvd":
                self.source=remux
    def set_group(self):
        self.group=self.get_info().get('release_group',"")
        try:
            self.group=self.group.lower()
        except:
            pass
    def set_season_num(self):
        self.season_num=self.get_info().get('season',"")
    def set_season(self):
        season_num=self.get_season_num()
        if type(season_num) is list or season_num=="":
            self.season=""
        elif(season_num<10):
            self.season="S" + "0" + str(season_num)
        else:
            self.season="S" + str(season_num)
    def get_season_num(self):
        return self.season_num
    def get_season(self):
        return self.season
    def get_group(self):
        return self.group
    def get_resolution(self):
        return self.resolution
    def get_name(self):
        return self.name
    def get_encode(self):
        return self.encode
    def get_source(self):
        return self.source


class Folder:
    """
    Finds for example the 2160p Remux Files in a folder. Holds information about those files.
    """

    def __init__(self,dir,type,max,arguments):
        self.size=0
        self.type=type
        self.files=""
        self.dir=dir.strip()
        self.max=max
        self.arguments=arguments
    def get_dir(self):
        return self.dir
    def get_type(self):
        return  self.type
    def get_files(self):
        return  self.files
    def get_size(self):
        return  self.size
    def get_max(self):
        return self.max
    def get_arg(self):
        return  self.arguments
    def set_size(self):
        temp=0
        self.get_files().seek(0, 0)
        if len(self.get_files().readlines())<2:
            return
        self.get_files().seek(0, 0)
        for line in self.get_files().readlines():
            path=self.get_dir()+'/'+line.rstrip()
            temp=temp+os.path.getsize(path)
        self.size=temp
    def set_files(self,files):
        fd=arguments['--fd']
        max=self.get_max()
        dir=self.get_dir().rstrip()
        os.chdir(dir)
        if self.get_type()=="remux2160":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'remux','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="remux1080":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'remux','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="remux720":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'remux','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="blu2160":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'.blu','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="blu1080":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'.blu','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="blu720":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'.blu','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')

        elif self.get_type()=="webr2160":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webr1080":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webr720":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webr480":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*720*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webdl2160":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webdl1080":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webdl720":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="webdl480":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*720*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="web2160":
            temp=subprocess.check_output([fd,'-d','1','--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="web1080":
            temp=subprocess.check_output([fd,'-d','1','--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="web720":
            temp=subprocess.check_output([fd,'-d','1','--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="web480":
            temp=subprocess.check_output([fd,'-d','1','--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*720*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')




        elif self.get_type()=="tv2160":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="tv1080":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="tv720":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="tv480":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*720*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')

        elif self.get_type()=="other2160":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
            '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="other1080":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
            '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="other720":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
            '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        elif self.get_type()=="other480":
            temp=subprocess.check_output([fd,'-d','1','-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*720*','--exclude','480','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
            '*[tT][rR][aA][iL][eE][rR]*']).decode('utf-8')
        files.write(temp.rstrip())
        self.files=files

    def get_first(self):
        self.get_files().seek(0, 0)
        files=self.get_files()
        try:
            first=files.readlines()[0]
            return first
        except:
            return "No Files"
def duperemove(txt):
    input=open(txt,"r")
    lines_seen = set() # holds lines already seen
    for line in input:
        if line not in lines_seen: # not a duplicate
            lines_seen.add(line)
    input.close()
    outfile = open(txt, "w")
    for line in lines_seen:
        outfile.write(line)
    outfile.close()

def get_url(arguments,guessitinfo):
    jackett=arguments['--url'] +"jackett/api/v2.0/indexers/"
    site=arguments['--site']
    apikey=arguments['--api']
    filter=arguments['--filter']
    name=guessitinfo.get_name()
    season=guessitinfo.get_season()
    source=guessitinfo.get_source()
    resolution=guessitinfo.get_resolution()
    url=jackett+ site +"/results/torznab/api?apikey=" + apikey + "&t=search&extended=1&q=" + \
        {"1":name + ' ' + season + ' '  + source  + ' ' + resolution, \
        "2":name + ' ' +season + ' ' +source, \
        "3":name + ' ' +season + ' ' +resolution, \
        "4":name + ' ' +season, \
        "5":name}.get(filter)
    url=url.replace(" ", "+")
    return url


def findmatches(arguments,files):
    torrentfolder=arguments['--torrent']
    site=arguments['--site']
    datefilter=(date.today()- timedelta(int(arguments['--date'])))
    file=files.get_first()
    if file=="No Files":
        return
    size=files.get_size()
    fileguessit=guessitinfo(file)
    fileguessit.set_values()
    search=get_url(arguments,fileguessit)
    print("Searching with:",search)
    try:
        response = requests.get(search)
    except:
        print("Issue getting response:",search)
        return
    results=xmltodict.parse(response.content)
    try:
        results['rss']['channel']['item']
    except:
        print("no results")
        return
    for element in results['rss']['channel']['item']:
        matchtitle=element['title']
        matchdate=datetime.strptime(element['pubDate'], '%a, %d %b %Y %H:%M:%S %z').date()
        matchsize=int(element['size'])
        matchguessit=guessitinfo(matchtitle)
        matchguessit.set_values()
        link=element['link']
        print("item:",size,"matching:",matchsize)
        if matchguessit.get_name()!=fileguessit.get_name():
            continue
        if matchguessit.get_source()!=fileguessit.get_source():
            continue
        if matchguessit.get_group()!=fileguessit.get_group():
            continue
        if matchguessit.get_resolution()!=fileguessit.get_resolution():
            continue
        if matchguessit.get_season_num()!=fileguessit.get_season_num():
            continue
        if datefilter > matchdate:
            continue
        if difference(matchsize,size)>.01 and size!=0:
            continue
        if torrentfolder=="None":
            t=open(arguments['--output'],'a')
            print("writing to file:",arguments['--output'])
            t.write(link+'\n')
            break
        torrent=torrentfolder + ("["+site+"]"+ matchtitle +".torrent").replace("/", "_")
        print(torrent)
        try:
            subprocess.run(['wget',link,'-O',torrent])
            break
        except:
            print("web error")
            break

def set_ignored(arguments,ignore):
    arg=arguments['--ignore']
    ignore=open(ignore,"a+")
    if arg==None:
        return
    for element in arg:
        ignore.write(element)
        ignore.write('\n')

def searchtv(arguments,ignorefile):
  if arguments['--tvr']==[]:
    return
  folders=open(arguments['--txt'],"a+")
  print("Adding TV Folders to txt")
  for root in arguments['--tvr']:
      if os.path.isdir(root)==False:
          print("is not valid directory")
          continue
      temp=subprocess.check_output([arguments['--fd'],'Season\s[0-9][0-9]$','-t','d','--full-path',root,'--ignore-file',ignorefile]).decode('utf-8')
      folders.write(temp)
      print(temp)
  print("Done")


def searchmovies(arguments,ignorefile):
    if arguments['--mvr']==[]:
        return
    folders=open(arguments['--txt'],"a+")
    print("Adding Movies Folders to txt")
    for root in arguments['--mvr']:
        if os.path.isdir(root)==False:
            print("is not valid directory")
            continue
        temp=subprocess.check_output([arguments['--fd'],'\)$','-t','d','--full-path',root,'--ignore-file',ignorefile]).decode('utf-8')
        folders.write(temp)
        print(temp)
    print("Done")

def set_max(arguments):

    if arguments['--size']=="t":
        max="--max-results=200"
    elif arguments['--size']=="f":
        max="--max-results=1"
    else:
        print(arguments['--size'],"is not a valid value for size")
        quit()
    return max
def difference(value1,value2):
    dif=(value2-value1)/((value1+value2)/2)
    return dif

def releasetype(arguments):
    source={'remux':'yes','web':'yes','blu':'yes','tv':'yes','other':'yes'}
    for element in arguments['--exclude']:
        try:
            source[element]="No"
        except KeyError:
            pass
    return source



def download(arguments,txt):
    max=set_max(arguments)
    folders=open(txt,"r")
    source=releasetype(arguments)

    for line in folders:
        print(line)
        if line=='\n':
            continue
        if source['remux']=='yes':
            files=tempfile.NamedTemporaryFile('w+')
            remux1=Folder(line,"remux1080",max,arguments)
            remux1.set_files(files)
            remux1.set_size()
            findmatches(arguments,remux1)
            #files.close()

            files=tempfile.NamedTemporaryFile('w+')
            remux2=Folder(line,"remux2160",max,arguments)
            remux2.set_files(files)
            remux2.set_size()
            findmatches(arguments,remux2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            remux3=Folder(line,"remux720",max,arguments)
            remux3.set_files(files)
            remux3.set_size()
            findmatches(arguments,remux3)
            files.close()
        if source['blu']=='yes':
            files=tempfile.NamedTemporaryFile('w+')
            blu1=Folder(line,"blu1080",max,arguments)
            blu1.set_files(files)
            blu1.set_size()
            findmatches(arguments,blu1)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            blu2=Folder(line,"blu2160",max,arguments)
            blu2.set_files(files)
            blu2.set_size()
            findmatches(arguments,blu2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            blu3=Folder(line,"blu720",max,arguments)
            blu3.set_files(files)
            blu3.set_size()
            findmatches(arguments,blu3)
            files.close()
        if source['tv']=='yes':
            files=tempfile.NamedTemporaryFile('w+')
            tv1=Folder(line,"tv1080",max,arguments)
            tv1.set_files(files)
            tv1.set_size()
            findmatches(arguments,tv1)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            tv2=Folder(line,"tv2160",max,arguments)
            tv2.set_files(files)
            tv2.set_size()
            findmatches(arguments,tv2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            tv3=Folder(line,"tv720",max,arguments)
            tv3.set_files(files)
            tv3.set_size()
            findmatches(arguments,tv3)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            tv4=Folder(line,"tv480",max,arguments)
            tv4.set_files(files)
            tv4.set_size()
            findmatches(arguments,tv4)
            files.close()
        if source['other']=='yes':
            files=tempfile.NamedTemporaryFile('w+')
            other1=Folder(line,"other1080",max,arguments)
            other1.set_files(files)
            other1.set_size()
            findmatches(arguments,other1)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            other2=Folder(line,"other2160",max,arguments)
            other2.set_files(files)
            other2.set_size()
            findmatches(arguments,other2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            other3=Folder(line,"other720",max,arguments)
            other3.set_files(files)
            other3.set_size()
            findmatches(arguments,other3)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            other4=Folder(line,"other480",max,arguments)
            other4.set_files(files)
            other4.set_size()
            findmatches(arguments,other4)
            files.close()
        if source['web']=='yes':
            files=tempfile.NamedTemporaryFile('w+')
            web1=Folder(line,"web1080",max,arguments)
            web1.set_files(files)
            web1.set_size()
            findmatches(arguments,web1)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            web2=Folder(line,"web2160",max,arguments)
            web2.set_files(files)
            web2.set_size()
            findmatches(arguments,web2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            web3=Folder(line,"web720",max,arguments)
            web3.set_files(files)
            web3.set_size()
            findmatches(arguments,web3)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            web4=Folder(line,"web480",max,arguments)
            web4.set_files(files)
            web4.set_size()
            findmatches(arguments,web4)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webr1=Folder(line,"webr1080",max,arguments)
            webr1.set_files(files)
            webr1.set_size()
            findmatches(arguments,webr1)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webr2=Folder(line,"webr2160",max,arguments)
            webr2.set_files(files)
            webr2.set_size()
            findmatches(arguments,webr2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webr3=Folder(line,"webr720",max,arguments)
            webr3.set_files(files)
            webr3.set_size()
            findmatches(arguments,webr3)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webr4=Folder(line,"webr480",max,arguments)
            webr4.set_files(files)
            webr4.set_size()
            findmatches(arguments,webr4)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webdl1=Folder(line,"webdl1080",max,arguments)
            webdl1.set_files(files)
            webdl1.set_size()
            findmatches(arguments,webdl1)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webdl2=Folder(line,"webdl2160",max,arguments)
            webdl2.set_files(files)
            webdl2.set_size()
            findmatches(arguments,webdl2)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webdl3=Folder(line,"webdl720",max,arguments)
            webdl3.set_files(files)
            webdl3.set_size()
            findmatches(arguments,webdl3)
            files.close()

            files=tempfile.NamedTemporaryFile('w+')
            webdl4=Folder(line,"webdl480",max,arguments)
            webdl4.set_files(files)
            webdl4.set_size()
            findmatches(arguments,webdl4)
            files.close()


if __name__ == '__main__':
    #
    arguments = docopt(__doc__, version='cross_seed_scan 1.2')
    file=arguments['--txt']

    if arguments['scan']:
        print("Scanning for folders")
        if arguments['--delete']:
            open(file, 'w').close()
        ignorefile=os.environ['HOME'] + "/.fdignore"
        set_ignored(arguments,ignorefile)
        searchtv(arguments,ignorefile)
        searchmovies(arguments,ignorefile)
        duperemove(file)
    elif arguments['dedupe']:
        duperemove(arguments['--txt'])
    elif arguments['grab']:
        download(arguments,file)
