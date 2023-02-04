
# Copyright: The TWPY Organization, License: BSD-3-Clause

import webview
import time # from time import sleep
import sys
import os # from os import path
import argparse

from tiddlywiki.twpyu import printif
from tiddlywiki.twpyu import safesavestr   
from tiddlywiki.twpyu import readtxtbin  

twpy_saver_js = r"""
    var messageBox = document.createElement("div");
    messageBox.style.display = 'none';
    messageBox.id = "tiddlyfox-message-box";
    document.body.appendChild(messageBox);
    messageBox.addEventListener("tiddlyfox-save-file", function(event) {
        var message = event.target;
        var filepath = message.getAttribute("data-tiddlyfox-path");
        var content = message.getAttribute("data-tiddlyfox-content");

        messageBox.setAttribute("data-to-save", content);
        pywebview.api.pyjsNotifySaveWiki();

        // Remove the message element from the message box
        message.parentNode.removeChild(message);
        // Send a confirmation message
        var event = document.createEvent("Events");
        event.initEvent("tiddlyfox-have-saved-file", true, false);
        event.savedFilePath = filepath;
        message.dispatchEvent(event);        
    });
    """

global twpye_window_list, twpy_verbose

twpye_window_list = list(())
twpy_verbose = False

def twpy_thread_loop():
    for w in twpye_window_list:
        w.window.evaluate_js(twpy_saver_js)
    while len(twpye_window_list) > 0:        
        for w in twpye_window_list:
            if w.to_savetw:
                w.savetw()           
        time.sleep(0.05)
    

class PyJsApi:
 
    def __init__(self, twpy_webview):
        self.twpy_webview = twpy_webview
     
    def pyjsNotifySaveWiki(self): 
        printif(twpy_verbose, "PyJsApi.pyjsNotifySaveWiki")
        self.twpy_webview.to_savetw = True     


class TwPyEditorWebview:

    def __init__(self, filepath, temppath):
        self.py_js_api = PyJsApi(self)
        self.temppath = temppath
        self.filepath = filepath
        self.content = readtxtbin(self.filepath)
        self.title = 'twpy - TiddlyWiki Python - ' + os.path.basename(self.filepath)
        self.window = webview.create_window(title=self.title, html=self.content, js_api=self.py_js_api, width=1280, height=720, text_select=True)   
        twpye_window_list.append(self)
        self.to_savetw = False
        def window_close_listener():
            twpye_window_list.remove(self)
        self.window.events.closed += window_close_listener
            
    def savetw(self): # failsafe save  
        self.content = self.window.evaluate_js("document.getElementById('tiddlyfox-message-box').getAttribute('data-to-save')")  # content = self.window.evaluate_js("$tw.wiki.renderTiddler('text/plain', '$:/core/save/all', {})")  # content = self.window.evaluate_js("document.documentElement.outerHTML")  
        safesavestr(self.filepath, self.temppath, self.content, twpy_verbose)
        self.to_savetw = False 



def start_twpy_editor():
    twpy_parser = argparse.ArgumentParser(description='twpy args')
    twpy_parser.add_argument('-f', '--file', dest='file', type=str, help='Path of the twpy file to work on.')
    twpy_parser.add_argument('-t', '--temp', dest='temp', type=str, help='Path of the temporary file created during saving (optional).')
    twpy_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Verbose terminal output.")
    twpy_args = twpy_parser.parse_args()
    global twpy_verbose
    twpy_verbose = hasattr(twpy_args, "verbose") and twpy_args.verbose
    print("twpye: verbose mode: '" + str(twpy_verbose) + "'")
    twpy_filepath = os.path.abspath(twpy_args.file)
    twpy_temppath = twpy_args.temp if hasattr(twpy_args, "temp") and twpy_args.temp else twpy_filepath+"-twpytmp"
    print("twpye: temp file: '" + twpy_temppath + "'")
    print("twpye: opening file: '" + twpy_filepath + "'")
    twpy_window = TwPyEditorWebview(twpy_filepath, twpy_temppath)
    webview.start(twpy_thread_loop, debug=True)


# start_twpy_editor()
print("--end-twpy-editor--")





