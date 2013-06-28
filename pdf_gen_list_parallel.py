import os, sys
import logging
import datetime

import pdf_gen
import pp
import plac

LOG_BACKUP_COUNT = 10
LOG_LEVEL = logging.INFO
TIMEOUT_DEFAULT = 2**3
TIMEOUT_LOG_LEVEL = 90
TIMEOUT_DEFAULT = 2**3
CSSFILE = os.path.join(os.environ.get('PATH_TO_PROGS', '.'), "oac_pdf.css")

def pdf_gen_wrap(filename, num, timeout=None, cssfile='/dsc/branches/production/oac-ead-to-pdf/oac_pdf.css', force=False, savehtml=False, outdir=None, data_root=None, logprefix='run_pdf_gen_parallel'):
    '''Wrapper for pdf_gen.generator.pdf_gen_file for call from pp'''
    #setup logging for each file
    logfile =logprefix+'-WORKER-'+str(num)+'.log'
    #TODO -- THE LOG FILES KEEP APPENDING, ALSO NO DATETIME IN LOG
    logging.basicConfig(filename=logfile, level=logging.INFO)
    generator = pdf_gen.OAC_EADtoPDFGenerator(os.path.join(pdf_gen.PATH_TO_PROGS, pdf_gen.XSLTFILE))
    complete, timeouts, errs, skips = generator.pdf_gen_file(filename, timeoutSecs=timeout, cssfile=cssfile, force=force, savehtml=savehtml, outdir_option=outdir, data_root=data_root)
    return complete, timeouts, errs, skips

def run_file_list_with_pp(filelist, ncpu=None, timeout=None, cssfile=CSSFILE, force=False, savehtml=False, outdir=None, data_root=None, logprefix='run_pdf_gen_parallel'):
    # only input is list file, parse and feed to ppserver
    #better run this in nice mode.
    #job_server = pp.Server(restart=True, loglevel=logging.INFO, logstream=jobslog) 
    logging.info("======= Enter run_list_with_pp =======")
    if len(filelist)==0:
        return [], [], [], []
    job_server = None
    #use 1/2 of the processors
    if not ncpu:
        job_server = pp.Server()
        ncpu = job_server.get_ncpus()
        ncpu = divmod(ncpu,2)[0]
    else:
        ncpu=int(ncpu)
        job_server = pp.Server(ncpus=ncpu)
    job_server.set_ncpus(ncpus=ncpu)
    msg = "RESET PP with "+str(ncpu)+" workers timeout="+str(timeout)
    logging.info(msg) 
    jobs = []
    for filename in filelist:
        jobs.append(job_server.submit(pdf_gen_wrap, args=(filename, len(jobs), timeout, cssfile, force, savehtml, outdir, data_root, logprefix), modules=('pdf_gen', 'logging', 'os')))
        #jobs.append(job_server.submit(pdf_gen_wrap, args=(filename, len(jobs), timeout, cssfile, force, savehtml, outdir, data_root, logprefix), modules=('pdf_gen', 'logging', 'os.path')))
    
    completed = []
    timeouts = []
    errs = []
    skipped = []
    job_server.wait()
    for job in jobs:
        c, to, e, skip = job()
        completed.extend(c)
        timeouts.extend(to)
        errs.extend(e)
        skipped.extend(skip)

    logging.info('JOBS SUBMITTED: %d' % (len(jobs)))
    logging.info(''.join(["COMPLETED:", str(len(completed)), ' ::FILES:: ',  str(completed)]))
    logging.info(''.join(["TIMEOUTS:", str(len(timeouts)), ' ::FILES:: ',  str(timeouts)]))
    logging.info(''.join(["ERRORS:", str(len(errs)), ' ::FILES:: ',  str(errs)]))
    logging.info(''.join(["SKIPPED:", str(len(skipped)), ' ::FILES:: ',  str(skipped)]))
    stats = job_server.get_stats().get('local')
    #job_server.print_stats()
    msg = str(stats.njobs) + ' jobs took ' + str(stats.time) + ' on ' + str(stats.ncpus) + ' cpus.' 
    logging.info(msg)
    # rworker is none for local? logging.info('RWORKER:'+str(stats.rworker))
    job_server.destroy() #NOTE: THIS IS IMPORTANT, other wise the previous idle processes hang around...
    logging.info("======= Exiting run_list_with_pp =======")
    return completed, timeouts, errs, skipped

#plac likes function annotations
@plac.annotations(
    list_file=("File with list of filepaths to convert", 'positional'),
    ncpu=("Number of cpus to run on (defaults to 1/2 of available", 'option'),
    timeout=("Timeout for files", 'option', 't'),
    cssfile=("CSS file", 'option'),
    force=("Overwrite existing pdf", 'flag'),
    savehtml=('Save intermediate html files', 'flag'),
    outdir=('parallel=/abs/dir - produce output in parallel directory structure, with root of /abs/dir subdir=name - produce output in subdir "name" outdir=/abs/dir - put all pdf files in /abs/dir. If not set, pdf will be created in same directory as source file.', 'option', 'o'),
    data_root=('Use when in list or file mode and want to produce data in a parallel directory. Points to root of data tree.  Parallel output will replace this root with the parallel directory root.', 'option'),
    logprefix=('Use <LOGPREFIX> for log file names.', 'option'),
)
def main(list_file, ncpu=None, timeout=None, cssfile=CSSFILE, force=False, savehtml=False, outdir=None, data_root=None, logprefix='run_pdf_gen_parallel'):
    logprefix = ''.join((logprefix, '-', str(datetime.datetime.now().strftime("%Y%m%d-%H%M"))))
    logfile = ''.join((logprefix,'.log'))
    timeout=int(timeout) if timeout else TIMEOUT_DEFAULT
    #jobslog = open('pdf_list_parallel-JOBS.log','a')
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logging.info("Process id: %s" % os.getpid())
    filelist = [line[:-1] for line in open(list_file)]
    completed, timeouts, errs, skipped = run_file_list_with_pp(filelist, ncpu=ncpu, timeout=timeout, cssfile=cssfile, force=force, savehtml=savehtml, outdir=outdir, data_root=data_root, logprefix=logprefix)
    logging.shutdown()

if __name__=='__main__':
    import plac; plac.call(main)
