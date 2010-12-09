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

nice -19 ${PATH_TO_PROGS}/pdf_gen.sh --dir=${PATH_TO_PROGS}/sample_files/ --savehtml --force --css=${PATH_TO_PROGS}/oac_pdf.css &> run_sample_files.out
