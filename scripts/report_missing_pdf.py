'''For a given directory and parallel pdf directory, report missing pdfs.
Give the EAD file stats for ones with missing pdfs.
Assumes that the root input directory is the branching point for the pdf dir, named pdf....
'''
import os, sys
from  datetime import datetime
import pdf_gen

DIR_EAD_ROOT = '/dsc/data/in/oac-ead/prime2002/'

def isNot_DC_or_METS_XML(fname):
    '''Checks file name to ensure file is just a <foo>.xml
    '''
    (name, ext) = os.path.splitext(fname)
    if ext == '.xml':
        #check if extra . in name (.mets.xml etc)
        (n2, ext2) = os.path.splitext(name)
        if not ext2:
            return True
        #need to ignore .dc.xml & .mets.xml but not other names
        if not (ext2 == '.dc' or ext2 == '.mets'):
            return True
    return False

def input_is_newer(self, input_file, output_file):
    newer = True
    if os.path.exists(output_file):
        out_stat = os.stat(output_file)
        if out_stat.st_size != 0:
            if os.stat(input_file).st_mtime < out_stat.st_ctime:
                newer = False
    return newer
def main(args=sys.argv):
    '''Run the check.
    No args
    Outputs list of xml files missing parallel directory pdf

    '''
    parallel_root = pdf_gen.build_parallel_dir(DIR_EAD_ROOT)
    missing = []
    found = []
    for root, dirs, files in os.walk(DIR_EAD_ROOT):
        for file in files:
            #translate file path, sub parallel_root for DIR_EAD_ROOT
            if not isNot_DC_or_METS_XML(file):
                continue
            source_path =os.path.join(root, file) 
            pdf_file_name = pdf_gen.build_parallel_path(source_path, DIR_EAD_ROOT)
            (pdf_file_name, ext) = os.path.splitext(pdf_file_name)
            pdf_file_name += '.pdf'
            statinfo_src = os.stat(source_path)
            if not os.path.exists(pdf_file_name) or os.stat(pdf_file_name).st_size == 0:
                statinfo_pdf = None
                if os.path.exists(pdf_file_name):
                    statinfo_pdf = os.stat(pdf_file_name)
                missing.append(((source_path, statinfo_src), (pdf_file_name, statinfo_pdf)))
            else:
                statinfo_pdf = os.stat(pdf_file_name)
                found.append(((source_path, statinfo_src), (pdf_file_name, statinfo_pdf)))
    if not missing:
        print 'NO MISSING PDF FOUND'
        #y = raw_input( 'Do you want a list of matching docs?')
        #if y.lower()[0] == 'y':
        #    print found
    else:
        print "MISSING %d PDFS\n" % len(missing)
        for (srcinfo, pdfinfo) in missing:
            pdf_msg = 'missing'
            if pdfinfo[1]:
                pdf_msg = 'zero size'
            print "%s mtime:%s ctime:%s size:%1.2fM PDF %s is %s" % (srcinfo[0],
                    datetime.fromtimestamp(srcinfo[1].st_mtime).strftime('%Y%m%d:%H:%M:%S'),
                    datetime.fromtimestamp(srcinfo[1].st_ctime).strftime('%Y%m%d:%H:%M:%S'),
                    srcinfo[1].st_size/1000000.0,
                    pdfinfo[0],
                    pdf_msg
                    )

if __name__=="__main__":
    import doctest
    #doctest.testmod()
    main()
