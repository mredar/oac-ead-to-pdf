#! /bin/sh

if [ $PATH_TO_PROGS ]
then
    echo "PATH to Programs: ${PATH_TO_PROGS}"
else
    SCRIPT=`readlink -f $0`
    PATH_TO_PROGS=`dirname ${SCRIPT}`
    export PATH_TO_PROGS 
    echo "PATH to Programs: ${PATH_TO_PROGS}"
fi
CLASSPATH=$PATH_TO_PROGS/javalib/classes:$CLASSPATH
export CLASSPATH

nice -20 python ${PATH_TO_PROGS}/pdf_gen_by_size_parallel.py $@
