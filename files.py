import re
from guessit import guessit
import os
from general import *
class File:
    """
    Holds information about a file.
    """
    def __init__(self,file,arguments,source):
        pass
        self.size=0
        self.source=source
        self.arguments=arguments
        self.name=file.rstrip("\n")
        self.dir="0"
        self.date=datetime.now().strftime("%m.%d.%Y")
        self.valid=None
        self.encode=None
        self.type=None

    def get_dir(self):
        return self.dir

    def get_name(self):
        return self.name
    def get_first(self):
        return self.name
    def get_size(self):
        return  self.size
    def get_type(self):
        return  self.type
    def get_arg(self):
        return  self.arguments
    def get_valid(self):
        return  self.valid
    def get_encode(self):
        return  self.encode
    def set_size(self):
        self.size=os.path.getsize(self.get_name())
    def set_valid(self):
        if re.search("[rR][eE][mM][uU][xX]",self.name)!=None and self.source['remux']=='yes':
            self.valid=True
        elif re.search("[rR][eE][mM][uU][xX]",self.name)==None and re.search("[bB][lL][uU]",self.name)!=None and self.source['blu']=='yes':
            self.valid=True
        elif re.search("[wW][eE][bB]",self.name)!=None and self.source['web']=='yes':
            self.valid=True
        elif re.search("[hH][dD][tT][vV]",self.name)!=None and self.source['tv']=='yes':
            self.valid=True
        #set invalid
        elif re.search("[sS][aA][mM][pP][lL][eE]",self.name)!=None or re.search("[tT][rR][aA][iL][eE][rR]",self.name)!=None:
            self.valid=False
        elif re.search("[rR][eE][mM][uU][xX]",self.name)!=None and self.source['remux']=='no':
            self.valid=False
        elif re.search("[rR][eE][mM][uU][xX]",self.name)==None and re.search("[bB][lL][uU]",self.name)!=None and self.source['blu']=='no':
            self.valid=False
        elif re.search("[wW][eE][bB]",self.name)!=None and self.source['web']=='no':
            self.valid=False
        elif re.search("[hH][dD][tT][vV]",self.name)!=None and self.source['tv']=='no':
            self.valid=False
        else:
            self.valid=True

    def set_type(self):
        if re.search("[rR][eE][mM][uU][xX]",self.name)!=None and self.source['remux']=='yes':
            self.type="Remux"
        elif re.search("[rR][eE][mM][uU][xX]",self.name)==None and re.search("[bB][lL][uU]",self.name)!=None and self.source['blu']=='yes':
            self.type="Blu-Ray"
        elif re.search("[wW][eE][bB]",self.name)!=None and self.source['web']=='yes':
            self.type="WEB"
        elif re.search("[hH][dD][tT][vV]",self.name)!=None and self.source['tv']=='yes':
            self.type="HDTV"
        else:
            self.type="Other"
    def set_encode(self):
        if re.search("[rR][eE][mM][uU][xX]",self.name)!=None and self.source['remux']=='yes':
            self.encode=False
        elif re.search("[rR][eE][mM][uU][xX]",self.name)==None and re.search("[bB][lL][uU]",self.name)!=None and self.source['blu']=='yes':
            self.encode=True
        elif (re.search("[wW][eE][bB]-[rR]",self.name)!=None or re.search("[wW][eE][bB][rR]",self.name)!=None) and self.source['web']=='yes':
            self.encode=True
        elif (re.search("[wW][eE][bB]-[dD]",self.name)!=None or re.search("[wW][eE][bB][dD]",self.name)!=None) and self.source['web']=='yes':
            self.enonde=False
        elif re.search("[hH][dD][tT][vV]",self.name)!=None and self.source['tv']=='yes':
            self.encode=False
        else:
            self.encode=False
    """
    Scanning File Functions
    """

def download_file(arguments,line,source,errorpath):
    currentfile=File(line,arguments,source)
    currentfile.set_valid()
    if currentfile.get_valid()==True:
        currentfile.set_size()
        currentfile.set_type()
        for site in arguments["--sites"].split(","):
            get_matches(site,errorpath,arguments,currentfile)
    if currentfile.get_valid()==False:
        return
    """
    Missing files Functions
    """
def scan_file(arguments,txt,line,source,errorpath):
    folders=open(txt,"r")
    currentfile=File(line,arguments,source)
    currentfile.set_valid()
    if currentfile.get_valid()==True:
        currentfile.set_size()
        currentfile.set_encode()
        currentfile.set_type()
        for site in arguments["--sites"].split(","):
            get_matches(site,errorpath,arguments,currentfile,currentfile.get_encode())
    if currentfile.get_valid()==False:
        print("Type excluded")
        return
