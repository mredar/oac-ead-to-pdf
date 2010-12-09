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
if [  $DATA_DIR ]
then
    echo "DATA DIR: ${DATA_DIR}"
else
    DATA_DIR=/dsc/data/in/oac-ead/prime2002/
    export DATA_DIR 
    echo "DATA DIR: ${DATA_DIR}"
fi


nice -19 python ${PATH_TO_PROGS}/pdf_gen.py --savehtml --force --css=${PATH_TO_PROGS}/oac_pdf.css --outdir=parallel --data_root=${DATA_DIR} --file=$1 &> run_file.out
