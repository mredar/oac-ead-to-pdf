# Author: Mark Redar <mark.redar@ucop.edu>
# Copyright: See LICENSE.txt
#<!-- BSD license copyright 2009 -->

import os, sys
import datetime
import logging
from optparse import OptionParser

import pdf_gen
#from pdf_gen import OAC_EADtoPDFGenerator as PDFGen
#from pdf_gen import Bunch

FILESIZE = 2**13 #8K
FILESIZE_MAX = 2**27 # ~100M
LOG_BACKUP_COUNT = 10
LOG_LEVEL = logging.INFO
TIMEOUT_LOG_LEVEL = 90
TIMEOUT_SECS_START = 2**5 #32

global info
info = pdf_gen.Bunch(numtimeouts = 0,
             numerrs = 0,
             numfileattempt = 0,
             numfilecomplete = 0,
             timer = datetime.timedelta(0),
             starttime = datetime.datetime.now(),
             nohtml = False,
             savehtml = False,
             debug=False,
             timeout_start = TIMEOUT_SECS_START,
             css = pdf_gen.CSSFILE,
             path_to_exe = pdf_gen.PATH_TO_PROGS,
             xslt=pdf_gen.XSLTFILE,
            )

logging.info("PATH_TO_PROGS: ", os.environ.get("PATH_TO_PROGS"))
description = '''
PDF Run by size: Runs the OAC EAD xml files through our PDF Generaotor. Runs
them by increasing size.
'''

def process_args(args_os):
    """Uses optparse.OptionsParser to get options. Stuffs values into the info
    Bunch object.
    """
    usage = "%prog --dir DIR [options]"
    arg_parser = OptionParser(usage=usage, description=description)
    arg_parser.add_option("-d", "--dir", dest="dir",
                      help="Recurse from directory <DIR> and create pdfs for all xml files in subtree.")
    arg_parser.add_option("-p", "--logprefix", dest="logprefix",
                      help="Use <LOGPREFIX> for log file names.")
    arg_parser.add_option("-o", "--outdir", dest="outdir",
                          help=""" parallel=/abs/dir - produce output in parallele directory structure, with root of /abs/dir
subdir=name - produce output in subdir "name"
outdir=/abs/dir - put all pdf files in /abs/dir
                          """
                         )
    arg_parser.add_option("--force", dest="force", action="store_true",
                          help="Force regeneration of existing pdf files")
    arg_parser.add_option("-t", "--timeout", dest="timeout",
                          help="Set <TIMEOUT> in seconds to start run at. Default=%s" %
                          info.timeout_start)
    arg_parser.add_option("--debug", action="store_true", dest="debug",
                      default=False, help="Run in debug mode")
    arg_parser.add_option("--savehtml", action="store_true", dest="savehtml",
                      default=False, help="Save intermediate html files")
    arg_parser.add_option("--nohtml", action="store_true", dest="nohtml",
                      default=False,
                      help="Do not generate html files, use existing files.")
    (options, args) = arg_parser.parse_args(args_os)

    if not options.dir:
        arg_parser.error("-d (--dir) must be set.")

    if options.outdir:
        if options.outdir.lower().find('parallel=') == -1:
	    #build parallel path 
            root_dir, drop = os.path.split(options.dir)
            if not drop:
                root_dir, drop = os.path.split(root_dir)
	    options.outdir = options.outdir.lower() + '=' + os.path.join(root_dir, 'pdf')
	
    return options

def setup_logger(logprefix='pdf_by_size'):
    log = logging.getLogger('OAC')
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    h = logging.handlers.RotatingFileHandler(logprefix+'.log', backupCount=LOG_BACKUP_COUNT )
    h.setLevel(LOG_LEVEL)
    format = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    h = logging.handlers.RotatingFileHandler(logprefix+'.err', backupCount=LOG_BACKUP_COUNT )
    h.setLevel(logging.ERROR)
    format = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    h = logging.handlers.RotatingFileHandler(logprefix+'.timeouts', backupCount=LOG_BACKUP_COUNT )
    h.setLevel(TIMEOUT_LOG_LEVEL)
    format = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    return log

def main(args):
    #setup our processor
    options = process_args(args)
    logprefix = options.logprefix if options.logprefix is not None else 'pdf_gen_by_size'
    LOGGER = setup_logger(logprefix=logprefix)
    LOGGER.info("Process id: %s" % os.getpid())
    generator = pdf_gen.OAC_EADtoPDFGenerator(os.path.join(info.path_to_exe,
                                                           info.xslt
                                                          )
                                             )
    filelist = []
    errorlist = []
    filesize_cur = FILESIZE
    filesize_last = 0

    timeout_cur = 0
    if options.timeout:
       timeout_cur = int(options.timeout)
    else:
        timeout_cur += info.timeout_start
    
    LOGGER.info("Force:%s" % options.force)
    LOGGER.info("savehtml:%s" % options.savehtml)
    LOGGER.info("nohtml: %s" % options.nohtml)
    LOGGER.info("outdir:%s" % options.outdir)
    timeouts_last_iter = []
    while (filesize_cur < FILESIZE_MAX):
        for root, dirs, files in os.walk(options.dir):
            for f in files:
                if generator.canGeneratePDF(f):
                    path = os.path.join(root, f)
                    if filesize_last < os.stat(path).st_size <= filesize_cur:
                        #LOGGER.info(path, os.stat(path).st_size)
                        filelist.append(path)
        filelist.extend(timeouts_last_iter)
        LOGGER.info("For %d  < size <= %d, %d files, %d are previous timeouts to process, TimeOut in seconds:%d" % (filesize_last,
                                               filesize_cur,
                                               len(filelist),
                                               len(timeouts_last_iter),
                                               timeout_cur
                                              )
                    )
        complete, timeouts, errs, skips = generator.pdf_gen_list(filelist,
                                                timeoutSecs=timeout_cur,
                                                outdir_option = options.outdir,
                                                data_root=options.dir,
                                                force = options.force,
                                                nohtml=options.nohtml,
                                                savehtml=options.savehtml,
						debug=options.debug
						)
        errorlist.extend(errs)
        LOGGER.info("RUNNING TIME: %s" % (datetime.datetime.now()-info.starttime))
        LOGGER.info("Attempts:%d Complete:%d Timeouts:%d Errs:%d TimeOut seconds:%d" % (len(filelist),
                                                                len(complete),
                                                                len(timeouts),
                                                                len(errs),
                                                                timeout_cur
                                                              )

                    )
        #if you get timeouts, add to file list next time
        timeouts_last_iter = timeouts
        if len(timeouts) > 0:
            timeout_cur = timeout_cur*2
        filesize_last = filesize_cur
        filesize_cur = filesize_cur*2
        filelist = []
        LOGGER.info("\n++++++++++++++++++++++++++++++++++++++\n")

    LOGGER.info("TOTAL RUNNING TIME: %s" % (datetime.datetime.now()-info.starttime))
    LOGGER.info("FINAL Attempts:%d Complete:%d Timeouts:%d Errs:%d" % (generator.numfileattempt,
                                                           generator.numfilecomplete,
                                                           generator.numtimeouts,
                                                           generator.numerrs
                                                          )
                )
    LOGGER.info("TIMEOUT LIST:")
    LOGGER.info(timeouts)
    LOGGER.info("ERROR LIST:")
    LOGGER.info(errorlist)

if __name__=='__main__':
    main(sys.argv)
