from lxml import etree as ET
import os
import os.path

rootdir = '/dsc/data/in/oac-ead/prime2002'
nested = []
for root, dirs, files in os.walk(rootdir):
    for file in files:
        fpath = os.path.join(root, file)
        foo = open(fpath)
        try:
            tree = ET.parse(foo) 
            dscs = tree.xpath('//dsc')
            sub = []
            for dsc in dscs:
                sub = dsc.xpath('dsc')
                if sub:
                    print "FILE:", fpath, " has at least", len(sub), " nested dscs"
                    nested.append((fpath, len(sub), os.stat(fpath)[6]))
        finally:
            foo.close()

f = open('nested.out', 'w')
for foo in nested:
    f.write("%s -- %d -- nests:%d" % (foo[0], foo[2], foo[1]))
    f.write('\n')
f.close()
