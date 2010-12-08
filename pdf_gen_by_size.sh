#! /bin/csh -v

setenv PATH_TO_PROGS .

#python2.5 (PIL, pisa, reportlab want 2.5)
python ${PATH_TO_PROGS}/pdf_gen_by_size.py $argv[*]
