#!/usr/bin/env python
'''
Support to suss out which xml files have non supported characters in them.

Needed to get expat to unparse escaped unicode chars such as Shinkichir&#x14D

'''
import sys
import os
import codecs
import xml.parsers.expat

FONTS = [('ascii', [ (0,255),]),
         ('dejavu', [ (0,0x02DF),  (0x0330,0x034F),
             (0x0370,0x03F), (0x0400,0x0525), (0x0531,0x058A),
             (0x05B0,0x05C3), (0x05C6,0x05C7), (0x05D0,0x05EA), (0x05F0,0x05F4),
             (0x0621,0x063A), (0x0640,0x0655), (0x0679,0x6BF), (0x6F0,0x06F9),
             (0x07C0,0x07E7), (0x07EB,0x07F5), (0x07F8,0x07FA),
             (0x0E3F), (0x10A0,0x10C5), (0x10D0,0x10FC),
             (0x1401,0x14FF),
             (0x1500,0x1507), (0x1510,0x153E), (0x1540,0x1550), (0x1552,0x156A),
             (0x1574,0x1585), (0x158A,0x1596), (0x15A0,0x15AF), (0x15DE),
             (0x15E1), (0x1646,0x1647), (0x1670,0x1676),
             (0x1680,0x169C),
             (0x1E00,0x1EFB),
             (0x2190,0x2311), (0x2500,0x269C), 
             (0x2800, 0x28FF), #Braille
             (0x2c60,0x2C7F),
             (0x2D30,0x2D65), #Tiffnagh
             (0x4DC0,0x4DFF), # Yijing Hexagrams

             (0x1F030,0x1F093) # dominos
             ]
         ), #TODO: EXTEND
        ]

#SNIPPET FROM: http://wiki.python.org/moin/EscapingXml
def unescape(s):
    '''Unescape non-xml text'''
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
    p.Parse("<e>", 0)
    p.Parse(s, 1)
    p.Parse("</e>", 1)

    # join the extracted strings and return
    es = ""
    if want_unicode:
        es = u""
    return es.join(char_list)

def unescape_xml(s):
    '''Unescape well formed xml text'''
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

    p.Parse(s, 1)

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
        try:
            start, stop = rng
        except TypeError:
            start = stop = rng
        #   TODO: change to expressions and eval, quicker and less mem
        font_range.extend(range(start, stop+1))
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
        s = unicode(s) # force unicode
        xml_to_true_unicode = unescape_xml(s) # replace xml escaped unicode with true
                                        # unicode char
        fonts = FONTS
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
