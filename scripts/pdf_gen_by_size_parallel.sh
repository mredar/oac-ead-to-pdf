#! /bin/sh

if [ ! $PATH_TO_PROGS ]
then
    SCRIPT=$(readlink -f $0)
    SCRIPT_DIR=`dirname ${SCRIPT}`
    PATH_TO_PROGS=`dirname ${SCRIPT_DIR}`
    export PATH_TO_PROGS 
fi
CLASSPATH=$PATH_TO_PROGS/javalib/classes:$CLASSPATH
export CLASSPATH

nice -20 python ${PATH_TO_PROGS}/pdf_gen_by_size_parallel.py $@
