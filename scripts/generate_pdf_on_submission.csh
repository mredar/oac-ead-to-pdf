#! /usr/bin/csh

# wrapper for python prog generate_pdf_on_submission.py
#setenv PYTHONPATH /dsc/local/pythonlib/:/dsc/local/pythonlib/pisa/
setenv PATH_TO_PROGS /dsc/branches/production/pdf_gen
setenv CLASSPATH=$PATH_TO_PROGS/javalib/classes

#python2.5 (PIL, pisa, reportlab want 2.5)
/dsc/local/bin/python $PATH_TO_PROGS/scripts/generate_pdf_on_submission.py $argv[*]
