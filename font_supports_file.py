#!/usr/bin/env python
'''
Support to suss out which xml files have non supported characters in them.

Needed to get expat to unparse escaped unicode chars such as Shinkichir&#x14D

'''
import sys
import os
import codecs
import xml.parsers.expat

FONTS = {'ascii': [ (0,255),],
         'dejavu': [ (0,0x02DF),  (0x02E0,0x02E9), (0x02EC,0x02EE), 0x02F3, 0x02F7, #latin
             (0x0300,0x034F), (0x0351,0x0353), (0x0357,0x0358), 0x035A, (0x035C,0x0362), #comgbining diacritical marks
             (0x0370,0x0377), (0x037A,0x037E), (0x0384,0x038A), 0x038C, (0x038E,0x03A1),(0x03A3,0x03FF), #greek and coptic
             (0x0400,0x0525), #cyrillic
             (0x0531,0x0556),(0x0559,0x055F),(0x0561,0x0587),(0x0589,0x058A), #armenian
             (0x05B0,0x05C3), (0x05C6,0x05C7), (0x05D0,0x05EA), (0x05F0,0x05F4), #hebrew
             (0x0606,0x0607), (0x0609,0x060A), 0x060C, (0x0621,0x063A), (0x0640,0x0655), 0x0657, 0x065A, (0x0660,0x0670), 0x0674, (0x0679,0x6BF), 0x06C6, 0x06CC, 0x06CE, 0x06D5, (0x6F0,0x06F9), #arabic
             (0x07C0,0x07E7), (0x07EB,0x07F5), (0x07F8,0x07FA),#NKo
             0x0E3F,
             (0x10A0,0x10C5), (0x10D0,0x10FC), #georgian
             (0x1401,0x14FF), (0x1500,0x1507), (0x1510,0x153E), (0x1540,0x1550), (0x1552,0x156A), (0x1574,0x1585), (0x158A,0x1596), (0x15A0,0x15AF), (0x15DE), (0x15E1), (0x1646,0x1647), (0x1670,0x1676), #canadian aboriginal syllabics
             (0x1680,0x169C), #ogham
#             (0x1D00,0x1D14), (0x1D16,0x1D23), (0x1D26,0x1D2E), (0x1D30,0x1D5B), (0x1D5D,0x1D6A), (0x1D77,0x1D78), 0x1D7b, 0x1D7D, #phonetic expressions 
             (0x1E00,0x1EFB),#latin extended additional
             (0x1F00,0x1F15), (0x1F18,0x1F1D), (0x1F20,0x1F45), (0x1F48,0x1F4D), (0x1F50,0x1F57), 0x1F59, 0x1F5B, 0x1F5D, (0x1F5F,0x1F7D), (0x1F80,0x1FB4), (0x1FB6,0x1FC4), (0x1FC6,0x1FD3), (0x1FD6,0x1FDB), (0x1FDD,0x1FEF), (0x1FF2,0x1FF4), (0x1FF6,0x1FFE), #greek extended
             (0x2000,0x2064), (0x206A,0x206F), #genral punctuation
             (0x2070,0x2071), (0x2074,0x208E), (0x2090,0x2094), #super/sub scripts
             (0x20A0,0x20B5), (0x20B8,0x20B9), #currency 
             (0x2100,0x2109),(0x210B,0x2149),0x214B, 0x214E, # letterlike symbols
             (0x2150,0x2185), 0x219, # number forms
             (0x2190,0x21FF),  #arrows
             (0x2200,0x22FF), #math
             (0x2500,0x269C), (0x26A0,0x26B8), (0x26c0,0x26C3), #drawing
             (0x2701,0x2704),(0x2706,0x2709),(0x270C,0x2727),(0x2729,0x274B),0x274D, (0x274F,0x2752), 0x2756, (0x2758,0x275E),(0x2761,0x2794),(0x2798,0x27AF),(0x27B1,0x27BE), #dingbats
             (0x2800, 0x28FF), #Braille
             (0x2c60,0x2C7F),#latin extended c
             (0x2D30,0x2D65), #Tiffnagh
             (0x4DC0,0x4DFF), # Yijing Hexagrams
             (0xFB53,0xFBA3), (0xFBAA,0xFBAD), (0xFBD3,0xFBD6), (0xFBD9,0xFBDA),(0xFBE8,0xFBE9),(0xFBFC,0xFBFF), #arabic presentation
             (0xFE70,0xFE74),(0xFE76,0xFEFC),0xFEFF, #arabic presentation-b
             (0x1D300,0x1D356), #Tai Xuan Jing Symbols
             (0x1F030,0x1F093), # dominos
             ], #TODO: EXTEND
         }
        

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

def test_file_against_font_coverage(filepath, fontname):
    unicode_str = None
    with codecs.open(filepath, 'r', encoding='utf-8') as infile:
        unicode_str = infile.read()
    unicode_str = unescape_xml(unicode_str) # replace xml escaped unicode with true
    fontcodes = FONTS[fontname]
    return  test_against_font_coverage(unicode_str, fontname, fontcodes)

def test_against_font_coverage(unicode_str, fontname, fontcodes):
    '''test against the font. The fontcodes is a iterable of mixed integers and
    tuples representing the low,high values for the char range.
    For now just Deja Vu is mapped?
    '''
    font_range = []
    for rng in fontcodes:
        try:
            start, stop = rng
        except TypeError, ValueError:
            start = stop = rng
        #   TODO: change to expressions and eval, quicker and less mem
        font_range.extend(range(start, stop+1))
    passes = True
    for c in unicode_str:
        if ord(c) not in font_range:
            passes = False
            print "Incompatible char for ", fontname, c.encode('utf-8'), ord(c) 
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
        ok_fonts = []
        for fontname, fontcodes in FONTS.items():
            if test_against_font_coverage(xml_to_true_unicode, fontname, fontcodes):
                ok_fonts.append(fontname)
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
