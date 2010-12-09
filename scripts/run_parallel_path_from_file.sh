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
if [ ! $DATA_DIR ]
then
    DATA_DIR=/dsc/data/in/oac-ead/prime2002/
    export DATA_DIR 
fi


nice -19 python ${PATH_TO_PROGS}/pdf_gen.py --savehtml --force --css=${PATH_TO_PROGS}/oac_pdf.css --outdir=parallel --data_root=${DATA_DIR} --file=$1 &> run_file.out
