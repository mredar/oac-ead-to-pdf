#! /bin/sh

if [ ! $PATH_TO_PROGS ]
then
    SCRIPT=$(readlink -f $0)
    SCRIPT_DIR=`dirname ${SCRIPT}`
    PATH_TO_PROGS=`dirname ${SCRIPT_DIR}`
    export PATH_TO_PROGS 
fi
CLASSPATH=${PATH_TO_PROGS}/javalib/classes:$CLASSPATH
export CLASSPATH

nice -19 ${PATH_TO_PROGS}/pdf_gen.sh --dir=${PATH_TO_PROGS}/sample_files/ --savehtml --force --css=${PATH_TO_PROGS}/oac_pdf.css &> run_sample_files.out
