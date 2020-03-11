#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'A PDF decryption tool based on "qpdf" (empty password)'

__author__ = 'Mango'

import os
import sys
import PyPDF3

def decrypt_files(input_path: str, output_path: str):
    lsdir = os.listdir(input_path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(input_path, i))]
    if dirs:
        for i in dirs:
            decrypt_files(os.path.join(input_path, i), output_path)
    files = [i for i in lsdir if os.path.isfile(os.path.join(input_path, i))]
    for f in files:
        input_file = os.path.join(input_path, f)
        output_file = os.path.join(output_path, input_file)
        if not os.path.isdir(output_path + input_path):
            os.system("mkdir -p %s" % output_path + input_path)
        command = "qpdf --password='' --decrypt %s %s" % (input_file, output_file)
        os.system(command)

if __name__ == "__main__":
    decrypt_files(sys.argv[1], sys.argv[2])
