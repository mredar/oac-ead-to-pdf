#! /bin/sh

SCRIPT=`readlink -f $0`
SCRIPTS_DIR=`dirname ${SCRIPT}`

. ${SCRIPTS_DIR}/set-pdf-env.sh

if [ $PATH_TO_PROGS ]
then
    echo "PATH to Programs: ${PATH_TO_PROGS}"
else
    PATH_TO_PROGS=`dirname ${SCRIPTS_DIR}`
    echo "PATH to Programs: ${PATH_TO_PROGS}"
fi
if [ $CLASSPATH ]
then
    echo "CLASSPATH: ${CLASSPATH}"
else
    CLASSPATH=$PATH_TO_PROGS/javalib/lib/saxonb-8.9.jar:$PATH_TO_PROGS/javalib/classes:${CLASSPATH}
    echo "CLASSPATH: ${CLASSPATH}"
fi
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


nice -9 ${PATH_TO_PROGS}/pdf_gen_by_size_parallel.sh -outdir=parallel -logprefix=${LOG_DIR}/pdf_gen_by_size_parallel -cssfile=${PATH_TO_PROGS}/oac_pdf.css -exclude_file=${SCRIPTS_DIR}/exclude.list ${DATA_DIR} 2>&1 > ${LOG_DIR}/pdf_gen_by_size_parallel.out

if [ ${PRODUCTION} = "true" ]; then
#datefix=`date +%Y-%m-%d`
#logsnip=`tail ${LOG_DIR}/pdf_gen_by_size_parallel-${datefix}.log`
logsnip=`tail ${LOG_DIR}/pdf_gen_by_size_parallel.out`
mail mark.redar@ucop.edu <<%%
subject: PDF Job Done


pdf_gen_by_size_parallel prime2002 for dsc on ${VORO_HOSTNAME} run finished.

${logsnip}


%%
fi
