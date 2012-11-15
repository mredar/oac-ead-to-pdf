'''
This program is a wrapper for the pdf_gen OAC_EADtoPDFGenerator and is called by process.cgi when a contributor submits an ead finding aid.

It first attempts to generate the PDF with a 64 second timeout. If this succeeds, it returns a HTML formatted success message which is put into the report file by process.cgi.
If it fails, it returns an error message to process.cgi.

If this first attempt times out, this forks. The parent returns a HTML formatted message stating that the generation is continuing. The forked child attempts to generate a PDF with no timeout set. After the attempt is over, it emails results to the user & oacops and modifies the report file....
 
'''
import os, sys
import datetime
import logging
import StringIO
import tempfile
from BeautifulSoup import BeautifulSoup

import pdf_gen

def msg_header():
    return '\n<div id="pdf_results"><h2>PDF Generation Results</h2>\n'
def msg_footer():
    return '\n</div>\n'

def msg_success_html(completed):
    ''' Return a nicely formatted success message for the completed file.
    HTML format.
    '''
    msg = msg_header()
    msg += '<h3>PDF Created</h3>PDF created for finding aid.' 
    msg += ' ' + str(completed[0])
    msg += msg_footer()
    return msg

def msg_skipped_html(skipped):
    ''' Return a nicely formatted success message for the completed file.
    HTML format.
    '''
    msg = msg_header()
    msg += '<h3>PDF Creation Skipped</h3>.' 
    msg += ' ' + str(skipped[0])
    msg += msg_footer()
    return msg

def msg_error_html(errors, useremail, errorLog):
    msg = msg_header()
    msg += ''.join(['<h3><font color=indianred>PDF Generation Errors</font></h3>There were problems with the generation of the PDF from your xml ead finding aid. OAC operations has been notified and should contact you at: ',
              useremail,
              '<div>',
              unicode(errors),
              '</div><div>',
              unicode(errorLog)
              ]
          )
    msg += msg_footer()
    return msg

def msg_timeout_html(timeouts, useremail):
    ''' Return a nicely formatted success message for the completed file.
    HTML format.
    '''
    msg = msg_header()
    msg += '<h3>PDF Generation Timed Out</h3>The generation of a pdf from the finding aid took longer than expected. OAC operations has been notified and the file has been restarted for pdf generation. You will recieve an email at: ' + useremail + ' when pdf processing is completed.'
    msg += msg_footer()
    return msg

def get_status(completed, timeouts, errors, skipped, useremail, errorLog):
    ''' Returns status code of OK, ERROR or TIMEOUT
    '''
    status = 'ERROR'
    if len(completed) > 0:
        status = 'OK'
    elif  len(skipped) > 0:
        status = 'SKIPPED'
    elif len(timeouts) > 0:
        status = 'TIMEOUT'
    return status

def msg_results_html(completed, timeouts, errors, skipped, useremail, errorLog):
    ''' Return appropriate message for result
    '''
    msg = 'Unknown status for pdf generation'
    status = get_status(completed, timeouts, errors, skipped, useremail, errorLog)
    if status == 'OK':
        msg = msg_success_html(completed)
    elif status == 'SKIPPED':
        msg = msg_skipped_html(skipped)
    elif status == 'ERROR':
        msg = msg_error_html(errors, useremail, errorLog)
    elif status == 'TIMEOUT':
        msg = msg_timeout_html(timeouts, useremail)
    return msg
    
def modify_results_file(resultsfile, inputfile, completed, timeouts, errors, skipped, useremail, errorLog):
    if not os.path.exists(resultsfile):
        return
    #read the results file & soup it
    f = open(resultsfile)
    html = f.read()
    f.close()
    # use soup to modify tag
    soup = BeautifulSoup(html)
    div_pdf = soup.find('div', attrs={'id':'pdf_results'})
    div_pdf.replaceWith(msg_results_html(completed, timeouts, errors, skipped, useremail, errorLog))
    #open tempfile and save, then rename
    tempfilename = resultsfile + '.tmp'
    f = open(tempfilename, 'w')
    try:
        f.write(unicode(soup))
        f.close()
        os.rename(tempfilename, resultsfile) 
    finally:
        f.close()
        if os.path.exists(tempfilename):
           os.remove(tempfilename)
    


def email_results(useremail, inputfile, completed, timeouts, errors, errorLog):
    import smtplib
    server = 'localhost'
    sender = "OAC Operations Team <oacops\@cdlib.org>"
    to = useremail
    reply_to = 'oacops@cdlib.org'
    subject = "voroEAD: PDF File Generation Results";
    if len(errors) > 0 or errorLog:
        msg = 'Error while generating PDF for finding aid ' + inputfile
        msg += ' The OAC Operations team has been notified.'
        msg += "ERROR LOG: " + errorLog
    elif len(completed) > 0:
        msg = 'PDF Generated for finding aid: ' + inputfile
    elif len(timeouts) > 0:
        msg = "PDF Generation Failed due to timeouts"
    else:
        msg = "PDF Generation Failed for unknown reason"
      
    mailMsgText= "From:" + sender + "\nTo:" + to + "\nReply-to:" + reply_to +  "\nSubject:" + subject + "\n\n" + msg + "\n\n"
    server=smtplib.SMTP(server)
    ehlo=server.ehlo()
    snd=server.sendmail(sender,to,mailMsgText)
    server.quit()

def main(args):
    #setup our processor
    inputfile = args[1]
    inputfile = os.path.normpath(inputfile)
    if '/dsc/data/in/oac-ead/prime2002/' not in inputfile:
        print inputfile
        raise Exception
    resultsfile = args[2]
    useremail = args[3]
    # any tempfiles will be here
    tempfile.tempdir = "/dsc/workspace/pdf/"

    log_stringio = StringIO.StringIO()
    logging.basicConfig(level=logging.ERROR,
                        stream=log_stringio)
                            
    generator = pdf_gen.OAC_EADtoPDFGenerator(os.path.join(os.environ.get("PATH_TO_PROGS", '/dsc/branches/production/oac-ead-to-pdf'), 'oac4_to_pdf.xslt'))
    (completed, timeouts, errors, skipped) = generator.pdf_gen_file(inputfile,
                                             timeoutSecs=64,
                                             outdir_option='parallel',
                                             data_root='/dsc/data/in/oac-ead/prime2002/',
                                             force=True,
                                            )

    status = get_status(completed, timeouts, errors, skipped, useremail, log_stringio.getvalue())
    # This returns to process cgi
    print msg_results_html(completed, timeouts, errors, skipped, useremail, log_stringio.getvalue())

    if status == 'OK':
        sys.exit(0)

    if status == 'ERROR':
        sys.exit(1)

    if status != 'TIMEOUT':
        sys.exit(2)
    else:
        # try again with no timeout
        # in a subprocess
        sys.stdout.flush() # flush here, else close in forked processes
                           # will output any previous stuff
        logging.shutdown()
        sys.stdin.close()
        sys.stderr.close()
        sys.stdout.close()
        # the trick to REALLY release std filedescriptors
        os.close(0)
        os.close(1)
        os.close(2)
        pid = os.fork()
        if pid:
            sys.exit(0)
        else:
            # want to put log into file
            (fd, filename) = tempfile.mkstemp()
            os.close(fd)
            logging.basicConfig(level=logging.ERROR,
                        filename=filename)
            # in child, run generator again with no time out
            nice = os.nice(19)
            (completed, timeouts, errors, skipped) = generator.pdf_gen_file(inputfile,
                                             timeoutSecs=0,
                                             outdir_option='parallel',
                                             data_root='/dsc/data/in/oac-ead/prime2002/',
                                             force=True,
                                            )
            #READ LOG FILE and delete after results file modified
            logging.shutdown()
            f = open(filename, 'r')
            try:
                errorLog = f.read()
            finally:
                f.close()
                os.remove(filename)
            # if completed, modify results file (replace the div id pdf_results
            # and email the user
            email_results(useremail, inputfile, completed, timeouts, errors, errorLog)
            # email oac ops
#            email_results('oacops@cdlib.org', inputfile, completed, timeouts, errors, errorLog)
            import time
            time.sleep(64)
            modify_results_file(resultsfile, inputfile, completed, timeouts, errors, skipped, useremail, log_stringio.getvalue())
            sys.exit(0)
            
            
if __name__=="__main__":
    main(sys.argv)
