
# Copyright: The TWPY Organization, License: BSD-3-Clause

import webview
# from threading import Thread
import time # from time import sleep
import sys
import os # from os import path
import argparse


def printif(cond, str):
    if cond:
        print(str)


def safesavestr(path, tmp_path, data, verbose): # Failproof Save by RZ
    printif(verbose, "failproof_save: writing temp to path: " + tmp_path)
    f = open(tmp_path, "wb")
    f.write(bytes(data, 'UTF-8'))
    f.close() 
    printif(verbose, "failproof_save: reading temp of path: " + tmp_path)    
    f = open(tmp_path, "rb")
    tmp_data = str(bytearray(f.read()), 'UTF-8')
    f.close() 
    printif(verbose, "failproof_save tmp_data: " + str(len(tmp_data)) + " data: " + str(len(data)))       
    if tmp_data == data: # unfortunately, f.read() in text mode strips newlines or adds them or something, so we have to read/write in binary in order for the written file to be binary equal to our string       
        if os.path.exists(path):
            printif(verbose, "failproof_save: removing path: " + path)
            os.remove(path)
        printif(verbose, "failproof_save: renaming path: " + tmp_path)
        os.rename(tmp_path, path)
    printif(verbose, "failproof_save: done saving: '" + path + "'")


def readtxtbin(filepath):
    f = open(filepath, "rb")
    content = str(bytearray(f.read()), 'UTF-8')
    f.close()
    return content
    
    
