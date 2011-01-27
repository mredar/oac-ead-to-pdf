#! /bin/sh

# Link relevant OAC XTF stylesheets to local files
# This way our pdf generation will can be sync'd with our main
# XTF style.

# Remove if they exist
#wdir=`pwd`
#echo "\nRemoving directories under ${wdir}/xslt\n"
#echo "DELETE ${wdir}/xslt????\n" 
#echo "ENTER Y to DELETE AND LINK\n"
#read yesno
#if  [ "${yesno}" = "Y" ]
#then

if  [ -d /dsc/branches/production/xtf/style/dynaXML ]
then
set -xv
# remove existing
rm -rf ./xslt
# Build necessary directories
mkdir -p ./xslt/dynaXML/docFormatter/common
mkdir -p ./xslt/dynaXML/docFormatter/ead/oac4
mkdir -p ./xslt/common
mkdir -p ./xslt/xtfCommon
mkdir -p ./xslt/crossQuery/resultFormatter/common

ln /dsc/branches/production/xtf/style/dynaXML/docFormatter/ead/oac4/table.html.xsl ./xslt/dynaXML/docFormatter/ead/oac4/table.html.xsl
ln /dsc/branches/production/xtf/style/dynaXML/docFormatter/ead/oac4/table.common.xsl ./xslt/dynaXML/docFormatter/ead/oac4/table.common.xsl
ln /dsc/branches/production/xtf/style/dynaXML/docFormatter/ead/oac4/parameter.xsl ./xslt/dynaXML/docFormatter/ead/oac4/parameter.xsl
ln /dsc/branches/production/xtf/style/dynaXML/docFormatter/ead/oac4/supplied-labels-headings.xsl ./xslt/dynaXML/docFormatter/ead/oac4/supplied-labels-headings.xsl
ln /dsc/branches/production/xtf/style/dynaXML/docFormatter/ead/oac4/ead.html.xsl ./xslt/dynaXML/docFormatter/ead/oac4/ead.html.xsl
ln /dsc/branches/production/xtf/style/common/langcodes.xsl ./xslt/common/langcodes.xsl
ln /dsc/branches/production/xtf/style/common/geocodes.xsl ./xslt/common/geocodes.xsl
ln /dsc/branches/production/xtf/style/common/SSI.xsl ./xslt/common/SSI.xsl
ln /dsc/branches/production/xtf/style/common/online-items-graphic-element.xsl ./xslt/common/online-items-graphic-element.xsl
ln /dsc/branches/production/xtf/style/common/scaleImage.xsl ./xslt/common/scaleImage.xsl
ln /dsc/branches/production/xtf/style/dynaXML/docFormatter/common/docFormatterCommon.xsl ./xslt/dynaXML/docFormatter/common/docFormatterCommon.xsl
ln /dsc/branches/production/xtf/style/crossQuery/resultFormatter/common/editURL.xsl ./xslt/crossQuery/resultFormatter/common/editURL.xsl
ln /dsc/branches/production/xtf/style/xtfCommon/xtfCommon.xsl ./xslt/xtfCommon/xtfCommon.xsl
else
    echo "You're not on a DSC server. You probably don't want to run this script"
fi
