#! /bin/sh -v

if [ ! $PATH_TO_PROGS ]
then
    SCRIPT=$(readlink -f $0)
    SCRIPT_DIR=`dirname ${SCRIPT}`
    PATH_TO_PROGS=`dirname ${SCRIPT_DIR}`
    export PATH_TO_PROGS 
fi
CLASSPATH=$PATH_TO_PROGS/javalib/classes:$CLASSPATH
export CLASSPATH
if [ ! $LOG_DIR ]
then
    LOG_DIR=${PATH_TO_PROGS}/log
fi
if [ ! $DATA_DIR ]
then
    DATA_DIR=/dsc/data/in/oac-ead/prime2002/
    export DATA_DIR 
fi


nice -19 ${PATH_TO_PROGS}/pdf_gen_by_size_parallel.sh -outdir=parallel -logprefix=${LOG_DIR}/pdf_gen_by_size_parallel -cssfile=${PATH_TO_PROGS}/oac_pdf.css -force ${DATA_DIR} &> ${LOG_DIR}/pdf_gen_by_size_parallel.out

set logsnip = '`tail ${LOG_DIR}/pdf_gen_by_size_parallel.log`'

mail mark.redar@ucop.edu <<%%
subject: PDF Job Done


pdf_gen_by_size_parallel prime2002 for dsc on $HOST run finished.

$logsnip


%%
