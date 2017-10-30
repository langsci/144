from sanitycheck import LSPDir
import re
from git import Repo
import os
import sys

    
if __name__ == "__main__":
  overleafurl = sys.argv[1]
  m = re.search('([0-9]{7,}[a-z]+)',overleafurl)
  overleafID = m.group(1)
  giturl = "https://git.overleaf.com/"+overleafID
  gitdir = './'+overleafID    
  Repo.clone_from(giturl, gitdir)
  lspdir = LSPDir(os.path.join(gitdir,'chapters'))
  print "checking %s" % ' '.join([f for f in lspdir.texfiles+lspdir.bibfiles])
  lspdir.check()
  lspdir.printErrors()