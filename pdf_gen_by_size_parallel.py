import os, sys
import logging
import datetime

from pdf_gen_list_parallel import run_file_list_with_pp
from pdf_gen import OAC_EADtoPDFGenerator
import plac

FILESIZE = 2**13 #8K
FILESIZE_MAX = 2**27 # ~100M
LOG_BACKUP_COUNT = 10
LOG_LEVEL = logging.INFO
TIMEOUT_LOG_LEVEL = 90
TIMEOUT_SECS_START = 2**5 #32
CSSFILE = os.path.join(os.environ.get('PATH_TO_PROGS', '.'), "oac_pdf.css")

description = '''
PDF Run by size: Runs the OAC EAD xml files through our PDF Generaotor. Runs
them by increasing size.
'''

def pdf_gen_by_size_parallel(directory_root, ncpu=None, timeout=600, cssfile=CSSFILE, force=False, savehtml=False, outdir=None, logprefix='run_pdf_gen_parallel', exclude_file=None):
    num_attempt = 0
    filelist = []
    successlist = []
    timeoutlist = []
    errorlist = []
    excludelist = [ line.strip() for line in open(exclude_file).readlines()] if exclude_file else []
    filesize_cur = FILESIZE
    filesize_last = 0
    timeout_cur = 0
    if timeout:
       timeout_cur = int(timeout)
    else:
        timeout_cur += TIMEOUT_SECS_START
    timeouts_last_iter = []
    start_time = datetime.datetime.now()
    while (filesize_cur < FILESIZE_MAX):
        for root, dirs, files in os.walk(directory_root):
            for f in files:
                if OAC_EADtoPDFGenerator.isNot_DC_or_METS_XML(f):
                    path = os.path.abspath(os.path.join(root, f))
                    if path in excludelist:
                        logging.info("EXCLUDING FILE:"+path)
                        continue
                    if filesize_last < os.stat(path).st_size <= filesize_cur:
                        filelist.append(path)
        num_attempt += len(filelist)
        filelist.extend(timeouts_last_iter)
        logging.info("++++++++++++++ For %d  < size <= %d, %d files to process, %d are previous timeouts to process, TimeOut in seconds:%d ++++++++++++++" % (filesize_last,
                                               filesize_cur,
                                               len(filelist),
                                               len(timeouts_last_iter),
                                               timeout_cur
                                              )
                    )
        completed, timeouts, errs, skipped = run_file_list_with_pp(filelist, ncpu=ncpu, timeout=timeout_cur, cssfile=cssfile, force=force, savehtml=savehtml, outdir=outdir, data_root=directory_root, logprefix=logprefix)
        successlist.extend(completed)
        errorlist.extend(errs)
        logging.info("++++++++++++++ RUNNING TIME: %s" % (datetime.datetime.now()-start_time))
        logging.info("++++++++++++++ Attempts:%d Complete:%d Timeouts:%d Errs:%d TimeOut seconds:%d" % (len(filelist),
                                                                len(completed),
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
        logging.info("\n++++++++++++++++++++++++++++++++++++++\n")
    return num_attempt, successlist, timeoutlist, errorlist, timeout_cur

@plac.annotations(
    directory_root=("Root directory for EAD files", 'positional'),
    ncpu=("Number of cpus to run on (defaults to 1/2 of available", 'option'),
    timeout=("Timeout for files", 'option', 't'),
    cssfile=("CSS file", 'option'),
    force=("Overwrite existing pdf", 'flag'),
    savehtml=('Save intermediate html files', 'flag'),
    outdir=('parallel=/abs/dir - produce output in parallel directory structure, with root of /abs/dir subdir=name - produce output in subdir "name" outdir=/abs/dir - put all pdf files in /abs/dir. If not set, pdf will be created in same directory as source file.', 'option'),
    #data_root=('Use when in list or file mode and want to produce data in a parallel directory. Points to root of data tree.  Parallel output will replace this root with the parallel directory root.', 'option'),
    logprefix=('Use <LOGPREFIX> for log file names.', 'option'),
    exclude_file=('List of files to be excluded (absolute path).', 'option'),
)

def main(directory_root, ncpu=None, timeout=600, cssfile=CSSFILE, force=False, savehtml=False, outdir=None, logprefix='run_pdf_gen_parallel', exclude_file=None):
    logprefix = ''.join((logprefix, '-', str(datetime.date.today())))
    logfile = ''.join((logprefix,'.log'))
    timeout=int(timeout)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logging.info("\n\n\n++++++++++++++ Process id: %s at %s ++++++++++++++" % (os.getpid(), datetime.datetime.now()))
    # build file lists according to size, how to report progress?
    

    num_attempt, successlist, timeoutlist, errorlist, timeout_end_of_run = pdf_gen_by_size_parallel(directory_root, ncpu=ncpu, timeout=timeout, cssfile=cssfile, force=force, savehtml=savehtml, outdir=outdir, logprefix=logprefix, exclude_file=exclude_file)


    report(num_attempt, successlist, errorlist, timeoutlist, timeout_end_of_run)
    logging.shutdown()

def report(num_attempt, successlist, errorlist, timeouts, timeout_end_of_run):
    logging.info("\n\n++++++++++++++++++++++++++++++++++++++\n\n")
    logging.info('COMPLETED FILES:'+str(successlist))
    logging.info('ERROR FILES:'+str(errorlist))
    logging.info('TIMEOUTS LEFT TO DO:'+str(timeouts))
    logging.info("\n\n++++++++++++++++++++++++++++++++++++++\n\n")
    logging.info("Completed %d files of %d attempts. %d had errors, while %d timed out with timeout of %d seconds." % ( len(successlist), num_attempt, len(errorlist), len(timeouts), timeout_end_of_run))

if __name__=='__main__':
    import plac; plac.call(main)
