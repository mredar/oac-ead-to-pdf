#! /bin/sh -e

if [ ! $PATH_TO_PROGS ]
then
    SCRIPT=$(readlink -f $0)
    PATH_TO_PROGS=`dirname ${SCRIPT}`
    export PATH_TO_PROGS 
fi
CLASSPATH=$PATH_TO_PROGS/javalib/classes:$CLASSPATH
export CLASSPATH

#python2.5+ (PIL, pisa, reportlab want 2.5)
python ${PATH_TO_PROGS}/pdf_gen.py $@
