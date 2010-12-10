# Author: Mark Redar <mark.redar@ucop.edu>
# Copyright: This module has been placed in the public domain.

description = """
Runs pdf_gen with geometrically increasing timeout settings in an attempt
to generate all valid pdfs. Emails error log to --notify and then attempts
to run timeouts from last time.

"""

__docformat__ = 'restructuredtext'

import sys
print sys.path
import os
import datetime
from optparse import OptionParser
import pdf_gen # will run main fn in this module

TIMEOUT = 600
TIMEOUT_LIMIT = 345600 # 96 hrs

try:
    LOG_FILE_PREFIX = pdf_gen.LOG_FILE_PREFIX
except AttributeError:
    LOG_FILE_PREFIX = 'pdf_runner'

try:
    PATH_TO_PROGS = pdf_gen.PATH_TO_PROGS 
except AttributeError:
    PATH_TO_PROGS = os.environ.get("PATH_TO_PROGS",
                            '/dsc/branches/production/oac-ead-to-pdf/')

try:
    XSLTFILE = pdf_gen.XSLTFILE 
except AttributeError:
    XSLTFILE = "oac4_to_pdf.xslt"

try:
    CSSFILE = pdf_gen.CSSFILE 
except AttributeError:
    CSSFILE = "oac_pdf.css"

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

def run_pdfs(args, timeout):
    pass

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
outdir=/abs/dir - put all pdf files in /abs/dir
                          """
                         )
    arg_parser.add_option("--css", dest="css",
                      help="Use css styling in <FILE>",
                         default=os.path.join(PATH_TO_PROGS, CSSFILE)
                         )
    #    arg_parser.add_option("--force", dest="force", action="store_true",
    #                          help="Force regeneration of existing pdf files")
    arg_parser.add_option("--exclude_dirs", dest="exclude_dirs",
                          help="Exclude directories listed in file <EXCLUDE_DIRS>")
    #    arg_parser.add_option("-t", "--timeout", dest="timeout",
    #                          help="Set <TIMEOUT> in seconds. Default=%s" % TIMEOUT_CONVERT )
    arg_parser.add_option("--debug", action="store_true", dest="debug",
                      default=False, help="Run in debug mode")
    arg_parser.add_option("--savehtml", action="store_true", dest="savehtml",
                      default=False, help="Save intermediate html files")
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
    info.css = options.css
    info.force = False
    info.exclude_dirs = options.exclude_dirs
    info.debug = options.debug
    info.savehtml = options.savehtml
    info.nohtml = options.nohtml

#    info.timeout = options.timeout
#    if not info.timeout:
#        info.timeout = 0
#    else:
#        info.timeout = int(info.timeout)

    return info

def email_results(timeout):
    # email error log
    subject = "pdf_runner results"
    # is there a way to query global lob object for err log?
    errFile = ''.join([info.logprefix, '.err'])
    f = open(errFile)
    errors = f.read()
    f.close()
    logFile = ''.join([info.logprefix, '.log'])
    f = open(logFile)
    logcontent = f.readlines()
    f.close()
    msg = "PDF RUNNER: TIMEOUT = %d\n" % timeout
    msg += ''.join(logcontent[-6:])
    print msg
    msg += "ERRORS:\n-----\n"
    msg += errors
    msg += "\n------\nEND ERRORS\n"
    print msg
    try:
         import smtplib
         server = 'localhost'
         port=587
         sender='mark.redar@ucop.edu'
         senderPSWD=''
         to='mark.redar@ucop.edu'
         mailMsgText= "From:" + sender + "\nTo:" + to + "\nSubject:" + subject + "\n\n" + msg + "\n\n"
         # email report to list
         server=smtplib.SMTP(server) #,port)
         ehlo=server.ehlo()
         #sttls=server.starttls()
         #login=server.login(sender,senderPSWD)
         refused = server.sendmail(sender,to,mailMsgText)
         print refused
         server.quit()
    except:
        raise
    #   if __debug__:
    #       logging.debug("SMTP PROBLEM")
    #       logging.debug(sys.exc_info()[0])
    #       print "SMTP PROBLEM"
    #       print "SYSTEM ERR:="
    #       print "Unexpected error:",
    #       sys.exc_info()[0]
    #       raise

def main(args):
    process_args(args, info)
    timeout_cur = TIMEOUT
    print timeout_cur
    print args
    while (timeout_cur < TIMEOUT_LIMIT):
        #pdf_gen.main(args)
        email_results(timeout_cur)
        # parse out timeout file for file names
        # and prep next list
        # usually starts with dir or file directive
        timeoutFile = ''.join([info.logprefix, '.timeouts'])
        f = open(timeoutFile)
        timeouts = f.readlines()
        f.close()
        print timeouts

        for i, arg in enumerate(args):
            if arg == '--file':
                args = args[:i] + args[i+2:]
            if arg == '--dir':
                args = args[:i] + args[i+2:]
            if arg == '--list':
                args = args[:i] + args[i+2:]

        args.append('--list')
        args.append('alist.tmp')

        # double timeout_cur
        # set args to reflect update 
        timeout_cur = timeout_cur * 2
        print timeout_cur
        args.append('--timeout')
        args.append(timeout_cur)

    print args
    print dir(args)

    if '--file' in args:
        print 'FILE'


if __name__=='__main__':
    main(sys.argv)
