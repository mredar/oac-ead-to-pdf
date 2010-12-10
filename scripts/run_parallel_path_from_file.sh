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
if [  $DATA_DIR ]
then
    echo "DATA DIR: ${DATA_DIR}"
else
    DATA_DIR=/dsc/data/in/oac-ead/prime2002/
    echo "DATA DIR: ${DATA_DIR}"
fi


nice -19 python ${PATH_TO_PROGS}/pdf_gen.py --savehtml --force --css=${PATH_TO_PROGS}/oac_pdf.css --outdir=parallel --data_root=${DATA_DIR} --file=$1 2>&1 > run_file.out
