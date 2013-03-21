#! /usr/bin/env python
description = """
Program to generate pdfs from ead xml files. Can work in dir walk, file or list file mode.

Use file option to generate PDF for one file.
Use dir option to generate PDF for xml files in a dir tree. Default output is in
Use list option to generate PDF for file names listed in text file.
Default output directory is the same directory as xml file.
Use -help option to see complete list of options.
"""

import cgitb
cgitb.enable(format='text')

import os, sys
import logging, logging.handlers
import datetime
import timeout
import cStringIO
#use plac instead?
from optparse import OptionParser, OptionError
import re
import xml.etree.ElementTree as ET
import ho.pisa as pisa

from font_supports_file import test_file_against_font_coverage

def elementlist_tostring(element_list):
    retStr = ''
    for elem in element_list:
        if elem.text:
            retStr = ' '.join([retStr, elem.text])
    return retStr
from BeautifulSoup import BeautifulSoup

class NullHandler(logging.Handler):
    '''NullHandler for apps that don't have loggin setups
    '''
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger('OAC').addHandler(h)

PATH_TO_PROGS = os.environ.get("PATH_TO_PROGS",
                            os.path.abspath(os.path.split(__file__)[0])
                              )
XSLTFILE = os.path.join(PATH_TO_PROGS, "oac4_to_pdf.xslt")
CSSFILE = os.path.join(PATH_TO_PROGS, "oac_pdf.css")
NUMFILES_PROCESSED = 0
STRFTIME = '%Y%m%d:%H:%M:%S'
TIMEOUT_CONVERT = 2**5 #in seconds
LOG_FILE_PREFIX = "create_PDF_batch"
TIMEOUT_LOG_LEVEL = 90
LOG_BACKUP_COUNT = 10
LOG_LEVEL = logging.INFO
PARALLEL_PATH = 'pdf'
TMP_FILE_DIR = None

def build_parallel_dir(source_root, parallel_path=PARALLEL_PATH):
    '''Build the parallel dir root name

    >>> build_parallel_dir('/dsc/data/in/oac-ead/prime2002')
    /dsc/data/in/oac-ead/pdf
    '''
    return os.path.join(os.path.split(os.path.abspath(source_root))[0], parallel_path)

def build_parallel_path(source_path, source_root, parallel_path=PARALLEL_PATH):
    '''Create a parallel path given the file source path and the branching root
    for the source path. The branching root is the dir path at which the
    parallel structure should be rooted.

    '''
    # do work on absolute paths...
    source_path = os.path.abspath(source_path)
    source_root = os.path.abspath(source_root)
    parallel_root = build_parallel_dir(source_root)
    return source_path.replace(source_root, parallel_root)

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

info = Bunch(numtimeouts = 0,
             numerrs = 0,
             numfileattempt = 0,
             numfilecomplete = 0,
             timer = datetime.timedelta(0),
             starttime = datetime.datetime.now(),
            )

class PDFGenerator(object):
    '''Generic PDF generator based on pisa. Create a new PDFGenerator object for
    each different configuration of input file transform code & post-process
    code. Can then call obj.generate(inputfile, outputdir) to create a pdf file
    '''
    def __init__(self, cssfile=None, inputTransform=None,  postProcessor=None, debug=False
                 ):
        # if transforms are None, set to pass through function
        if inputTransform is None:
            self.inputTransform = self.__nullTransform
        else:
            self.inputTransform = inputTransform
        css_str = None
        if cssfile and os.path.isfile(cssfile):
            css = file(cssfile,'r')
            try:
                if css:
                    css_str = css.read()
            finally:
                css.close()
        self.css = css_str
        if postProcessor is None:
            self.postProcessor = lambda x,y: True
        else:
            self.postProcessor = postProcessor
        self.debug = debug

    def __html_to_pdf(self, htmlstring, pdffile, cssstring=None,
                    encoding='utf-8', debug=False):
        '''Converts an html string to pdf.
        inputs:
            htmlstring : string containing html to convert
            pdffile : file like object to write output to
            cssstring : string containing css to override default
            encoding : html encoding
            debug : debug flag

        Wrap call in try: finally: to close open file object

        returns pdf context object
        will raise some exceptions but must also check that 
        pdfcontext.err == 0
        '''
        # must convert any <br></br> to just <br/>
        # then feed result to pisaDocument
        pisaHTMLString = htmlstring.replace('<br></br>', '<br/>')
        #logging.error( 'pisaHTMLString is %s' % type(pisaHTMLString))
        # wrap string in file like StringIO
        pdfcontext = pisa.pisaDocument(cStringIO.StringIO(pisaHTMLString),
                             dest=pdffile,
                             debug=debug,
                             default_css=cssstring,
                             encoding=encoding
                            )
        return pdfcontext
    
    def __nullTransform(self, filepath, debug=False):
        if os.path.isfile(filepath):
            f = file(filepath, 'r')
            try:
                content = f.read()
            finally:
                f.close()
            return content
        else:
            raise OSError, "No such file:%s" % filepath

    def generate(self, filepath_in, filepath_out, savehtml=False, htmlpath=None, htmlonly=False):
        '''Trys to generate a pdf from the input file.
        Runs the input transform to create html string
        Then runs pisa on the html string.
        Outputs result to outputfilepath then runs
        post-processor on the outputfile
        Returns the intermediate html and postProcessor result?
        '''
        htmlstring = self.inputTransform(filepath_in, debug=self.debug)
        if savehtml or htmlonly:
            f = open(htmlpath, 'w')
            try:
                f.write(htmlstring)
            finally:
                f.close()
        result_pp = None
        if not htmlonly:
            foo = open(filepath_out, 'wb')
            try:
                self.__html_to_pdf(htmlstring, foo, self.css )
            finally:
                foo.close()
            result_pp = self.postProcessor(filepath_out, filepath_in)
        return htmlstring, result_pp

class OAC_EADtoPDFGenerator(object):
    '''Class for OAC specific EAD to PDF generation
    Defaults to OAC standards
    '''
    def __init__(self, path_to_xslt):
        self.timer = datetime.timedelta(0)
        self.starttime = datetime.datetime.now()
        self.numfileattempt = 0
        self.numfilecomplete = 0
        self.numtimeouts = 0
        self.numerrs = 0
        self.xsltpath = path_to_xslt
        self.postProcessor = PostProcessor_OACEAD()

    def canGeneratePDF(self, fname):
        return OAC_EADtoPDFGenerator.isNot_DC_or_METS_XML(fname)

    @staticmethod
    def isNot_DC_or_METS_XML(fname):
        '''Checks file name to ensure file is just a <foo>.xml
        '''
        (name, ext) = os.path.splitext(fname)
        if ext == '.xml':
            #check if extra . in name (.mets.xml etc)
            (n2, ext2) = os.path.splitext(name)
            if not ext2:
                return True
            #need to ignore .dc.xml & .mets.xml but not other names
            if not (ext2 == '.dc' or ext2 == '.mets'):
                return True
        return False

    @staticmethod
    def outpath(outdir_option, data_root, curdir):
        '''can probably cache some of this'''
        dirname = os.path.abspath(curdir)
        if not outdir_option:
            return dirname
        if outdir_option.lower().find('subdir=') != -1:
            subdirname = outdir_option[7:]
            subdir = os.path.join(dirname, subdirname)
            if os.path.exists(subdir):
                if not os.path.isdir(subdir):
                    #assert this??
                    pass
            else:
                os.mkdir(subdir)
    
            return subdir
        if outdir_option.lower().find('parallel') != -1:
            data_root = os.path.abspath(data_root)
            if outdir_option.lower().find('parallel=') != -1:
                root_out = os.path.abspath(outdir_option[9:])
            else:
                root_out = os.path.join(os.path.split(data_root)[0], PARALLEL_PATH)
            if not os.path.exists(root_out):
                os.makedirs(root_out)
            # remove common path from fpath
            absdirname = os.path.abspath(dirname)
            out_dir = absdirname.replace(data_root,root_out)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            return out_dir
    
        if outdir_option.lower().find('outdir=') != -1:
            logging.info( "outpath is finding: outdir")
            logging.info( "outdir strip = %s" % (outdir_option[7:], ))
            return os.path.abspath(outdir_option[7:])
    
        return dirname

    def nohtmlTransform(self, filepath, debug=False):
        foo = filepath+'.html'
        logging.info("Using existing html file %s to create PDF." % foo)
        if os.path.isfile(foo):
            f = file(foo, 'r')
            try:
                content = f.read()
            finally:
                f.close()
            return content
        else:
            raise OSError, "No such file:%s" % filepath

    def inputTransform(self, filepath, debug=False):
        '''Transform input file to html for consumption by pisa
        '''
        import tempfile
        (fd, tempfilepath) = tempfile.mkstemp()
        try:
            #close the open filehandle
            os.close(fd)
            syscall = ''.join(["java net.sf.saxon.Transform -s ",
                               filepath, " -o ",
                                tempfilepath, ' ',
                                self.xsltpath,
                               " doc.view=entire_text pdfgen=",
                               "debug" if debug else "normal"
                                #" #2> /dev/null"
                              ])
        
            logging.getLogger('OAC').info("Saxon call: %s" % (syscall))
            import subprocess
            print "+++++++SYSCALL:", syscall
            p = subprocess.Popen(syscall, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            #p = subprocess.Popen(syscall, shell=True, stdout=None,
            #                     stderr=None)
            sts = os.waitpid(p.pid, 0)
            print "STATUS", sts
            err = sts[1]
            logging.getLogger('OAC').info("Saxon call exit:%s" % (err))
            if err != 0:
                logging.getLogger('OAC').error("Error Msg: %s  ERRORCODE:%s :: cmd: %s" % (p.stderr.read(), err, syscall))
                #cleanup tempfile
                raise Exception
            f = open(tempfilepath,'rb')
            try:
                html = f.read()
            finally:
                f.close()
        finally:   
            try:
                os.remove(tempfilepath)
                if os.path.exists(tempfilepath):
                    os.remove(tempfilepath)
            except:
                print >> sys.stderr, "Exception from os.remove"
                raise
        return html

    def xml_to_pdf(self, filepath_in, outputdir, cssfile=CSSFILE, nohtml=False, savehtml=False, htmlonly=False, debug=False):
        '''Run saxon on xml with oac4_to_pdf.xslt to produce html suitable for 
        the pisa html to pdf library.
        '''
        #print "xml_to_pdf input:", filepath_in, outputdir, cssfile, nohtml, savehtml, debug
        dir, filename = os.path.split(filepath_in)
        fname, ext = os.path.splitext(filename)
        #filepath_in = os.path.join(dirname, name, '.xml')
        filepath_out = os.path.join(outputdir, fname)
        err = 0
        # create an instance of the PDFGenerator
        # feeding it inputTransform & PostProcessor class
        if nohtml:
            transform = self.nohtmlTransform
        else:
            transform = self.inputTransform

        pdfGen = PDFGenerator(inputTransform = transform, postProcessor = self.postProcessor, cssfile=cssfile, debug=debug )
        html, result_post  = pdfGen.generate(filepath_in, filepath_out+'.pdf', savehtml=savehtml, htmlpath=os.path.join(outputdir, fname+ext+'.html'), htmlonly=htmlonly)
        return html, result_post
    
    @staticmethod
    def input_is_newer(input_file, output_file):
        newer = True
        if os.path.exists(output_file):
            out_stat = os.stat(output_file)
            if out_stat.st_size != 0:
                if os.stat(input_file).st_mtime < out_stat.st_ctime:
                    newer = False
        return newer

    def pdf_gen_file(self, fname, cssfile=CSSFILE, timeoutSecs=None, outdir_option=None, data_root=None,
                     force=False, nohtml = False, savehtml = False, debug=False,
                    htmlonly=False):
        self.starttime = datetime.datetime.now()
        logging.getLogger('OAC').info('Running in file mode for file:%s cssfile:%s' % (fname, cssfile))
        if outdir_option is not None:
        	if (outdir_option.lower().find('parallel') != -1) and not data_root:
                        logging.error("To use parallel output dir in file mode, you must specify the data_root (--data_root=)")
                        raise OptionError
        return self.pdf_gen_list([fname], cssfile=cssfile, outdir_option=outdir_option,
                          data_root=data_root, nohtml=nohtml, savehtml=savehtml,
                          timeoutSecs=timeoutSecs, force=force, debug=debug,
                                htmlonly=htmlonly)
    
    def pdf_gen_list(self, flist, cssfile=CSSFILE, timeoutSecs=None,
                     outdir_option=None, data_root=None,
                     force=False, nohtml = False, savehtml = False, debug=False,
                    htmlonly=False):
        if outdir_option is not None:
            if (outdir_option.lower().find('parallel') != -1) and not data_root:
                logging.error("To use parallel output dir in list mode, you must specify the data_root (--data_root=)")
                raise OptionError
        completed = []
        timeouts = []
        errs = []
        skipped = []
        logger = logging.getLogger('OAC')
        self.starttime = datetime.datetime.now()
        if timeoutSecs and (int(timeoutSecs) != 0):
            convert_func = timeout.TimeoutFunction(self.xml_to_pdf, timeoutSecs)
        else:
            logging.warn("RUNNING WITH NO TIMEOUT")
            convert_func = self.xml_to_pdf
    
        cssfile_orig = cssfile
        for fname in flist:
            cssfile = cssfile_orig
            if OAC_EADtoPDFGenerator.isNot_DC_or_METS_XML(fname):
                #If pdf exists and is newer than xml, do nothing?
                # may want to make an opt for this behavior
                tStart = datetime.datetime.now()
                (dirname, name) = os.path.split(fname)
                (name, ext) = os.path.splitext(name)
                outputdir = self.outpath(outdir_option, data_root, dirname )
                outfilename = name+'.pdf'
                outfile_path = os.path.join(outputdir, outfilename)
                logger.info("FILE: %s%s started at %s outputdir:%s]" % (name,
                                                                ext,
                                                                tStart.strftime(STRFTIME),
                                                                         outputdir) )
                                                                         #ext,
                                                                         #tStart.strftime(STRFTIME),
                                                                         #outputdir) )
                # where i need to check file stamps if not force
                # need function outputdir to become outputfpath
                # and check filestamp of input xml file against output pdf file
                if force or self.input_is_newer(fname, outfile_path):
                    self.numfileattempt +=1
                    msg = ''
                    status = 'WORKING'
                    #Check for deja vu font compatibility

                    dejavu_compat = test_file_against_font_coverage(fname, 'dejavu')
                    if not dejavu_compat:
                        cssfile = u''.join((os.path.splitext(cssfile)[0],
                            "-unifont", os.path.splitext(cssfile)[1]))
                        logger.info("Using unifont for {0} -- css:{1}.".format(fname, cssfile))
                    try:
                        html, result_post = convert_func(fname,
                                     outputdir,
                                     cssfile = cssfile,
                                     nohtml=nohtml,
                                     savehtml=savehtml,
                                     htmlonly=htmlonly,
                                     debug = debug
                                    )
                        self.numfilecomplete +=1
                        completed.append((fname, outfile_path))
                        status = 'SUCCESS'
                        if (debug or savehtml or nohtml):
                            #Save html string as file
                            htmlfilepath = os.path.join(outputdir, (os.path.split(fname)[1]+'.html'))
                            logger.info("Saving html to file: " + htmlfilepath)
                            f = open(htmlfilepath, 'w')
                            try:
                                f.write(html)
                            finally:
                                f.close()
                    except timeout.TimeoutFunctionException:
                        status = 'TIMEOUT'
                        tFinish = datetime.datetime.now()
                        tDiff = tFinish - tStart
                        msg = "%s:: +++++TIMEOUT CONVERT FUNCTION TIMED OUT!----- Elapsed time:%s +++++ %s" % (status, tDiff, fname)
                        logger.log(TIMEOUT_LOG_LEVEL, msg)
                        self.numtimeouts += 1
                        timeouts.append(fname)
                    except :
                        self.numerrs += 1
                        errs.append(fname)
                        status = 'ERROR'
                        msg = "%s:: Unknown Exception caught for file- +++++ %s\n\n" % (status, fname)
                        logger.exception(msg)
                    # remove pdf is size is 0
                    if os.path.exists(outfile_path):
                        out_stat = os.stat(outfile_path)
                        if out_stat.st_size == 0:
                            os.remove(outfile_path)
                else:
                    status = 'SKIPPED'
                    skipped.append((fname, outfile_path))
                tFinish = datetime.datetime.now()
                tDiff = tFinish - tStart
                logger.info("[%s: IN FILE: %s -- OUTDIR:%s -- Elapsed time = %s]\n\n" %
                                  (status, fname, outputdir, tDiff))
                self.timer = self.timer + tDiff
                if self.timer.seconds > 0:
                    self.timer = datetime.timedelta(0)
                    if len(flist) > 1:
                        logger.info("CURRENT RUNNING TIME FOR LIST:%s" % (tFinish - self.starttime))
                if len(flist) > 1:
                    logger.info("ATTEMPTS: %d; SUCCESS:%d; ERR:%d; TIMEOUTS:%d" %
                                 (self.numfileattempt, self.numfilecomplete,
                                  self.numerrs, self.numtimeouts)
                            )
        return completed, timeouts, errs, skipped

    def pdf_gen_dirtree(self, dir, outdir, excludes=[], timeoutSecs=600,
                        force=False, exclude_dirs=[], savehtml=False,
                        nohtml=False, debug=False, cssfile=CSSFILE,
                        htmlonly=False):
        ''' Call list process on each dir
        '''
        self.starttime = datetime.datetime.now()
        logger = logging.getLogger('OAC')
        logger.info("EXCLUDE DIRS=%s" % (exclude_dirs))
        dir = os.path.abspath(dir)
        xml_files = []
        for root, dirs, files in os.walk(dir):
            logger.info("PROCESS DIRECTORY:%s" % os.path.abspath(root))
            if os.path.abspath(root) in exclude_dirs:
                logger.info("SKIP DIRECTORY:%s" % os.path.abspath(root))
                del dirs[:] #reassignment didn't work, must be in place mod
                continue
            for file in files:
                if OAC_EADtoPDFGenerator.isNot_DC_or_METS_XML(file):
                    fpath = os.path.join(root,file)
                    if fpath not in excludes:
                        xml_files.append(fpath)
        logger.info("Number of files to process:%d\n\n" % len(xml_files))
        (completed, timeouts, errors, skipped) = self.pdf_gen_list(xml_files,
                              timeoutSecs=timeoutSecs, outdir_option=outdir,
                              data_root=dir, force=force, savehtml=savehtml,
                              nohtml=nohtml, debug=debug, cssfile=cssfile,
                              htmlonly=htmlonly)
        return completed, timeouts, errors, skipped


################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
class PostProcessor_OACEAD(object):
    '''Make this a callable (input file(xml), output file)
    '''
    def __call__(self, filepathPDF, filepathXML):
        return self.post_process_pdf(filepathPDF, XMLfile=filepathXML)


    def parse_source_html_metadata(self, PDFfile):
        '''we know that html is produced next to the pdf!
        '''
        # get the html file name
        path, ext  = os.path.splitext(PDFfile)
        htmlFile = path + '.html'
        title = None
        try:
            f = open(htmlFile, 'r')
            try:
                html = f.read()
                #use beautifulsoup to parse the html source of the PDF.
                soup = BeautifulSoup(html)
                adminView = soup.find(name='div', attrs={'class':'collection-admin-view'})
                t = adminView.find(name='h1')
                if t:
                    title = adminView.find(name='h1').contents[0]
                if title:
                    title = title
            finally:
                f.close()
        except IOError:
            pass
    
        docInfo = dict(title=title)
        return docInfo
    
    def parse_source_xml_metadata(self, XMLfile):
        '''Parse the xml for any interesting doc info
        '''
        logger = logging.getLogger('OAC')
        retVal = None
        try:
            f = open(XMLfile, 'r')
            try:
                root_element = ET.parse(f)        
                logger.debug(root_element)
                # try Dublin Core Elements
                contributor = elementlist_tostring(root_element.findall('./contributor'))
                creator = elementlist_tostring(root_element.findall('.//creator'))
                c =root_element.find('./archdesc/did/origination')
                if c is not None:
                    creator = elementlist_tostring(root_element.find('./archdesc/did/origination').getchildren())
                date = elementlist_tostring(root_element.findall('./date'))
                description = elementlist_tostring(root_element.findall('./description'))
                format = elementlist_tostring(root_element.findall('./format'))
                identifier = elementlist_tostring(root_element.findall('./identifier'))
                language = elementlist_tostring(root_element.findall('./language'))
                publisher = elementlist_tostring(root_element.findall('./publisher'))
                source = elementlist_tostring(root_element.findall('./source'))
                subject = elementlist_tostring(root_element.findall('./archdesc/subject'))
                if subject=='':
                    subject = elementlist_tostring(root_element.findall('.//subject'))
                title = elementlist_tostring(root_element.findall('.//title'))
                type = elementlist_tostring(root_element.findall('./type'))
    
                title = elementlist_tostring(root_element.findall('./titleproper'))
                if title == '':
                    title = root_element.find('.//unittitle').text 
    
                author = creator
                
                logger.debug('A:%s, T:%s, S:%s' % (author, title, subject))
                retVal = dict(author=author, 
                              title=title,
                              subject=subject,
                             )
            finally:
                f.close()
        except IOError:
            logger.info("IOError: %s" % PDFfile)
        return retVal
    
    def modify_pdf(self, PDFfile, docInfo):
        ''' Do just some straight text replacement here
        We always replace at least the producer doc info.
        '''
        logger = logging.getLogger('OAC')
        logger.info("IN MODIFY PDF FOR : %s" % PDFfile)
        try:
            fin = fout = None
            fin = open(PDFfile, 'r')
            lines = fin.readlines()
            fin.close()
            try:
                hasOutline = False
                for idx, line in enumerate(lines):
                    if 'OutlineEntryObject' in line:
                        hasOutline = True
                        # change the following line with << /Count -XXXXX
                        # to << /Count XXXXX
                        # look for /Count -%d or endobj in lines[idx]-> endobj
                        prog = re.compile(r"/Count -(\d+)")
                        for jdx, line in enumerate(lines[idx:]):
                            if prog.search(line):
                                newline = prog.sub(r"/Count \1", line)
                                lines[idx+jdx] = newline
                                break
                            if 'endobj' in line:
                                break
                        break
    
                newlines = []
                for line in lines:
                    if line.find("/Producer") != -1:
                        newline = " /Producer (%s)\n" % docInfo.get('producer','')
                    else:
                        newline = line
    
                    newline = newline.replace("/Author ()","/Author (%s)" %
                                           unicode(docInfo.get('author','')).encode('UTF-8'))
                    newline = newline.replace("/Subject ()","/Subject (%s)" %
                                           unicode(docInfo.get('subject','')).encode('UTF-8'))
                    newline = newline.replace("/Title ()", "/Title (%s)" %
                                              unicode(docInfo.get('title','')).encode('UTF-8'))
                    if hasOutline:
                        newline = newline.replace("UseNone", "UseOutlines")
                    newlines.append(newline)
                logger.debug("WRITING:%s" % newlines)
                fout = open(PDFfile, 'w') # hammer file & write
                fout.writelines(newlines)
            finally:
                if fin:
                    fin.close()
                if fout:
                    fout.close()
        except IOError:
            logger.info("IOError: %s" % PDFfile)
    
    def post_process_pdf(self, PDFfile, XMLfile=None):
        '''Add some extra info to the generated pdf
        Try to get metadata for title, author & subject.
        '''
        docInfo = dict(author='', title='', subject='',
            producer='Online Archive of California'# '- California Digital Library'
                  )
    
        if XMLfile:
            xmlInfo =  self.parse_source_xml_metadata(XMLfile)
            docInfo['title'] = xmlInfo.get('title', docInfo['title'])
            docInfo['author'] = xmlInfo.get('author', docInfo['author'])
            docInfo['subject'] = xmlInfo.get('subject', docInfo['subject'])
        tmp = self.parse_source_html_metadata(PDFfile) # currently will only find title
        if tmp['title']:
            docInfo['title'] = tmp['title']
        # add the pisa Producer lis
        pisaTagline = ' - with pisa XHTML to PDF'# <http://www.xhtml2pdf.com>'
        docInfo['producer'] = docInfo['producer'] + pisaTagline
#        msg = 'docInfo title:%s author:%s producer:%s subject: %s' % (docInfo.get('title'),
#                                               docInfo.get('author'),
#                                               docInfo.get('producer'),
#                                               docInfo.get('subject')
#                                              )
#   
#        logging.getLogger('OAC').info("PDFfile=%s %s" % (PDFfile, msg))
        self.modify_pdf(PDFfile, docInfo)

################################################################################
################################################################################
################################################################################
################################################################################

def read_list_file(fname):
    f = file(fname)
    files = [line.rstrip() for line in f]
    f.close()
    logging.debug("filelist:%s" % str(files))
    return files

def read_exclude_dirs_file(fname):
    f = file(fname)
    exclude_dirs = [line.rstrip() for line in f]
    f.close()
    return exclude_dirs

def read_exclude_file(fname):
    f = file(fname)
    exclude_filenames = {}
    for line in f:
        exclude_filenames[line.rstrip()] = 'EXCLUDE'
    f.close()
    return exclude_filenames


def setup_logger():
    #log = logging.getLogger('OAC')
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    h = logging.handlers.RotatingFileHandler(info.logprefix+'.log', backupCount=LOG_BACKUP_COUNT )
    h.setLevel(LOG_LEVEL)
    format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    h = logging.handlers.RotatingFileHandler(info.logprefix+'.err', backupCount=LOG_BACKUP_COUNT )
    h.setLevel(logging.ERROR)
    format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    h = logging.handlers.RotatingFileHandler(info.logprefix+'.timeouts', backupCount=LOG_BACKUP_COUNT )
    h.setLevel(TIMEOUT_LOG_LEVEL)
    format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    return log

def process_args(args_cmd, info):
    """Uses optparse.OptionsParser to get options. Stuffs values into the info
    Bunch object.
    """
    usage = "%prog (-fFILE or -dDIR or -lLIST_FILE) [options]"
    arg_parser = OptionParser(usage=usage, description=description)
    arg_parser.add_option("-d", "--dir", dest="dir",
                      help="Recurse from directory <DIR> and create pdfs for all xml files in subtree.")
    arg_parser.add_option("-f", "--file", dest="file",
                      help="Generate PDF for filename <FILE>")
    arg_parser.add_option("-l", "--list", dest="list",
                      help="Generate PDFs for filenames in file <LIST>")
    arg_parser.add_option("-x", "--exclude", dest="exclude",
                      help="Exclude files listed in file <EXCLUDE>")
    arg_parser.add_option("-p", "--logprefix", dest="logprefix",
                      help="Use <LOGPREFIX> for log file names.")
    arg_parser.add_option("-o", "--outdir", dest="outdir",
                          help=""" parallel=/abs/dir - produce output in parallele directory structure, with root of /abs/dir
subdir=name - produce output in subdir "name"
outdir=/abs/dir - put all pdf files in /abs/dir.
If not set, pdf will be created in same directory as source file.
                          """
                         )
    arg_parser.add_option("--data_root", dest="data_root",
                          help="""Use when in list or file mode and want to produce data in a parallel directory. Points to root of data tree. Parallel output will replace this root with the parallel directory root"""
                         )
    arg_parser.add_option("--css", dest="css",
                      help="Use css styling for PDF in <FILE>",
                         default=CSSFILE
                         )
    arg_parser.add_option("--xslt", dest="xslt",
                      help="Use this xsl stylesheet to transfor EAD xml",
                         default=XSLTFILE
                         )
    arg_parser.add_option("--force", dest="force", action="store_true",
                          help="Force regeneration of existing pdf files")
    arg_parser.add_option("--exclude_dirs", dest="exclude_dirs",
                          help="Exclude directories listed in file <EXCLUDE_DIRS>")
    arg_parser.add_option("-t", "--timeout", dest="timeout",
                          help="Set <TIMEOUT> in seconds. Default=%s" % TIMEOUT_CONVERT )
    arg_parser.add_option("--debug", action="store_true", dest="debug",
                      default=False, help="Run in debug mode")
    arg_parser.add_option("--savehtml", action="store_true", dest="savehtml",
                      default=False, help="Save intermediate html files")
    arg_parser.add_option("--htmlonly", action="store_true", dest="htmlonly",
                      default=False, help="Generate intermediate html files, save them and exit before creating pdf")
    arg_parser.add_option("--nohtml", action="store_true", dest="nohtml",
                      default=False,
                      help="Do not generate html files, use existing files.")
    (options, args) = arg_parser.parse_args(args_cmd)

    info.dir = options.dir
    info.file = options.file
    info.list = options.list
    if (info.dir and (info.list or info.file)) or (info.file and info.list):
        arg_parser.error("Only one of -d (--dir), -l (--list), or -f (--file) can be set")
    if not (info.dir or info.list or info.file):
        arg_parser.error("One of -d (--dir), -l (--list), or -f (--file) must be set.")
    if info.dir:
        info.mode = 'dir'
    elif info.list:
        info.mode = 'list'
    else:
        info.mode = 'file'
    info.exclude =  options.exclude
    info.logprefix = options.logprefix
    if not info.logprefix:
        info.logprefix = LOG_FILE_PREFIX
    info.outdir = options.outdir
    info.data_root = options.data_root
    if options.outdir != None:
        if (options.outdir.lower().find('parallel') != -1 and (info.list or info.file)):
            if not options.data_root:
                arg_parser.error("To use parallel output dir in list or file mode, you must specify the data_root (--data_root=)")
    if os.path.isfile(options.css):
        info.css = options.css
    else:
        info.css = os.path.join(PATH_TO_PROGS, options.css)
    if os.path.isfile(options.xslt):
        info.xslt = options.xslt
    else:
        info.xslt = os.path.join(PATH_TO_PROGS, options.xslt)
    info.force = options.force
    info.exclude_dirs = options.exclude_dirs
    info.debug = options.debug
    info.savehtml = options.savehtml
    info.htmlonly = options.htmlonly
    info.nohtml = options.nohtml

    info.timeout = options.timeout
    if not info.timeout:
        info.timeout = TIMEOUT_CONVERT
    else:
        info.timeout = int(info.timeout)
    return info

def main(args):
    global log
    info.numfileattempt = 0
    info.numfilecomplete = 0
    info.numerrs = 0
    info.numtimeouts = 0
    process_args(args, info)
    logger = setup_logger()
    info.starttime = datetime.datetime.now()
    info.timer = datetime.timedelta(0)
    logger.info("Starting at %s" % info.starttime.strftime(STRFTIME))
    logger.info("Process id: %s" % os.getpid())
    logger.info("Mode = %s" % (info.mode))
    logger.info("Outdir = %s" % (info.outdir))
    logger.info("Timeout in secs = %s" % (info.timeout))
    logger.info("Force = %s" % (info.force))
    logger.info("Save html  = %s" % info.savehtml)
    logger.info("No html  = %s" % info.nohtml)
    logger.info("CSS File = %s" % info.css)
    logger.info("XSLT File = %s\n\n\n" % info.xslt)
    excludes = []
    if info.exclude:
        excludes = read_exclude_file(info.exclude)
    logger.info("EXCLUDE FILES=%s" % (excludes))
    #create Processor & call appropriate function
    pdfGenerator = OAC_EADtoPDFGenerator(info.xslt)
    completed = []
    timeouts = []
    errors = []
    skipped = []
    if info.mode == 'dir':
        exclude_dirs = []
        if info.exclude_dirs:
            exclude_dirs = read_exclude_dirs_file(info.exclude_dirs)
        (completed, timeouts, errors, skipped) = pdfGenerator.pdf_gen_dirtree(info.dir, info.outdir,
            excludes=excludes, cssfile=info.css,
            timeoutSecs=info.timeout, force=info.force, debug=info.debug,
            exclude_dirs=exclude_dirs, savehtml=info.savehtml, nohtml=info.nohtml,
            htmlonly=info.htmlonly)
    elif info.mode == 'list':
        file_list = read_list_file(info.list)
        (completed, timeouts, errors, skipped)  = pdfGenerator.pdf_gen_list(file_list,
            cssfile=info.css, timeoutSecs=info.timeout,
            outdir_option=info.outdir, data_root=info.data_root,
            nohtml=info.nohtml, savehtml=info.savehtml, force=info.force,
            debug=info.debug, htmlonly=info.htmlonly)
    else:
        (completed, timeouts, errors, skipped) = pdfGenerator.pdf_gen_file(info.file,
            cssfile=info.css, timeoutSecs=info.timeout,
            outdir_option=info.outdir, data_root=info.data_root,
            nohtml=info.nohtml, savehtml=info.savehtml, force=info.force,
            debug=info.debug, htmlonly=info.htmlonly)
    tFinish = datetime.datetime.now()
    logger.info("\n\n\n\nFinished at %s" % tFinish.strftime(STRFTIME))
    tDiff = tFinish - info.starttime
    logger.info("Elapsed time: %s" % tDiff)
    attempted = len(completed) + len(timeouts) + len(errors) + len(skipped)
    logger.info("Number files attempted: %d" % attempted)
    logger.info("Number files completed: %d" % len(completed))
    logger.info("Number errs: %d" % len(errors))
    logger.info("Number timeouts: %d" % len(timeouts))
    logger.info("Number skipped: %d" % len(skipped))


if __name__ == "__main__":
    main(sys.argv)
