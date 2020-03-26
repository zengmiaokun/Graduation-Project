#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'Clean and extract data'

__author__ = 'MangoPro'


import os
import sys
import re
import logging
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator

# ignore WARNING
logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)


def strF2H(ustring):
    'Full-width to Half-width'
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        # Convert "space" directly
        if inside_code == 12288:
            inside_code = 32
        # Convert convertible characters
        elif (inside_code >= 65281 and inside_code <= 65374):
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring


def extract_text(fpath: str) -> str:
    'Extract text from PDF file'

    # Open a PDF file.
    with open(fpath, 'rb') as fp:

        # Create a PDF parser object associated with the file object.
        parser = PDFParser(fp)

    # Create a PDF document object that stores the document structure.
    doc = PDFDocument()

    # Connect the parser and document objects.
    parser.set_document(doc)
    doc.set_parser(parser)

    # Supply the password for initialization.
    # (If no password is set, give an empty string.)
    doc.initialize("")

    # Check if the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Set parameters for analysis.
    laparams = LAParams()

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Store text data
    res = []

    # Process each page contained in the document.
    for page in doc.get_pages():

        # The layout analyzer gives a "LTPage" object for each page in the PDF document.
        interpreter.process_page(page)
        layout = device.get_result()

        # Extract text from TextBox
        for text_box in layout:
            if(isinstance(text_box, LTTextBoxHorizontal)):
                res += text_box.get_text()
    return strF2H(''.join(res))


def extract_data(input_text: str) -> dict:
    'Extract data from text'

    # Put result in a dict
    res = dict()

    # Extract the abstract section using regular expressions
    pattern_abs = r'(\[?\s*摘[\s\t\n]*要\s*\]?[0-9a-zA-Z~\-\s\:]*)([\s\S]{,800})(\[*\s*关[\s\t\n]*键[\s\t\n]*词\s*\]?)'
    abstract_raw = (re.search(pattern_abs, input_text) or ['NULL']*4)[2]

    # Remove extra special characters
    abstract_value = re.sub(r'[\s\t\r\n\[\]\【\】]*', '', abstract_raw, count=0)

    # Put the content of abstract section in the dict
    res['abstract'] = abstract_value

    # Extract the discuss section using regular expressions
    pattern_dcs = r'(讨\s{0,5}论\n)([\s\S]*)参\s{0,3}考\s{0,3}文\s{0,3}献'
    pre_discuss = re.search(pattern_dcs, input_text)
    if not pre_discuss:
        pattern_dcs = r'(小\s{0,5}结\n)([\s\S]*)参\s{0,3}考\s{0,3}文\s{0,3}献'
        pre_discuss = pre_discuss = re.search(pattern_dcs, input_text)
    discuss_raw = (pre_discuss or ['NULL']*3)[2]
    discuss_value = re.sub(r'[\s\t\r\n\[\]\【\】]*', '', discuss_raw, count=0)
    res['discuss'] = discuss_value
    # res['all'] = input_text
    return res


def extract_all(input_path: str):
    lsdir = os.listdir(input_path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(input_path, i))]
    if dirs:
        for i in dirs:
            # extract_all(os.path.join(input_path, i))
            for element in extract_all(os.path.join(input_path, i)):
                yield element
    files = [i for i in lsdir if os.path.isfile(os.path.join(input_path, i))]
    for f in files:
        input_file = os.path.join(input_path, f)
        # print(input_file)
        # print(extract_text(input_file))
        # print(extract_data(extract_text(input_file)))
        temp = re.search(r'[\s\S]*Downloads/(\S*)/([0-9]*)年([0-9]*)期/(\S*).pdf', input_file)
        article_info = dict()
        article_info['journal'] = temp[1]
        article_info['year'] = temp[2]
        article_info['month'] = temp[3]
        article_info['title'] = temp[4]
        try:
            full_text = extract_text(input_file)
        except:
            print("Error: %s\nFile: %s" % ('Extract FullText', input_file))
            continue
        article_info.update(extract_data(full_text))
        yield article_info

if __name__ == "__main__":
    a = extract_all(sys.argv[1])
    for b in a:
        print(b)
