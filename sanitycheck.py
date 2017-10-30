# -*- coding: utf-8 -*-
import re
import glob
import sys
import fnmatch
import os
import textwrap
import uuid
import enchant
from enchant.tokenize import get_tokenizer

class LSPError:
  def __init__(self,fn,linenr,line,offendingstring,msg):
    self.fn = fn.split('/')[-1]
    self.linenr = linenr
    self.line = line
    self.offendingstring = offendingstring
    self.msg = msg
    self.pre =self.line.split(self.offendingstring)[0]
    self.post =self.line.split(self.offendingstring)[1]
    self.ID = uuid.uuid1()
    self.name = str(hash(msg))[-6:]
    t = textwrap.wrap(self.name,2)[-3:]
    self.color =  "rgb({},{},{})".format(int(t[0])+140,int(t[1])+140,int(t[2])+140)
    self.bordercolor = "rgb({},{},{})".format(int(t[0])+100,int(t[1])+100,int(t[2])+100)
 
    
  def __str__(self): 
    return u"{linenr}:{offendingstring}\n\t{msg}".format(**self.__dict__).encode('utf8')

class LSPFile:
  def __init__(self,fn):
    self.fn = fn
    self.content = open(fn).read().decode('utf8')
    self.lines = self.split_(self.content)
    self.errors = []
    self.spelld = enchant.Dict("en_UK") 
    self.tknzr = get_tokenizer("en_UK")
    self.spellerrors = []
    self.latexterms = ("newpage","clearpage","textit","textbf","textsc","textwidth","tabref","figref","sectref","emph")
    
  def split_(self,c):
    result = self._removecomments(c).split('\n')
    return result
    
  def _removecomments(self,s):
    #negative lookbehind 
    result = re.sub('(?<!\\\\)%.*\n','\n',s)
    return result
	    
  def check(self):
    self.errors=[]
    for i,l in enumerate(self.lines):
      if '\\chk' in l: #the line is explicitely marked as being correct
	continue 
      for ap,msg in self.antipatterns:
	m = re.search('(%s)'%ap,l)
	if m != None:
	  g = m.group(1)
	  if g!='':	    
	    self.errors.append(LSPError(self.fn,i,l,g,msg))	 
      for posp,negp,msg in self.posnegpatterns:
	posm = re.search('(%s)'%posp,l)
	if posm==None:
	  continue
	g = posm.group(1)
	negm = re.search(negp,l)
	if negm==None:
	  self.errors.append(LSPError(self.fn,i,l,g,msg)) 
	  
  def spellcheck(self):
    result = sorted(list(set([t[0] for t in self.tknzr(self.content) if self.spelld.check(t[0])==False and t[0] not in self.latexterms])))
    self.spellerrors =  result
 

class TexFile(LSPFile):  
  antipatterns = (
    (r" et al.","Please use the citation commands \\citet and \\citep"),      #et al in main tex
    (r"setfont","You should not set fonts explicitely"),      #no font definitions
    (r"\\(small|scriptsize|footnotesize)","Please consider whether changing font sizes manually is really a good idea here"),      #no font definitions
    (r"([Tt]able|[Ff]igure|[Ss]ection|[Pp]art|[Cc]hapter\() *\\ref","It is often advisable to use the more specialized commands \\tabref, \\figref, \\sectref, and \\REF for examples"),      #no \ref
    #("",""),      #\ea\label
    #("",""),      #\section\label
    (" \\footnote","Footnotes should not be preceded by a space"),
    ("\\caption\{.*[^\.]\} +$","The last character of a caption should be a '.'"),      #captions end with .
    #("",""),      #footnotes end with .
    (r"\[[0-9]+,[0-9]+\]","Please use a space after the comma in lists of numbers "),      #no 12,34 without spacing
    ("\([^)]+\\cite[pt][^)]+\)","In order to avoid double parentheses, it can be a good idea to use \\citealt instead of \\citet or \\citep"),    
    ("([0-9]+-[0-9]+)","Please use -- for ranges instead of -"),      
    #(r"[0-9]+ *ff","Do not use ff. Give full page ranges"),
    (r"[^-]---[^-]","Use -- with spaces rather than ---"), 
    (r"tabular.*\|","Vertical lines in tables should be avoided"),   
    (r"\hline","Use \\midrule rather than \\hline in tables"),      
    (r"\gl[lt] *[a-z].*[\.?!] *\\\\ *$","Complete sentences should be capitalized in examples"), 
    (r"\section.*[A-Z].*[A-Z].*","Only capitalize this if it is a proper noun"), 
    (r"\section.*[A-Z].*[A-Z].*","Only capitalize this if it is a proper noun"), 
    (r"[ (][12][8901][0-9][0-9]","Please check whether this should be part of a bibliographic reference"), 
    (r"(?<!\\)[A-Z]{3,}","It is often a good idea to use \\textsc\{smallcaps} instead of ALLCAPS"), 
    ("[?!;\.,][A-Z]","Please use a space after punctuation (or use smallcaps in abbreviations)"),        
      )

  posnegpatterns = (
    (r"\[sub]*section\{",r"\label","All sections should have a \\label. This is not necessary for subexamples."),
    #(r"\\ea.*",r"\label","All examples should have a \\label"),
    (r"\\gll\W+[A-Z]",r"[\.?!][ }]*\\\\ *$","All vernacular sentences should end with punctuation"),
    (r"\\glt\W+[A-Z]",r"[\.?!]['’”ʼ]+[ }\\]*$","All translated sentences should end with punctuation"),
    )
    
  filechecks = (
    ("",""),    #src matches #imt
    ("",""),     #words
    ("",""),     #hyphens
    ("",""),    #tabulars have lsptoprule
    ("",""),    #US/UK                    
    )
   

#year not in order in multicite

class BibFile(LSPFile):
  
  antipatterns = (
    #("[Aa]ddress *=.*[,/].*[^ ]","No more than one place of publication. No indications of countries or provinces"), #double cities in address
    #("[Aa]ddress *=.* and .*","No more than one place of publication."), #double cities in address
    ("[Tt]itle * =.*: +(?<!{)[a-zA-Z]+","Subtitles should be capitalized. In order to protect the capital letter, enclose it in braces {} "), 
    ("[Aa]uthor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*","Full author names should be given. Only use abbreviated names if the author is known to prefer this. It is OK to use middle initials"),
    ("[Ee]ditor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*","Full editor names should be given. Only use abbreviated names if the editor is known to prefer this. It is OK to use middle initials"),
    ("[Aa]uthor *=.* et al","Do not use et al. in the bib file. Give a full list of authors"), 
    ("[Aa]uthor *=.*&.*","Use 'and' rather than & in the bib file"), 
    ("[Tt]itle *=(.* )?[IVXLCDM]*[IVX]+[IVXLCDM]*[\.,\) ]","In order to keep the Roman numbers in capitals, enclose them in braces {}"), 
    ("\.[A-Z]","Please use a space after a period or an abbreviated name"), 
    )
  posnegpatterns = []
  filechecks = []
  spellerrors = []



class LSPDir:
  def __init__(self,dirname):
    self.dirname = dirname
    self.texfiles = self.findallfiles('tex')
    self.bibfiles = self.findallfiles('bib')
    self.errors={} 
    
  def findallfiles(self, ext):
    matches = []
    for root, dirnames, filenames in os.walk(self.dirname):
      for filename in fnmatch.filter(filenames, '*.%s'%ext):
	  matches.append(os.path.join(root, filename))
    return matches
  	    
  def printErrors(self):
    for fn in self.errors:
      print fn
      fileerrors = self.errors[fn]
      print '%i possible errors found' % len(fileerrors)
      for e in fileerrors:
	try:
	  print e
	except TypeError:
	  print e.__dict__
	  raise
    #print "the following words were not found in the dictionary:", self.spellerrors
  
  def check(self):
    for tfn in self.texfiles:
      t = TexFile(tfn)
      t.check()
      t.spellcheck()
      self.errors[tfn] = [None,None]
      self.errors[tfn][0] = t.errors
      self.errors[tfn][1] = t.spellerrors
    for bfn in self.bibfiles:
      b = BibFile(bfn) 
      b.check()
      self.spellerrors = [] 
      self.errors[bfn] = [None,None]
      self.errors[bfn][0] = b.errors
      self.errors[bfn][1] = b.spellerrors
    
 
    
if __name__ == "__main__":
  try:
    d = sys.argv[1]
  except IndexError:
    d = '.'
  lspdir = LSPDir(d)
  print "checking %s" % ' '.join([f for f in lspdir.texfiles+lspdir.bibfiles])
  lspdir.check()
  lspdir.printErrors()
