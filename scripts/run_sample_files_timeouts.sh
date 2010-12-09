#! /bin/sh

if [ $PATH_TO_PROGS ]
then
    echo "PATH to Programs: ${PATH_TO_PROGS}"
else
    SCRIPT=`readlink -f $0`
    SCRIPTS_DIR=`dirname ${SCRIPT}`
    PATH_TO_PROGS=`dirname ${SCRIPTS_DIR}`
    export PATH_TO_PROGS 
    echo "PATH to Programs: ${PATH_TO_PROGS}"
fi
CLASSPATH=$PATH_TO_PROGS/javalib/classes:$CLASSPATH
export CLASSPATH

nice -19 ${PATH_TO_PROGS}/pdf_gen.sh --list=${PATH_TO_PROGS}/timeouts.list --savehtml --force --css=${PATH_TO_PROGS}/oac_pdf.css --timeout=3600 &> run_sample_files_timeouts.out
