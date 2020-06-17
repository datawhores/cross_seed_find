
#! /usr/bin/env python3

"""NOTE: READ DOCUMENTATION BEFORE USAGE.
Usage:
    cross.py (-h | --help)
    cross.py scan --txt=<txtlocation> --type <type> --root <root_folders_to_scan>...
    [--delete ][--ignored <sub_folders_to_ignore> --exclude <source_excluded>]...
    cross.py grab --txt=<txtlocation> --torrent <torrents_download>  --api <apikey> --site <jackett_sitename>
    [--date <int> --filter <reduce_query> --url <jacketturl_port> --fd <binary_fd>]
    cross.py dedupe --txt=<txtlocation>



Options:
  -h --help     Show this screen.
  scan scan the root folder(s) create a list of files to download. 'txt file creator'

  --type ; -t <movie(m or tv(t)>  Controls how the folder is scanned. TV files have an extra directory for Seasons
  --root ; -r <root_folders_to_scan> subfolders in this root folder will be scanned
  --delete; -d  Will delete the old txt file(optional)
  --exclude ; -e <source_excluded>  This file type will not be scanned blu,tv,remux,other,web.(optional)  [default: [None]]
  --ignored ; -i <sub_folders_to_ignore>  If this folder is a part of  a root folder it will be ignore, subfolders can still be scan if you add it as a root (optional) [default: [None]]
  --fd <binary_fd> fd is a program to scan for files, use this if you don't have fd in path,(optional)   [default: fd]



  grab downloads torrents using txt file
  --site <jackett_sitename>  This is the site name from Jackett
  --torrent <torrents_download>  Here are where the torrent files will download
  --date <int> only download torrents newer then this input should be int, and represents days. By default it is set to around 25 years(optional)  [default: 10000 ]
  --api <apikey> This is the apikey from jackett
  --filter ; -f <reduce_query> Some sites don't allow for much filtering in searches: [1:Video + Season(TV) + resolution + source][2:Video + Season(TV) + source]
  [3:Video + Season(TV) + resolution][4:Video + Season(TV)][5:Video]
  Note:Season only matters for TV(optional)  [default: 2]

  --url <jacketturl_port> This is the url used to access jackett main page(optional)  [default: http://127.0.0.1:9117/]


  dedupe
  Just a basic script to remove duplicate entries from the list. scan will automatically run this after it finishes

  --txt <txtlocation>  txt file with all the file names(required for all commands)
  """
import requests
import subprocess
from pathlib import Path
import json
import os
import glob
from guessit import guessit
import untangle
from xml.etree import ElementTree as ET
from datetime import date,timedelta, datetime
from docopt import docopt
import tempfile

def duperemove():
    moviefiles=open(file,"r")
    lines_seen = set() # holds lines already seen
    for line in moviefiles:
        if line not in lines_seen: # not a duplicate
            lines_seen.add(line)
    moviefiles.close()
    outfile = open(file, "w")
    for line in lines_seen:
        outfile.write(line)
    outfile.close()

def skip(list,filename):
    if filename in list:
        return None
    else:
        return 1

def convertlower(dict):
    try:
        dict['source']=dict['source'].lower()
    except Exception as e:
        pass

    try:
        dict['other']=dict['other'].lower()
    except Exception as e:
        pass
    try:
        dict['title']=dict['title'].lower()
    except Exception as e:
        pass
    try:
        dict['release_group']=dict['release_group'].lower()
    except Exception as e:
        pass
    return dict











def findmatches(arguments,max):
    final=""
    files=open(file,"a+")
    fd=arguments['--fd']




    if source['remux']=='yes':
        #1080
        remux1=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'remux','--exclude','*2160*',
        '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
        #2160
        remux2=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'remux','--exclude','*1080*',
        '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
        #720
        remux3=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'remux','--exclude','*1080*',
        '--exclude','*2160*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
        remux=remux1+remux2+remux3
        remux=remux.decode('utf-8')
        final=final+remux
    if source['web']=='yes':
            #1080
            web1=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
            #2160
            web2=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
            #720
            web3=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*2160*',
            '--exclude','*1080*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','[tT][rR][aA][iL][eE][rR]*'])
            #480
            web4=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.webr|.web-r)','--exclude','*2160*',
            '--exclude','*720*','--exclude','*1080*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'(.web-dl|.webdl)','--exclude','*2160*',
            '--exclude','*720*','--exclude','*1080*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])+subprocess.check_output([fd,'--glob','-e','.mkv','-e','.mp4','-e','.m4v',max,'*.[wW][eE][bB].*','--exclude','*2160*',
            '--exclude','*720*','--exclude','*1080*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])

            web=web1+web2+web3+web4
            web=web.decode('utf-8')
            final=final+web
    if source['blu']=='yes':
            #1080
            blu1=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'.blu','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])
            #2160
            blu2=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'.blu','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])
            #720
            blu3=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'.blu','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
        '*[tT][rR][aA][iL][eE][rR]*'])
            blu=blu1+blu2+blu3
            blu=blu.decode('utf-8')
            final=final+blu

    if source['tv']=='yes':
            #1080
            tv1=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*2160*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
            #2160
            tv2=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*1080*',
            '--exclude','*720*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
            #720
            tv3=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*480*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
            #480
            tv4=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'hdtv','--exclude','*1080*',
            '--exclude','*2160*','--exclude','*720*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude','*[tT][rR][aA][iL][eE][rR]*'])
            tv=tv1+tv2+tv3+tv4
            tv=tv.decode('utf-8')
            final=final+tv
    #finding Others
    #1080
    if source['other']=='yes':
        other1=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*2160*',
        '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
    '*[tT][rR][aA][iL][eE][rR]*'])
    #2160
        other2=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*1080*',
        '--exclude','*720*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
    '*[tT][rR][aA][iL][eE][rR]*'])
    #720
        other3=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*1080*',
        '--exclude','*2160*','--exclude','*480*','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
    '*[tT][rR][aA][iL][eE][rR]*'])
    #480
        other4=subprocess.check_output([fd,'-e','.mkv','-e','.mp4','-e','.m4v',max,'tv','--exclude','*1080*',
        '--exclude','*2160*','--exclude','*720*','--exclude','480','--exclude','*[rR][eE][mM][uU][xX]*','--exclude','*.[wW][eE][bB]*','--exclude','*.[bB][lL][uU]*','--exclude','*[tT][vV]*','--exclude','*[sS][aA][mM][pP][lL][eE]*','--exclude',
    '*[tT][rR][aA][iL][eE][rR]*'])
        others=other1+other2+other3+other4
        others=others.decode('utf-8')
        final=final+others





    if final!="":
        print("adding to txt file:" + '\n'+final)
        files.write(final)
    files.close()

def searchtv(arguments):
  open(file, 'w').close()
  max="--max-results=1"
  roots=arguments['--root']
  ignorelist=arguments['--ignored']
  print("Searching")
  seasonlist=[]
  for root in roots:

    for show in os.scandir(root):
        if skip(ignorelist,show.path)==None:
            continue
        if show.is_dir():
            print("Scanning for season folders in:",show)
            for season in os.scandir(show):
                if season.is_dir():
                    seasonlist.append(season.path)


    for season in seasonlist:
        os.chdir(season)
        findmatches(arguments,max)

    duperemove()


def searchmovies(arguments):
    max="--max-results=200"
    roots=arguments['--root']
    ignorelist=arguments['--ignored']
    print("Searching for all Movies")
    for root in roots:
        for movie in os.scandir(root):
            print("Scanning for Movie Folder:",movie, "added")
            if skip(ignorelist,movie.path)==None:
                continue
            if movie.is_dir():
                os.chdir(movie)
                findmatches(arguments,max)
    duperemove()
def download(arguments):
    files= open(file,"r")
    folder=arguments['--torrent']
    days=int(arguments['--date'])
    site=arguments['--site']
    apikey=arguments['--api']
    filter=arguments['--filter']
    for line in files:
        print("Searching for match:"+line)
        show=guessit(line)
        show=convertlower(show)
        name=show.get('title',"")
        season_num=show.get('season')
        if type(season_num) is list or season_num==None:
            season=""
        elif(season_num<10):
            season="S" + "0" + str(season_num)
        else:
            season="S" + str(season_num)
        source=show.get('source',"")
        remux=show.get('other',"")
        if remux=="remux" or source=="hd-dvd":
            source=remux
        resolution=show.get('screen_size',"")
        encode=show.get('video_codec',"")
        release=show.get('release_group',"")

        xml=tempfile.NamedTemporaryFile(mode = 'w+').name
        jackett=arguments['--url'] +"jackett/api/v2.0/indexers/"
        url=jackett+ site +"/results/torznab/api?apikey=" + apikey + "&t=search&extended=1&q=" + \
        {"1":name + ' ' + season + ' '  + source  + ' ' + resolution, \
        "2":name + ' ' +season + ' ' +source, \
        "3":name + ' ' +season + ' ' +resolution, \
        "4":name + ' ' +season, \
        "5":name}.get(filter)
        url=url.replace(" ", "+")
        print(url)

        textsearch=requests.get(url=url)
        tree = ET.fromstring(textsearch.content)
        tree = ET.ElementTree(tree)
        tree.write(xml)
        tree = ET.parse(xml)
        try:
            obj = untangle.parse(xml)
            obj.rss.channel.item
        except:
            print("No hits")
            continue

        for element in obj.rss.channel.item:
            matchtitle=element.title.cdata.strip()
            comment=element.comments.cdata.strip() +  '\n'
            torrent=("["+site+"]"+ matchtitle +".torrent").replace("/", "_")
            link=element.link.cdata.strip()
            filedate= element.pubDate.cdata.strip()
            filedate=datetime.strptime(filedate, '%a, %d %b %Y %H:%M:%S %z').date()
            matchtitle=guessit(matchtitle)
            matchtitle=convertlower(matchtitle)

            matchsource=matchtitle.get('source',"")
            matchremux=matchtitle.get('other',"")
            matchseason=matchtitle.get('season')
            matchresolution=matchtitle.get('screen_size',"")
            matchencode=matchtitle.get('video_codec',"")
            matchname=matchtitle.get('title',"")
            matchrelease=matchtitle.get('release_group',"")
            daterestrict=(date.today()-timedelta(days))

            if matchremux=="remux" or matchsource=="hd-dvd":
                matchsource=matchremux

            if(matchsource!=source):
                continue

            if(matchname!=name):
                continue

            if(matchrelease!=release):
                continue

            if(matchresolution!=resolution):
                continue

            if(matchseason!=season_num):
                continue

            if(matchrelease!=release):
                continue
            if(daterestrict > filedate):
                continue
            else:
                torrentfile=(folder+torrent)
                print(torrentfile)


                fp = open(torrentfile, "wb")
                try:
                    subprocess.check_output(['wget',link,'-O',torrentfile])
                except:
                    print("web error")
                break
if __name__ == '__main__':

    arguments = docopt(__doc__, version='CLI AHD Uploader 1.2')
    file=arguments['--txt']
    if arguments['scan']:
        type=arguments['--type']
        source={'remux':'yes','web':'yes','blu':'yes','tv':'yes','other':'yes'}
        exclude=arguments['--exclude']
        if arguments['--delete']:
            open(file, 'w').close()




        for element in exclude:
            try:
                source[element]="No"
            except KeyError:
                pass

        if type=="movie" or type=="m":
            searchmovies(arguments)
        elif type=="tv" or type=="t":
            searchtv(arguments)
        else:
            print("invalid type")
    elif arguments['dedupe']:
        duperemove()
    elif arguments['grab']:
        download(arguments)
