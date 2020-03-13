#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'Extract text from PDF file'

__author__ = 'MangoPro'

import sys
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator


def extractor(fpath: str) -> str:

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
    return res


if __name__ == "__main__":
    extractor(sys.argv[1])
