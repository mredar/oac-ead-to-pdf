#! /bin/sh -e

if [ $PATH_TO_PROGS ]
then
    echo "PATH to Programs: ${PATH_TO_PROGS}"
else
    SCRIPT=`readlink -f $0`
    PATH_TO_PROGS=`dirname ${SCRIPT}`
    echo "PATH to Programs: ${PATH_TO_PROGS}"
fi
CLASSPATH=$PATH_TO_PROGS/javalib/lib/saxonb-8.9.jar:$PATH_TO_PROGS/javalib/classes:${CLASSPATH}
export CLASSPATH

#python2.5+ (PIL, pisa, reportlab want 2.5)
python ${PATH_TO_PROGS}/pdf_gen.py $@
