#! /usr/bin/env python
'''
Support to suss out which xml files have non supported characters in them.

Needed to get expat to unparse escaped unicode chars such as Shinkichir&#x14D

'''
import sys
import os
import codecs
import xml.parsers.expat

#FROM: http://wiki.python.org/moin/EscapingXml
def unescape(s):
    want_unicode = False
    if isinstance(s, unicode):
        s = s.encode("utf-8")
        want_unicode = True

    # the rest of this assumes that `s` is UTF-8
    char_list = []

    # create and initialize a parser object
    p = xml.parsers.expat.ParserCreate("utf-8")
    p.buffer_text = True
    p.returns_unicode = want_unicode
    p.CharacterDataHandler = char_list.append

    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    #p.Parse("<e>", 0)
    p.Parse(s, 1)
    #p.Parse("</e>", 1)

    # join the extracted strings and return
    es = ""
    if want_unicode:
        es = u""
    return es.join(char_list)

def test_against_font_coverage(unicode_str, font):
    '''test against the font. The font is a tuple of (<fontname>, [encoding range, encoding_range, ])
    For now just Deja Vu is mapped?
    '''
    fontname = font[0]
    font_range = []
    for rng in font[1]:
        start, stop = rng.split(',')
        font_range.extend(range(int(start, 0), int(stop, 0)+1))
    passes = True
    for c in unicode_str:
        if ord(c) not in font_range:
            passes = False
            #print font, c, ord(c)
            break
    return passes


def get_fonts_with_coverage_for_file(filepath):
    '''Get fonts that will work with file'''
    with codecs.open(filepath, 'r', encoding='utf-8') as infile:
        print "----> Processing {0}".format(filepath)
        s = infile.read()
        if type(s) != "unicode":
            s = unicode(s) # make unicode to force unescape
        xml_to_true_unicode = unescape(s)
        fonts = [('ascii', [ '0,255',],),
                ('dejavu', [ '0,0x02AF',  '0x0370,0x037FF'],), #TODO: EXTEND
                ]
        ok_fonts = []
        for font in fonts:
            if test_against_font_coverage(xml_to_true_unicode, font):
                ok_fonts.append(font)
        return ok_fonts

def main(args):
    '''Report files that need can't use dejavu'''
    if not os.path.isdir(args[1]):
        raise Exception("{0} is not a directory".format(args[1]))
    for root, dirs, files in os.walk(args[1]):
        for f in files:
            if os.path.splitext(f)[1] == '.xml':
                fpath = os.path.abspath(os.path.join(root, f))
                fonts = get_fonts_with_coverage_for_file(fpath)
                if not fonts:
                    print "{0} has no suitable fonts, use unifont.".format(fpath)

if __name__=='__main__':
    main(sys.argv)
