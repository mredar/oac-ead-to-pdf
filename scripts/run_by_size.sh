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
if [ $LOG_DIR ]
then
    echo "LOG DIR: ${LOG_DIR}"
else
    LOG_DIR=${PATH_TO_PROGS}/log
    echo "LOG DIR: ${LOG_DIR}"
fi
if [  $DATA_DIR ]
then
    echo "DATA DIR: ${DATA_DIR}"
else
    DATA_DIR=/dsc/data/in/oac-ead/prime2002/
    export DATA_DIR 
    echo "DATA DIR: ${DATA_DIR}"
fi

nice -19 ${PATH_TO_PROGS}/pdf_gen_by_size_parallel.sh -outdir=parallel -logprefix=${LOG_DIR}/pdf_gen_by_size_parallel -cssfile=${PATH_TO_PROGS}/oac_unicode_pdf.css ${DATA_DIR} &> ${LOG_DIR}/pdf_gen_by_size_parallel.out

set logsnip = '`tail ${LOG_DIR}/pdf_gen_by_size_parallel.log`'

mail mark.redar@ucop.edu <<%%
subject: PDF Job Done


pdf_gen_by_size_parallel prime2002 for dsc on $HOST run finished.

$logsnip


%%
