# -*- coding: utf-8 -*-

import os
import re
import shutil
import codecs
import uuid
import sys 
import langscibibtex

WD = '/home/doc2tex'
WD = '/tmp'
lspskeletond = '/home/doc2tex/skeletonbase'
#lspskeletond = '/home/snordhoff/versioning/git/langsci/lsp-converters/webapp/doc2tex/assets/skeletonbase'
#wwwdir = os.path.join(wd,'www')
wwwdir = '/var/www/wlport'        

def convert(fn, wd=WD, tmpdir=False):
    #print "converting %s" %fn
    odtfn = False
    os.chdir(wd)
    if tmpdir == False:
      tmpdir = fn.split('/')[-2] 
    #tmpdir = "."
    #print tmpdir
    if fn.endswith("docx"):        
        os.chdir(tmpdir)
        syscall = """soffice --headless   %s --convert-to odt "%s"  """ %(tmpdir,fn)
        #print syscall
        os.system(syscall)
        odtfn = fn.replace("docx","odt") 
    elif fn.endswith("doc"):        
        os.chdir(tmpdir)
        syscall = """soffice --headless   %s --convert-to odt "%s"  """ %(tmpdir,fn)
        #print syscall
        os.system(syscall)
        odtfn = fn.replace("doc","odt")
    elif fn.endswith("odt"):
        odtfn = fn 
    else:
        raise ValueError
    if odtfn == False:
        return False
    os.chdir(wd)
    texfn = odtfn.replace("odt","tex")
    #print texfn
    w2loptions = ("-clean",
    "-wrap_lines_after=0",
    "-multilingual=false", 
    #floats
    "-simple_table_limit=10"
    "-use_supertabular=false",
    "-float_tables=false", 
    "-float_figures=false", 
    "-use_caption=true", 
    '-image_options="width=\\textwidth"',
    #"use_colortbl=true",
    #"original_image_size=true",
    #input
    "-inputencoding=utf8",
    "-use_tipa=false", 
    "-use_bibtex=true", 
    "-ignore_empty_paragraphs=true",
    "-ignore_double_spaces=false", 
    #formatting
    "-formatting=convert_most",
    "-use_color=false",
    "-page_formatting=ignore_all",
    "-use_hyperref=true",
    #"-no_preamble=true"
    )
    syscall = """w2l {} "{}" "{}" """.format(" ".join(w2loptions), odtfn, texfn)
    #print syscall
    os.system(syscall)
    w2lcontent = open(texfn).read()
    preamble, text = w2lcontent.split(r"\begin{document}")
    text = text.split(r"\end{document}")[0] 
    preamble=preamble.split('\n')
    newcommands = '\n'.join([l for l in preamble if l.startswith('\\newcommand') and '@' not in l and 'writerlist' not in l and 'labellistLi' not in l and 'textsubscript' not in l]) # or l.startswith('\\renewcommand')])
    #replace all definitions of new environments by {}{}
    newenvironments = '\n'.join(['%s}{}{}'%l.split('}')[0] for l in preamble if l.startswith('\\newenvironment')  and 'listLi' not in l]) # or l.startswith('\\renewcommand')])
    newpackages = '\n'.join([l for l in preamble if l.startswith('\\usepackage') and "fontenc" not in l and "inputenc" not in l])
    newcounters = '\n'.join([l for l in preamble if l.startswith('\\newcounter')]+['\\newcounter{itemize}'])        
    return Document(newcommands,newenvironments, newpackages, newcounters, text)
    
class Document:
    def __init__(self, commands, environments, packages, counters, text):
        self.commands = commands
        self.environments = environments
        self.packages = packages
        self.counters = counters
        self.text = text
        self.modtext = self.getModtext()
        
    def ziptex(self): 
        localskeletond = os.path.join(WD,'skeleton')
        try:
           shutil.rmtree(localskeletond)
        except OSError:
            pass
        shutil.copytree(lspskeletond, localskeletond)
        os.chdir(localskeletond)
        localcommands = codecs.open('localcommands.tex','a', encoding='utf-8')
        localpackages = codecs.open('localpackages.tex','a', encoding='utf-8')
        localcounters = codecs.open('localcounters.tex','a', encoding='utf-8') 
        content =   codecs.open('chapters/filename.tex','w', encoding='utf-8') 
        contentorig =   codecs.open('chapters/filenameorig.tex','w', encoding='utf-8')  
        localcommands.write(self.commands)
        localcommands.write(self.environments)
        localcommands.close()
        localpackages.write(self.packages)
        localpackages.close()
        localcounters.write(self.counters)
        localcounters.close()
        content.write(self.modtext)
        content.close()
        contentorig.write(self.text)
        contentorig.close()
        os.chdir(WD)
        self.zipfn = str(uuid.uuid4())
        shutil.make_archive(self.zipfn, 'zip', localskeletond)
        shutil.move(self.zipfn+'.zip',wwwdir) 
        
        
        
    def getModtext(self,ID='key'):
        modtext = self.text
        explicitreplacements = ( #'`^v~
                
        (r"\'{a}",u"á"),
        (r"\'{e}",u"é"),
        (r"\'{i}",u"í"),
        (r"\'{o}",u"ó"),
        (r"\'{u}",u"ú"),
        (r"\'{y}",u"ý"),
        (r"\'{m}",u"ḿ"),
        (r"\'{n}",u"ń"),
        (r"\'{r}",u"ŕ"),
        (r"\'{l}",u"ĺ"),
        (r"\'{c}",u"ć"),
        (r"\'{s}",u"ś"),
        (r"\'{z}",u"ź"),
        
        (r"\`{a}",u"à"),
        (r"\`{e}",u"è"),
        (r"\`{i}",u"ì"),
        (r"\`{o}",u"ò"),
        (r"\`{u}",u"ù"),
        (r"\`{y}",u"ỳ"),
        (r"\`{n}",u"ǹ"),        
        
        (r"\^{a}",u"â"),
        (r"\^{e}",u"ê"),
        (r"\^{i}",u"î"),
        (r"\^{o}",u"ô"),
        (r"\^{u}",u"û"),
        (r"\^{y}",u"ŷ"),
        (r"\^{c}",u"ĉ"),
        (r"\^{s}",u"ŝ"),
        (r"\^{z}",u"ẑ"),
        
        
        (r"\~{a}",u"ã"),
        (r"\~{e}",u"ẽ"),
        (r"\~{i}",u"ĩ"),
        (r"\~{o}",u"õ"),
        (r"\~{u}",u"ũ"),
        (r"\~{y}",u"ỹ"),
        (r"\~{n}",u"ñ"),
        
        
        (r"\v{a}",u"ǎ"),
        (r"\v{e}",u"ě"),
        (r"\v{i}",u"ǐ"),
        (r"\v{o}",u"ǒ"),
        (r"\v{u}",u"ǔ"), 
        (r"\v{n}",u"ň"),
        (r"\v{r}",u"ř"), 
        (r"\v{c}",u"č"),
        (r"\v{s}",u"š"),
        (r"\v{z}",u"ž"),
        (r"\v{C}",u"Č"),
        (r"\v{S}",u"Š"),
        (r"\v{Y}",u"Ž"), 
        
        (r"\u{a}",u"ă"),
        (r"\u{e}",u"ĕ"),
        (r"\u{i}",u"ĭ"),
        (r"\u{o}",u"ŏ"),
        (r"\u{u}",u"ŭ"),        
        (r"\u{A}",u"Ă"),
        (r"\u{E}",u"Ĕ"),
        (r"\u{I}",u"Ĭ"),
        (r"\u{O}",u"Ŏ"),
        (r"\u{U}",u"Ŭ"),
        
        (r"\={a}",u"ā"),
        (r"\={e}",u"ē"),
        (r"\={i}",u"ī"),
        (r"\={o}",u"ō"),
        (r"\={u}",u"ū"),        
        (r"\={A}",u"Ā"),
        (r"\={E}",u"Ē"),
        (r"\={I}",u"Ī"),
        (r"\={O}",u"Ō"),
        (r"\={U}",u"Ū"),
        
        ("{\\textquoteleft}","`"),
        ("{\\textgreater}",">"),
        ("{\\textless}","<"),
                                ("{\\textquotedblleft}","``"), 
                                ("{\\textquoteright}","'"),
                                ("{\\textquotedblright}","''"),
                                ("{\\textquotesingle}","'"),
                                ("{\\textquotedouble}",'"'), 
                                ("\\par}","}"),
                                ("\\clearpage","\n"),
                                #("\\begin","\n\\begin"),
                                #("\\end","\n\\end"), 
                                #(" }","} "),%causes problems with '\ '
                                ("supertabular","tabular"),  
                                ("\~{}","{\\textasciitilde}"), 
                                #("\\section","\\chapter"),  
                                #("\\subsection","\\section"),  
                                #("\\subsubsection","\\subsection"),  
                                
                                ("""\\begin{listWWNumiileveli}
\\item 
\\setcounter{listWWNumiilevelii}{0}
\\begin{listWWNumiilevelii}
\\item 
\\begin{styleLangSciLanginfo}""","\\begin{styleLangSciLanginfo}"),#MSi langsci
                                
                                ("""\\begin{listWWNumiileveli}
\\item 
\\setcounter{listWWNumiilevelii}{0}
\\begin{listWWNumiilevelii}
\\item 
\\begin{stylelsLanginfo}""","\\begin{stylelsLanginfo}"),#MSi ls
                                
                                ("""\\begin{listWWNumiileveli}
\\item 
\\begin{styleLangSciLanginfo}\n""","\\ea\\label{ex:key:}\n%%1st subexample: change \\ea\\label{...} to \\ea\\label{...}\\ea; remove \\z  \n%%further subexamples: change \\ea to \\ex; remove \\z  \n%%last subexample: change \\z to \\z\\z \n\\langinfo{}{}{"),#MSii langsci
                                
                                ("""\\begin{listWWNumiileveli}
\\item 
\\begin{stylelsLanginfo}\n""","\\ea\\label{ex:key:}\n%%1st subexample: change \\ea\\label{...} to \\ea\\label{...}\\ea; remove \\z  \n%%further subexamples: change \\ea to \\ex; remove \\z  \n%%last subexample: change \\z to \\z\\z \n\\langinfo{}{}{"),#MSii ls
                                
                                ("""\\begin{listLangSciLanginfoiileveli}
\\item 
\\begin{styleLangSciLanginfo}""","\\begin{styleLangSciLanginfo}"),#OOi langsci
                                
                                ("""\\begin{listlsLanginfoiileveli}
\\item 
\\begin{stylelsLanginfo}""","\\begin{stylelsLanginfo}"),#OOi ls
                                
                                ("""\\begin{listLangSciLanginfoiilevelii}
\\item 
\\begin{styleLangSciLanginfo}""","\\begin{styleLangSciLanginfo}"),#OOii langsci
                                
                                ("""\\begin{listlsLanginfoiilevelii}
\\item 
\\begin{stylelsLanginfo}""","\\begin{stylelsLanginfo}"),#OOii ls
                                
                                ("""\\end{styleLangSciLanginfo}


\\end{listWWNumiilevelii}
\\end{listWWNumiileveli}""","\\end{styleLangSciLanginfo}"),   #langsci  
                                
                                ("""\\end{stylelsLanginfo}


\\end{listWWNumiilevelii}
\\end{listWWNumiileveli}""","\\end{stylelsLanginfo}"),     #ls
                                
                                ("""\\end{styleLangSciLanginfo}

\\end{listWWNumiilevelii}
\\end{listWWNumiileveli}""","\\end{styleLangSciLanginfo}"), #langsci
                                
                                
                                ("""\\end{stylelsLanginfo}

\\end{listWWNumiilevelii}
\\end{listWWNumiileveli}""","\\end{stylelsLanginfo}"), #ls
                                 
                                
                                ("\\begin{styleLangSciLanginfo}\n","\\ea\label{ex:key:}\n\\langinfo{}{}{"),
                                ("\\begin{stylelsLanginfo}\n","\\ea\label{ex:key:}\n\\langinfo{}{}{"),

                                ("\\begin{listWWNumiilevelii}\n\\item \n\\ea\\label{ex:key:}\n",""),

                                ("\n\\end{styleLangSciLanginfo}\n","}\\\\\n"),                          
                                ("\\begin{styleLangSciExample}\n","\n\\gll "),
                                ("\\end{styleLangSciExample}\n","\\\\"),
                                ("\\begin{styleLangSciSourceline}\n","\\gll "),
                                ("\\end{styleLangSciSourceline}\n","\\\\"),

                                ("\n\\end{stylelsLanginfo}\n","}\\\\\n"),                          
                                ("\\begin{stylelsExample}\n","\n\\gll "),
                                ("\\end{stylelsExample}\n","\\\\"),
                                ("\\begin{stylelsSourceline}\n","\\gll "),
                                ("\\end{stylelsSourceline}\n","\\\\"),
                                ("\\end{listWWNumiileveli}\n\\gll","\\gll"),

                                ("\\begin{styleLangSciIMT}\n","     "),
                                ("\\end{styleLangSciIMT}\n","\\\\"),
                                ("\\begin{styleLangSciTranslation}\n","\\glt "),
                                ("\\end{styleLangSciTranslation}","\z"), 
                                ("\\begin{styleLangSciTranslationSubexample}\n","\\glt "),
                                ("\\end{styleLangSciTranslationSubexample}","\z"), 

                                ("\\begin{stylelsIMT}\n","     "),
                                ("\\end{stylelsIMT}\n","\\\\"),
                                ("\\begin{stylelsTranslation}\n","\\glt "),
                                ("\\end{stylelsTranslation}","\z"), 
                                ("\\begin{stylelsTranslationSubexample}\n","\\glt "),
                                ("\\end{stylelsTranslationSubexample}","\z"), 

                                ("""\\setcounter{listWWNumiileveli}{0}
\\ea\\label{ex:key:}""",""),#MS
                                #("""\\setcounter{listLangSciLanginfoiilevelii}{0}
#\\ea\\label{ex:key:}""",""),#OO
                                ("""\\begin{listLangSciLanginfoiileveli}
\item""","\\ea\label{ex:key:}"),
                                ("""\setcounter{listLangSciLanginfoiilevelii}{0}
\\ea\label{ex:key:}""",""),
                                ("\n\\end{listLangSciLanginfoiileveli}",""), 
                                ("\n\\end{listLangSciLanginfoiilevelii}",""), 

                                ("""\\begin{listlsLanginfoiileveli}
\item""","\\ea\label{ex:key:}"),
                                ("""\setcounter{listlsLanginfoiilevelii}{0}
\\ea\label{ex:key:}""",""),
                                ("\n\\end{listlsLanginfoiileveli}",""), 
                                ("\n\\end{listlsLanginfoiilevelii}",""), 

                                ("\n\\glt ~",""), 
                                #end examples
                                ("{styleQuote}","{quote}"),  
                                ("{styleAbstract}","{abstract}"),  
                                ("textstylelsCategory","textsc"),  
                                ("textstylelsCategory","textsc"),  
                                #("\\begin{styleListParagraph}","%\\begin{epigram}"),
                                #("\\end{styleListParagraph}","%\\end{epigram}"), 
                                #("\\begin{styleListenabsatz}","%\\begin{epigram}"),
                                #("\\end{styleListenabsatz}","%\\end{epigram}"), 
                                #("\\begin{styleEpigramauthor}","%\\begin{epigramauthor}"),
                                #("\\end{styleEpigramauthor}","%\\end{epigramauthor}"),  
                                ("{styleConversationTranscript}","{lstlisting}"),   
                                ("\ "," "), 					    
				#(" }","} "),  
                                #("\\setcounter","%\\setcounter"),  
                                ("\n\n\\item","\\item"),  
                                ("\n\n\\end","\\end") 
                                
                            )    
        yanks =  ("\\begin{flushleft}",
                    "\\end{flushleft}",
                    "\\centering",
                    "\\raggedright",
                    "\\par ",
                    "\\tablehead{}", 
                    "\\textstylepagenumber",
                    "\\textstyleCharChar", 
                    "\\textstyleInternetlink",
                    "\\textstylefootnotereference",
                    "\\textstyleFootnoteTextChar",
                    "\\textstylepagenumber",
                    "\\textstyleappleconvertedspace",
                    "\\pagestyle{Standard}",
                    "\\hline",
                    "\\begin{center}",
                    "\\end{center}",
                    "\\begin{styleStandard}",
                    "\\end{styleStandard}",
                    "\\begin{styleBodytextC}",
                    "\\end{styleBodytextC}",
                    "\\begin{styleBodyTextFirst}",
                    "\\end{styleBodyTextFirst}",
                    "\\begin{styleIllustration}",
                    "\\end{styleIllustration}",
                    "\\begin{styleTabelle}",
                    "\\end{styleTabelle}",
                    "\\begin{styleAbbildung}",
                    "\\end{styleAbbildung}",
                    "\\begin{styleTextbody}",
                    "\\end{styleTextbody}",
                    "\\maketitle",
                    "\\hline",
                    "\\arraybslash",
                    "\\textstyleAbsatzStandardschriftart{}",
                    "\\textstyleAbsatzStandardschriftart",
                    "[Warning: Image ignored] % Unhandled or unsupported graphics:",
                    "%\\setcounter{listWWNumileveli}{0}\n",
                    "%\\setcounter{listWWNumilevelii}{0}\n",
                    "%\\setcounter{listWWNumiileveli}{0}\n",
                    "%\\setcounter{listWWNumiilevelii}{0}\n",
                    "%\\setcounter{listLangSciLanginfoiileveli}{0}\n",
                    "%\\setcounter{listlsLanginfoiileveli}{0}\n",
                    "\\setcounter{itemize}{0}",                    
                    "\\setcounter{page}{1}",
                    "\\mdseries "
                    ) 
        for old, new in explicitreplacements:
            modtext = modtext.replace(old,new)
            
        for y in yanks:
            modtext = modtext.replace(y,'')
        #unescape w2l unicode
        w2lunicodep3 = re.compile(r'(\[[0-9A-Fa-f]{3}\?\])')
        w2lunicodep4 = re.compile(r'(\[[0-9A-Da-d][0-9A-Fa-f]{3}\?\])') #intentionally leaving out PUA   
        #for m in w2lunicodep3.findall(modtext):
          #modtext=modtext.replace(m,'\u0{}'.format(m[1:-2]).decode('unicode_escape'))
        #for m in w2lunicodep4.findall(modtext):
            #modtext=modtext.replace(m,'\u{}'.format(m[1:-2]).decode('unicode_escape'))
        #remove marked up white space and punctuation
        modtext = re.sub("\\text(it|bf|sc)\{([ \.,]*)\}","\\2",modtext)  
        
        #remove explicit counters. These are not usefull when from autoconversion 
        
        #remove explicit table widths
        modtext = re.sub("m\{-?[0-9.]+(in|cm)\}","X",modtext)  
        modtext = re.sub("X\|","X",modtext)
        modtext = re.sub("\|X","X",modtext)
        modtext = re.sub(r"\\fontsize\{.*?\}\\selectfont","",modtext)
        modtext = modtext.replace("\\multicolumn{1}{l}{}","")
        modtext = modtext.replace("\\multicolumn{1}{l}","")
        #remove stupid Open Office styles 
        modtext = re.sub("\\\\begin\\{styleLangSciSectioni\\}\n+(.*?)\n+\\\\end\\{styleLangSciSectioni\\}","\\section{ \\1}",modtext) #whitespace in front of capture due to some strange chars showing up without in Strik book
        modtext = re.sub("\\\\begin\\{styleLangSciSectionii\\}\n+(.*?)\n+\\\\end\\{styleLangSciSectionii\\}","\\subsection{ \\1}",modtext)
        modtext = re.sub("\\\\begin\\{styleLangSciSectioniii\\}\n+(.*?)\n+\\\\end\\{styleLangSciSectioniii\\}","\\subsubsection{ \\1}",modtext)
        modtext = re.sub("\\\\begin\\{styleLangSciSectioniv\\}\n+(.*?)\n+\\\\end\\{styleLangSciSectioniv\\}","\\subsubsubsection{ \\1}",modtext)
        
        modtext = re.sub("\\\\begin\\{stylelsSectioni\\}\n+(.*?)\n+\\\\end\\{stylelsSectioni\\}","\\section{ \\1}",modtext) #whitespace in front of capture due to some strange chars showing up without in Strik book
        modtext = re.sub("\\\\begin\\{stylelsSectionii\\}\n+(.*?)\n+\\\\end\\{stylelsSectionii\\}","\\subsection{ \\1}",modtext)
        modtext = re.sub("\\\\begin\\{stylelsSectioniii\\}\n+(.*?)\n+\\\\end\\{stylelsSectioniii\\}","\\subsubsection{ \\1}",modtext)
        modtext = re.sub("\\\\begin\\{stylelsSectioniv\\}\n+(.*?)\n+\\\\end\\{stylelsSectioniv\\}","\\subsubsubsection{ \\1}",modtext)
        
        modtext = re.sub(r"\\begin\{styleHeadingi}\n+(.*?)\n+\\end\{styleHeadingi\}","\\chapter{\\1}",modtext) 
        modtext = re.sub("\\\\begin\\{styleHeadingii\\}\n+(.*?)\n+\\\\end\\{styleHeadingii\\}","\\section{\\1}",modtext)
        modtext = re.sub("\\\\begin\{styleHeadingiii\}\n+(.*?)\n+\\\\end\{styleHeadingiii}","\\subsubsection{\\1}",modtext)
        modtext = re.sub("\\\\begin\{styleHeadingiv\}\n+(.*?)\n+\\\\end\{styleHeadingiv}","\\subsubsection{\\1}",modtext)
        
        #remove explicit shorttitle for sections
        modtext = re.sub("\\\\(sub)*section(\[.*?\])\{(\\text[bfmd][bfmd])\?(.*)\}","\\\\1section{\\4}",modtext) 
        #                        several subs | options       formatting           title ||   subs      title
        #move explict section number to end of line and comment out
        modtext = re.sub("section\{([0-9\.]+ )(.*)","section{\\2 %\\1/",modtext)
        modtext = re.sub("section\[.*?\]","section",modtext)
        #                                 number    title         title number
        #table cells in one row
        modtext = re.sub("[\n ]*&[ \n]*",' & ',modtext)
        modtext = modtext.replace(r'\ &','\&')
        #collapse newlines
        modtext = re.sub("\n*\\\\\\\\\n*",'\\\\\\\\\n',modtext) 
        #bib
        modtext = re.sub("\(([A-Z][a-z]+) +et al\.  +([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citep[\\3]{\\1EtAl\\2}",modtext)
        modtext = re.sub("\(([A-Z][a-z]+) +([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citep[\\3]{\\1\\2}",modtext)
        modtext = re.sub("\(([A-Z][a-z]+) +et al\. +([12][0-9]{3}[a-z]?)\)","\\citep{\\1EtAl\\2}",modtext)
        modtext = re.sub("\(([A-Z][a-z]+) +([12][0-9]{3}[a-z]?)\)","\\citep{\\1\\2}",modtext)
        #citet
        modtext = re.sub("([A-Z][a-z]+) +et al. +\(([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citet[\\3]{\\1EtAl\\2}",modtext)
        modtext = re.sub("([A-Z][a-z]+) +\(([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citet[\\3]{\\1\\2}",modtext)
        modtext = re.sub("([A-Z][a-z]+) +et al. +\(([12][0-9]{3}[a-z]?)\)","\\citet{\\1EtAl\\2}",modtext)
        modtext = re.sub("([A-Z][a-z]+) +\(([12][0-9]{3}[a-z]?)\)","\\citet{\\1\\2}",modtext)
        #modtext = re.sub("([A-Z][a-z]+) +([12][0-9]{3}[a-z]?)","\\citet{\\1\\2}",modtext)i
        #very last thing: catch all citealt
        modtext = re.sub("([A-Z][a-z]+) +([12][0189][0-9]{2}[a-z]?)","\\citealt{\\1\\2}",modtext)    
        modtext = re.sub("([A-Z][a-z]+) \\& \\citet{","\\citet{\\1",modtext)        
        modtext = re.sub("([A-Z][a-z]+) \\& \\citealt{","\\citealt{\\1",modtext)        
        #examples
        modtext = modtext.replace("\n()", "\n\\ea \n \\gll \\\\\n   \\\\\n \\glt\n\\z\n\n")
        modtext = re.sub("\n\(([0-9]+)\)", """\n\ea%\\1
    \label{ex:key:\\1}
    \\\\gll\\\\newline
        \\\\newline
    \\\\glt
    \z

        """,modtext)
        modtext = re.sub("\\label\{(bkm:Ref[0-9]+)\}\(\)", """ea%\\1
    \label{\\1}  
    \\\\gll \\\\newline  
        \\\\newline
    \\\\glt
    \z

    """,modtext)
    
        #subexamples
        modtext = modtext.replace("\n *a. ","\n% \\ea\n%\\gll \n%    \n%\\glt \n")
        modtext = modtext.replace("\n *b. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n")    
        modtext = modtext.replace("\n *c. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n")  
        modtext = modtext.replace("\n *d. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n") 
        modtext = modtext.replace(r"\newline",r"\\")


        modtext = re.sub("\n\\\\textit{Table ([0-9]+)[\.:] *(.*?)}\n","%%please move \\\\begin{table} just above \\\\begin{tabular . \n\\\\begin{table}\n\\caption{\\2}\n\\label{tab:key:\\1}\n\\end{table}",modtext)
        modtext = re.sub("\nTable ([0-9]+)[\.:] *(.*?) *\n","%%please move \\\\begin{table} just above \\\\begin{tabular\n\\\\begin{table}\n\\caption{\\2}\n\\label{tab:\\1}\n\\end{table}",modtext)#do not add } after tabular
        modtext = re.sub("Table ([0-9]+)","\\\\tabref{tab:key:\\1}",modtext) 
        modtext = re.sub("\nFigure ([0-9]+)[\.:] *(.*?)\n","\\\\begin{figure}\n\\caption{\\2}\n\\label{fig:key:\\1}\n\\end{figure}",modtext)
        modtext = re.sub("Figure ([0-9]+)","\\\\figref{fig:key:\\1}",modtext)
        modtext = re.sub("Section ([0-9\.]+)","\\\\sectref{sec:key:\\1}",modtext) 
        modtext = re.sub("\\\\(begin|end){minipage}.*?\n",'',modtext)
        modtext = re.sub("\\\\begin{figure}\[h\]",'\\\\begin{figure}',modtext)
        
        
        modtext = re.sub("(begin\{tabular\}[^\n]*)",r"""\1
\lsptoprule""",modtext) 
        modtext = re.sub(r"\\end{tabular}\n*",r"""\lspbottomrule
\end{tabular}\n""",modtext) 

        modtext = modtext.replace("begin{tabular}","begin{tabularx}{\\textwidth}")
        modtext = modtext.replace("end{tabular}","end{tabularx}")

        modtext = re.sub(r"\\setcounter{[^}]+\}\{0\}",'',modtext)

        modtext = re.sub("""listWWNum[ivxlc]+level[ivxlc]+""","itemize",modtext) 
        modtext = re.sub("""listL[ivxlc]+level[ivxlc]+""","itemize",modtext) 
        
        modtext = modtext.replace("& \\begin{itemize}\n\\item","& \n%%\\begin{itemize}\\item\n")  
        modtext = modtext.replace("\\end{itemize}\\\\\n","\\\\\n%%\\end{itemize}\n")  
        modtext = modtext.replace("& \\end{itemize}","& %%\\end{itemize}\n")
        
        
        modtext = re.sub("""\n+\\z""","\\z",modtext) 
        modtext = re.sub("""\n\n+""","\n\n",modtext) 
        
        
        #merge useless chains of formatting
        modtext = re.sub("(\\\\textbf\{[^}]+)\}\\\\textbf\{","\\1",modtext)
        modtext = re.sub("(\\\\textit\{[^}]+)\}\\\\textit\{","\\1",modtext)
        modtext = re.sub("(\\\\textsc\{[^}]+)\}\\\\textsc\{","\\1",modtext)
        modtext = re.sub("(\\\\texttt\{[^}]+)\}\\\\texttt\{","\\1",modtext)
        modtext = re.sub("(\\\\emph\{[^}]+)\}\\\\emph\{","\\1",modtext)
        
        
        #TODO propagate textbf in gll
        
        #for s in ('textit','textbf','textsc','texttt','emph'):
          #i=1
          #while i!=0:
            #modtext,i = re.subn('\\%s\{([^\}]+) '%s,'\\%s{\\1} \\%s{'%(s,s),modtext) 
        modtext = re.sub("\\\\includegraphics\[.*?width=\\\\textwidth","%please move the includegraphics inside the {figure} environment\n%%\includegraphics[width=\\\\textwidth",modtext)
        
        modtext = re.sub("\\\\item *\n+",'\\item ',modtext)
        
        modtext = re.sub("\\\\footnote\{ +",'\\\\footnote{',modtext)
        #put spaces on right side of formatting
        #right
        modtext = re.sub(" +\\}",'} ',modtext)
        #left
        modtext = re.sub("\\\\text(it|bf|sc|tt|up|rm)\\{ +",' \\\\text\\1{',modtext)
        modtext = re.sub("\\\\text(it|bf|sc|tt|up|rm)\\{([!?\(\)\[\]\.\,\>]*)\\}",'\\2',modtext)
        
        
        
        #duplicated section names 
        modtext = re.sub("(chapter|section|paragraph)\[.*?\](\{.*\}.*)","\\1\\2",modtext)
        
        
        bibliography = ''
        modtext = modtext.replace(r'\\textbf{References}','References')
        modtext = modtext.replace('\\section{References}','References')
        modtext = modtext.replace('\\chapter{References}','References') 
        a = re.compile("\n\s*References\s*\n").split(modtext)
        if len(a)==2:
                modtext = a[0]
                refs = a[1].split('\n')
                bibliography = '\n'.join([langscibibtex.Record(r).bibstring for r in refs])                
        return modtext+"\n\\begin{verbatim}%%move bib entries to  localbibliography.bib\n"+bibliography+'\\end{verbatim}'
            
if __name__ == '__main__':
    fn = sys.argv[1]
    cwd = os.getcwd()
    d = convert(fn,tmpdir=cwd,wd=cwd)
    tx = d.text
    mt = d.modtext
    out1 = codecs.open("temporig.tex", "w", "utf-8")
    out2 = codecs.open("temp.tex", "w", "utf-8")
    out1.write(tx)
    out2.write(mt)
    out1.close()
    out2.close()
