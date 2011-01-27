#! /usr/bin/csh

# wrapper for python prog generate_pdf_on_submission.py
setenv PATH_TO_PROGS /dsc/branches/production/oac-ead-to-pdf
setenv PYTHONPATH $PATH_TO_PROGS
setenv CLASSPATH=$PATH_TO_PROGS/javalib/lib/saxonb-8.9.jar:$PATH_TO_PROGS/javalib/classes

#python2.5 (PIL, pisa, reportlab want 2.5)
/dsc/local/bin/python $PATH_TO_PROGS/scripts/generate_pdf_on_submission.py $argv[*]
