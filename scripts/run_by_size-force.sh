#! /bin/sh

if [ $PATH_TO_PROGS ]
then
    echo "PATH to Programs: ${PATH_TO_PROGS}"
else
    SCRIPT=`readlink -f $0`
    SCRIPTS_DIR=`dirname ${SCRIPT}`
    PATH_TO_PROGS=`dirname ${SCRIPTS_DIR}`
    echo "PATH to Programs: ${PATH_TO_PROGS}"
fi
CLASSPATH=$PATH_TO_PROGS/javalib/lib/saxonb-8.9.jar:$PATH_TO_PROGS/javalib/classes:${CLASSPATH}
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
    echo "DATA DIR: ${DATA_DIR}"
fi


nice -19 ${PATH_TO_PROGS}/pdf_gen_by_size_parallel.sh -outdir=parallel -logprefix=${LOG_DIR}/pdf_gen_by_size_parallel -cssfile=${PATH_TO_PROGS}/oac_pdf.css -force ${DATA_DIR} &> ${LOG_DIR}/pdf_gen_by_size_parallel.out

set logsnip = '`tail ${LOG_DIR}/pdf_gen_by_size_parallel.log`'

mail mark.redar@ucop.edu <<%%
subject: PDF Job Done


pdf_gen_by_size_parallel prime2002 for dsc on $HOST run finished.

$logsnip


%%
