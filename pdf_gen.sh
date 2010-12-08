#! /bin/csh -v

setenv PATH_TO_PROGS .

#python2.5 (PIL, pisa, reportlab want 2.5)
python ./pdf_gen.py $argv[*]
