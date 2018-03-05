#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
extract parts of rst files.
"""

# pylint: disable=invalid-name

from optparse import OptionParser
#import string
import os.path
import sys
import re
import textwrap
import pprint

# version of the program:
my_version= "1.0"

# output:
out= sys.stdout

#rx_dcolon=re.compile(r'::\s*$')
rx_term=re.compile(r':term:`([^`]+)`')
rx_doc=re.compile(r':doc:`([^<]+)\s*<[^`]+`')
rx_ref=re.compile(r':ref:`([^<]+?)\s*<[^`]+`')
rx_http_link=re.compile(r'`([\w\s]+)\s+(<[^>]+>)`_')
rx_text_link=re.compile(r'`([^`]+)`_')

# python2, python3 compability:
def my_print(st):
    """print."""
    out.write(st)

def process_line(l):
    """do some replacements with the line."""
    #l= rx_dcolon.sub(":", l)
    l= l.replace("``", "")
    l= rx_term.sub(r"\1", l)
    l= rx_doc.sub(r"\1", l)
    l= rx_ref.sub(r"\1", l)
    l= rx_http_link.sub(r"\1 \2", l)
    l= rx_text_link.sub(r'"\1"', l)
    return l

rx_skip=re.compile(r'^\.\.')

def line_to_skip(l):
    """returns True if the line is to skip."""
    return rx_skip.match(l) is not None

def indentation(s):
    """return indentation of a string."""
    if not s:
        return 0
    if s.isspace():
        return 0
    # special hack for enumerations in rst like:
    #  - first item
    #  - second item
    # in this case, the "-" should be treated like a space with respect to
    # indentation.
    #if s.startswith("-"):
    #    s= s.replace("-"," ",1)
    return len(s) - len(s.lstrip())

rx_no= re.compile(r'^[0-9#]\. ')

def enumeration_indent(st):
    """return if st belongs to an enumeration.

    returns indentation for following lines or None.
    """
    if st.startswith("- "):
        return 2
    if rx_no.match(st):
        return 3
    return

def is_table_line(st):
    """return True if the line belongs to a table."""
    st= st.lstrip()
    if st.startswith("+-"):
        return True
    if st.startswith("|"):
        return True
    return False

def empty(s):
    """return the string, if it is empty."""
    if not s:
        return True
    if s.isspace():
        return True
    return False

def join_lines(lines):
    """join paragraphs."""
    new= []
    last_indent= None
    verbatim_mode= 0
    for l in lines:
        if empty(l):
            last_indent= None
            new.append("")
            if verbatim_mode==1:
                verbatim_mode= 2
            elif verbatim_mode==2:
                verbatim_mode= 0
            continue
        l= l.rstrip()
        if is_underline(l, None):
            new.append(l)
            last_indent= None
            continue
        if ends_dcolon(l):
            # replace "::" with ":":
            l= rm_dcolon(l)
            verbatim_mode= 1
            #new.append(l)
            #last_indent= None
            #continue
        if is_table_line(l):
            verbatim_mode= 1
            new.append(l)
            last_indent= None
            continue
        indent= enumeration_indent(l)
        if indent:
            # is an enumeration
            new.append(l)
            last_indent= indent
            continue

        indent= indentation(l)
        if last_indent is None:
            new.append(l)
            last_indent= indent
            continue
        if last_indent!=indent:
            new.append(l)
            last_indent= indent
            continue
        if verbatim_mode>1:
            new.append(l)
            last_indent= indent
            continue
        new[-1]= "%s %s" % (new[-1], l.strip())
    #pprint.pprint(new)
    #sys.exit(1)
    return new

def do_wrap(lines):
    """do text wrap on lines."""
    new= []
    wrapper= textwrap.TextWrapper(width=70, expand_tabs=True,
                                  initial_indent="")
    for l in lines:
        if len(l)<70:
            new.append(l)
            continue
        indent= enumeration_indent(l)
        if indent is None:
            indent= indentation(l)
        wrapper.subsequent_indent= " "*indent
        ll= wrapper.wrap(l)
        new.extend(ll)
    return new

def ends_dcolon(st):
    """returns True if st ends with '::'."""
    return st.rstrip().endswith("::")

def rm_dcolon(st):
    """remove the double colon at the end of a string.

    Note: st *must* end with "::", it is unsafe to call this function if it
    doesn't.
    """
    return st.rstrip()[0:-1]

def is_underline(st, underline_dict):
    """test if st is an rst underline.

    returns the underline character or None.
    """
    if not st:
        return
    ch= st[0]
    for c in st.strip():
        if c!=ch:
            return
    if underline_dict is not None:
        if underline_dict.get(ch) is None:
            if underline_dict.get("max") is None:
                underline_dict["max"]= -1
            underline_dict["max"]= underline_dict["max"]+1
            underline_dict[ch]= underline_dict["max"]
    return ch

def ch_le(ch1, ch2, underline_dict):
    """returns True of ch1 less or equal to ch2."""
    return underline_dict[ch1]<=underline_dict[ch2]

def extract_chapters(chapters, f, no_subchapters):
    """process a single file."""
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    if not chapters:
        sys.exit("chapters are missing")
    chapters_set= set(chapters)
    chapter_order= []
    for h in chapters:
        l= h.split(":",1)
        if len(l)!=2:
            sys.exit("wrong chapter spec: '%s'" % h)
        chapter_order.append(l[0])
    underline_dict= {}
    result= { "_order": chapter_order }
    curr_chapter= None
    curr_dict= None
    curr_chapter_ch= None
    curr_subchapter_ch= None
    curr_subchapter_order= None

    curr_lines= None
    mode="search chapter"
    do_readline= True
    last_line= None
    line= None
    fh= open(f)
    while True:
        if not do_readline:
            do_readline= True
        else:
            last_line= line
            line= fh.readline()
            if line=="":
                break
            line= line.rstrip()
        if mode=="search chapter":
            ch= is_underline(line, underline_dict)
            if ch is None:
                continue
            if last_line is None:
                continue
            h= "%s:%s" % (last_line.strip(), ch)
            if h in chapters_set:
                curr_chapter= last_line.strip()
                curr_chapter_ch= ch
                curr_lines= [last_line, line]
                curr_subchapter_order= []
                if no_subchapters:
                    result[curr_chapter]= curr_lines
                else:
                    curr_dict= { "": curr_lines,
                                 "_order": curr_subchapter_order }
                    result[curr_chapter]= curr_dict
                mode="chapter summary"
            continue
        if mode=="chapter summary":
            ch= is_underline(line, underline_dict)
            if ch is None:
                curr_lines.append(line)
                continue
            if ch_le(ch, curr_chapter_ch, underline_dict):
                # remove previous line
                curr_lines.pop()
                do_readline= False
                mode= "search chapter"
                continue
            if no_subchapters:
                curr_lines.append(line)
                continue
            curr_lines.pop()
            curr_subchapter_ch= ch
            curr_lines= [last_line, line]
            curr_dict[last_line.strip()]= curr_lines
            curr_subchapter_order.append(last_line.strip())
            mode= "subchapter"
            continue
        if mode=="subchapter":
            ch= is_underline(line, underline_dict)
            if ch is None:
                curr_lines.append(line)
                continue
            if ch_le(ch, curr_chapter_ch, underline_dict):
                # remove previous line
                curr_lines.pop()
                do_readline= False
                mode= "search chapter"
                continue
            if ch==curr_subchapter_ch:
                curr_lines.pop()
                curr_lines= [last_line, line]
                curr_dict[last_line.strip()]= curr_lines
                curr_subchapter_order.append(last_line.strip())
                continue
            curr_lines.append(line)
            continue
    fh.close()
    return result

def replace_and_skip(result, no_subchapters):
    """do some first replacements and skip some lines."""
    def repl_lines(lines):
        """replace lines."""
        new= []
        last_len= None
        for line in lines:
            if line_to_skip(line):
                continue
            new_line= process_line(line)
            ch= is_underline(line, None)
            if ch:
                if last_len is not None:
                    new_line= ch * last_len
            new.append(new_line)
            last_len= len(new_line)
        return new
    for chapter_name, chapter in result.items():
        if chapter_name=="_order":
            continue
        if no_subchapters:
            result[chapter_name]= repl_lines(chapter)
        else:
            for subchapter_name, subchapter in chapter.items():
                if subchapter_name=="_order":
                    continue
                chapter[subchapter_name]= repl_lines(subchapter)

def text_wrap(result, no_subchapters):
    """wrap text."""
    def wrap(lines):
        """do the wrap."""
        return do_wrap(join_lines(lines))
    for chapter_name, chapter in result.items():
        if chapter_name=="_order":
            continue
        if no_subchapters:
            result[chapter_name]= wrap(chapter)
        else:
            for subchapter_name, subchapter in chapter.items():
                if subchapter_name=="_order":
                    continue
                chapter[subchapter_name]= wrap(subchapter)


def process(options,args):
    """process all files."""
    # pylint: disable=too-many-branches
    if not options.file:
        sys.exit("error: file not specified")
    result= extract_chapters(args, options.file, options.no_subchapters)
    replace_and_skip(result, options.no_subchapters)
    text_wrap(result, options.no_subchapters)
    if options.pprint:
        if options.varname:
            my_print("%s=\\\n" % options.varname)
        pprint.pprint(result)
    elif options.text:
        for chapter_name in result["_order"]:
            chapter= result[chapter_name]
            if options.no_subchapters:
                my_print("\n".join(chapter))
                my_print("\n")
            else:
                my_print("\n".join(chapter[""]))
                my_print("\n")
                for subchapter_name in chapter["_order"]:
                    my_print("\n".join(chapter[subchapter_name]))
                    my_print("\n")
    else:
        if options.varname:
            my_print("%s=\\\n" % options.varname)
        my_print("{\n")
        my_print('%s: %s,\n' % (repr("_order"), repr(result["_order"])))
        for chapter_name in result["_order"]:
            chapter= result[chapter_name]
            if options.no_subchapters:
                my_print('%s: r"""\n' % repr(chapter_name))
                my_print("\n".join(chapter))
                my_print('""",\n')
            else:
                my_print('%s: {\n' % repr(chapter_name))
                my_print('%s: %s,\n' % (repr("_order"),
                                        repr(chapter["_order"])))
                my_print('"": r"""\n')
                my_print("\n".join(chapter[""]))
                my_print('""",\n')
                for subchapter_name in chapter["_order"]:
                    my_print('%s: r"""\n' % repr(subchapter_name))
                    my_print("\n".join(chapter[subchapter_name]))
                    my_print('""",\n')
                my_print("},\n")
        my_print("}\n")


def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def print_summary():
    """print a short summary of the scripts function."""
    my_print("%-20s: a tool for ...\n\n" % script_shortname())

def main():
    """The main function.

    parse the command-line options and perform the command
    """
    global out

    # command-line options and command-line help:
    usage = "usage: %prog [options] [headings]\n" \
            "Headings must consist of the heading string, a colon and " \
            "the first character of the underline."

    parser = OptionParser(usage=usage,
                          version="%%prog %s" % my_version,
                          description="this program extracts text from rst "
                                      "as python expressions.")

    parser.add_option("--summary",
                      action="store_true",
                      help="print a summary of the function of the program",
                     )
    parser.add_option("--varname",
                      action="store",
                      type="string",
                      help="specify the VARIABLENAME of the python "
                           "structure",
                      metavar="VARIABLENAME"
                     )
    parser.add_option("-f", "--file",
                      action="store",
                      type="string",
                      help="specify the RSTFILE",
                      metavar="RSTFILE"
                     )
    parser.add_option("-o", "--out",
                      action="store",
                      type="string",
                      help="specify the OUTPUTFILE",
                      metavar="OUTPUTFILE"
                     )
    parser.add_option("-n", "--no-subchapters",
                      action="store_true",
                      help="do not create subchapters",
                     )
    parser.add_option("-t", "--text",
                      action="store_true",
                      help="dump as text",
                     )
    parser.add_option("--pprint",
                      action="store_true",
                      help="dump with pprint",
                     )

    # x= sys.argv
    (options, args) = parser.parse_args()
    # options: the options-object
    # args: list of left-over args

    if options.summary:
        print_summary()
        sys.exit(0)

    if options.out:
        f= file(options.out, "w")
        out= f

    process(options,args)
    if options.out:
        f.close()
    sys.exit(0)

if __name__ == "__main__":
    main()

