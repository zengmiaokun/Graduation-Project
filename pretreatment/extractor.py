#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'Clean and extract data'

__author__ = 'MangoPro'


import sys
import re
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator


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
    return ''.join(res)


def extract_data(input_text: str) -> dict:
    'Extract data from text'

    # Put result in a dict
    res = dict()

    # Extract the abstract section using regular expressions
    pattern_abs = r'(\[\s*摘要\s*\][\s]*)([\s\S]*)(\[\s*关键词\s*\])'
    abstract_raw = re.search(pattern_abs, input_text)[2]

    # Remove extra special characters
    abstract_value = re.sub(r'[\s\t\n]*', '', abstract_raw, count=0)

    # Put the content of abstract section in the dict
    res['abstract'] = abstract_value

    return res


if __name__ == "__main__":

    import time
    start = time.time()
    text = extract_text(sys.argv[1])
    print(extract_data(text))
    print("Time: %.2fs" % (time.time()-start))
