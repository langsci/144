## --* encoding=utf8 *-- 
import sys
import re
import pprint 
import normalizebib
 
#pattern definitions
year = '\(? *(?P<year>[12][78901][0-9][0-9][a-f]?) *\)?' 
pages = u"(?P<pages>[0-9xivXIV]+[-––]+[0-9xivXIV]+)"
pppages = u"\(?[Pps\. ]*%s\)?"%pages
author = "(?P<author>.*?)" #do not slurp the year
ed = "(?P<ed>\([Ee]ds?\.?\))?"
editor = "(?P<editor>.+)"
booktitle = "(?P<booktitle>.+)"
title = "(?P<title>.*)"
journal = "(?P<journal>.*?)"
note = "(?P<note>.*)"
numbervolume = "(?P<volume>[-\.0-9/]+) *(\((?P<number>[-0-9/]+)\))?"
pubaddr = "(?P<address>.+) *:(?!/) *(?P<publisher>[^:]+[^\.\n])"
seriesnumber = "(?P<newtitle>.*) \((?P<series>.*?) +(?P<number>[-\.0-9/]+)\)"
SERIESNUMBER =  re.compile(seriesnumber)
#compiled regexes
BOOK = re.compile(u"{author} {ed}[\., ]*{year}[\., ]*{title}\. +{pubaddr}{note}".format(author=author,
                                                                          ed=ed,
                                                                          year=year,
                                                                          title=title,
                                                                          pubaddr=pubaddr,
                                                                          note=note))
ARTICLE = re.compile(u"{author}[., ]*{year}[., ]*{title}\. +{journal},? *{numbervolume}[\.,:] *{pages}{note}"\
            .format(pages=pppages,
                    author=author,
                    year=year,
                    journal=journal,
                    numbervolume=numbervolume,
                    title=title,
                    note=note)
                    )
INCOLLECTION = re.compile(u"{author}[., ]*{year}[., ]*{title}\. In {editor} \([Ee]ds?\. *\)[\.,]? {booktitle}[\.,]? {pages}\. +{pubaddr}\.{note}"\
                      .format(author=author,
                              year=year,
                              title=title,
                              editor=editor,
                              booktitle=booktitle,
                              pages=pppages,
                              pubaddr=pubaddr,
                              note=note)
                              )
MISC = re.compile("{author}[., ]*{year}[., ]*{title}\.? *(?P<note>.*)".format(author=author, year=year, title=title))

#regexes for telling entry types    
EDITOR = re.compile("[0-9]{4}.*(\([Ee]ds?\.?\))") #make sure the editor of @incollection is only matched after the year
PAGES = re.compile(pages)
PUBADDR = re.compile(pubaddr)

#fields to output
FIELDS = ["key",
    "title",
    "booktitle",
    "author",
    "editor",
    "year",
    "journal",
    "volume",
    "number",
    "pages",
    "address",
    "publisher",
    "note",
    "url",
    "series"
    ]
    
    
class Record():
  def __init__(self,s):  
    s=s.strip()
    self.orig = s    
    self.bibstring = s
    self.typ = "misc"    
    self.key = None
    self.title = None
    self.booktitle = None
    self.author = "Anonymous"
    self.editor = None
    self.year = None
    self.journal = None
    self.volume = None
    self.number  = None
    self.pages = None
    self.address = None
    self.publisher = None
    self.note = None 
    self.url = None 
    if  EDITOR.search(s):
      self.typ = "incollection"
      m = INCOLLECTION.search(s) 
      #print 1
      if m: 
        #print 2
        self.author = m.group('author')
        self.editor = m.group('editor')
        self.title = m.group('title')
        self.booktitle = m.group('booktitle')
        self.year = m.group('year') 
        self.address = m.group('address')
        self.publisher = m.group('publisher')
        self.pages = m.group('pages')   
        self.note = m.group('note')   
        #pprint.pprint(self.__dict__)
    elif  PAGES.search(s):      
      self.typ = "article"
      m = ARTICLE.search(s)
      if m:
        self.author = m.group('author')
        self.title = m.group('title')
        self.year = m.group('year')
        self.journal = m.group('journal')
        self.number = m.group('number')
        self.volume = m.group('volume')
        self.pages = m.group('pages')   
        self.note = m.group('note')   
    elif PUBADDR.search(s):
      self.typ = "book"  
      m = BOOK.match(s) 
      if m:
        self.author = m.group('author')
        if m.group('ed') != None:
          self.editor = m.group('author')
          self.author = None
        self.title = m.group('title')
        self.year = m.group('year')
        self.address = m.group('address')
        self.publisher = m.group('publisher')
        self.note = m.group('note')
    else: 
      m = MISC.search(s)
      if m:
        self.author = m.group('author')
        self.title = m.group('title')
        self.year = m.group('year')
        self.note = m.group('note') 
    if self.note=='.':
      self.note = None 
    try:
      self.author = self.author.replace('&', ' and ').replace('\ ', ' ')
    except AttributeError: 
      try:
        self.editor = self.editor.replace('&', ' and ')
      except AttributeError:
        return
    if self.title and "http" in self.title:
      t = self.title.split("http:")[0]
      self.url="http:"+'http://'.join(self.title.split("http:")[1:])
      self.title=t
    if self.title:
      m = SERIESNUMBER.match(self.title)
      if m:
        self.series = m.group('series')
        self.number = m.group('number')
        self.title = m.group('newtitle')
    #http
    #series volume
    authorpart = "Anonymous"
    yearpart = "9999" 
    try: 
      authorpart = self.author.split(',')[0].split(' ')[0] 
    except AttributeError: 
      authorpart = self.editor.split(',')[0].split(' ')[0] 
    try:
      yearpart = self.year[:4]
    except TypeError:
      return
    key = authorpart+yearpart 
    bibstring="@%s{%s,\n\t"%(self.typ,key)    
    fields = [(f,self.__dict__[f]) for f in self.__dict__ if f in FIELDS and self.__dict__[f] not in ('',None)]
    fields.sort()
    bibstring+=",\n\t".join(["%s = {%s}"%f for f in fields])
    bibstring+="\n}"  
    #print bibstring
    self.bibstring = normalizebib.Record(bibstring).bibtex() 

def getRecords(fn, splitter="\n\n"):
  c = open(fn).read()
  return [Record(s) for s in c.split(splitter)]

 
  
if __name__=="__main__":
  fn = sys.argv[1]
  lines = open(fn).readlines()
  for l in lines:
    if l.strip=='':
      continue
    r = Record(l) 
    print(r.bibstring)
    #r.tobibtex()