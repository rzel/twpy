
# Copyright: The TWPY Organization, License: BSD-3-Clause

import webview
import time # from time import sleep
import sys
import os # from os import path
import argparse
import shutil
import subprocess
import urllib.request
import datetime


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
        pywebview.api.notifySavePYfromJS();

        // Remove the message element from the message box
        message.parentNode.removeChild(message);
        // Send a confirmation message
        var event = document.createEvent("Events");
        event.initEvent("tiddlyfox-have-saved-file", true, false);
        event.savedFilePath = filepath;
        message.dispatchEvent(event);        
    });
    """

global twpym_window_list, twpy_verbose, twpy_testing

twpym_window_list = list(())
twpy_testing = False


def twpy_thread_loop():
    #for w in twpym_window_list:
    #    w.window.evaluate_js(twpy_saver_js)
    # twpy_window.to_save = True
    while len(twpym_window_list) > 0:        
        for w in twpym_window_list:
            if w.to_savews:
                w.savews()   
            if w.to_opentw:
                w.opentw()      
            if w.to_maketw:
                w.maketw()         
        time.sleep(0.05)
    

class PyJsApi:
 
    def __init__(self, twpy_webview):
        self.twpy_webview = twpy_webview
     
    def pyjsNotifySaveWorkspace(self): 
        printif(twpy_verbose, "PyJsApi.pyjsNotifySaveWorkspace")
        self.twpy_webview.to_savews = True     

    def pyjsLaunchWikiEditor(self, filepath): 
        printif(twpy_verbose, "PyJsApi.pyjsLaunchWikiEditor('" + filepath + "')")
        self.twpy_webview.edittw(filepath)

    def pyjsNotifySelectWiki(self): 
        printif(twpy_verbose, "PyJsApi.pyjsNotifySelectWiki")
        self.twpy_webview.to_opentw = True

    def pyjsShowWikiLocation(self, command, filepath): 
        printif(twpy_verbose, "PyJsApi.pyjsShowWikiLocation('" + command + "', '" + filepath + "')")
        self.twpy_webview.showtw(command, filepath)

    def pyjsNotifyCreateWiki(self, templatepath):
        printif(twpy_verbose, "PyJsApi.pyjsNotifyCreateWiki")
        self.twpy_webview.to_maketw = True
        self.twpy_webview.templatepath = templatepath

class TwPyManagerWebview:

    def __init__(self, filepath):
        self.py_js_api = PyJsApi(self)
        self.filepath = filepath
        self.content = readtxtbin(self.filepath)
        self.title = 'twpy Workspace Manager - ' + os.path.basename(self.filepath)
        self.window = webview.create_window(title=self.title, html=self.content, js_api=self.py_js_api, width=1024, height=512, text_select=True)   
        twpym_window_list.append(self)
        self.to_savews = False
        self.to_opentw = False
        self.to_maketw = False
        def window_close_listener():
            twpym_window_list.remove(self)
        self.window.events.closed += window_close_listener
            
    def savews(self): # failsafe save  
        printif(twpy_verbose, "TwPyManagerWebview.save")
        self.content = self.window.evaluate_js("twjsGetDocument()") # new XMLSerializer().serializeToString(document); # if we don't do 'document.title = ', the save function will add javascript to the title tag - calling "save" the next time the page is loaded
        savepath = self.filepath
        if twpy_testing: # GET RID OF APPENDING "-thetest" TO self.filepath IN PRODUCTION
            savepath += "-thetest"
        safesavestr(savepath, savepath + "-twpytmp", self.content, twpy_verbose) 
        self.to_savews = False 

    def opentw(self):
        printif(twpy_verbose, "TwPyManagerWebview.openas")
        file_types = ('TiddlyWiki Files (*.html;*.htm)', 'All files (*.*)')
        result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True, file_types=file_types)   
        printif(twpy_verbose, "TwPyManagerWebview.openas: self.window.create_file_dialog: " + str(result))
        if result:
            for r in result:
                self.window.evaluate_js("twjsImportWiki('" + r + "')")     
        self.to_opentw = False
        
    def edittw(self, filepath):
        if twpy_testing:
            twpy_codedir = os.path.dirname(os.path.abspath(__file__))
            twpy_scriptpath = os.path.join(twpy_codedir, 'twpye.py')
            printif(twpy_verbose, "TwPyManagerWebview.edittw: twpy_scriptpath: '" + twpy_scriptpath + "'") 
            edit_tw_terminal_command = 'python3 ' + twpy_scriptpath + ' --file ' + " '" + filepath + "' "   
        else:    
            edit_tw_terminal_command = 'twpye ' + ' --file ' + " '" + filepath + "' "   
        if twpy_verbose:
            edit_tw_terminal_command += ' --verbose'
        printif(twpy_verbose, "TwPyManagerWebview.edittw: edit_tw_terminal_command: '" + edit_tw_terminal_command + "'")     
        subprocess.Popen(edit_tw_terminal_command, shell=True)    
       
    def showtw(self, command, filepath):
        printif(twpy_verbose, "TwPyManagerWebview.showtw: command: '" + command + "', filepath: '" + filepath + "'") 
        if command:
            subprocess.Popen(command + " '" + filepath + "'", shell=True)  
    
    def copytw(self, filepath):
        pass
        
    def maketw(self):
        printif(twpy_verbose, "TwPyManagerWebview.maketw")
        local_file = self.window.create_file_dialog(webview.SAVE_DIALOG, directory='~/', save_filename='new-tiddlywiki-' + str((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()) + '.html')
        printif(twpy_verbose, "TwPyManagerWebview.maketw: local_file: '" + str(local_file) + "'")
        if local_file:
            local_file = ''.join(local_file)
            with urllib.request.urlopen(self.templatepath) as in_stream, open(local_file, 'wb') as out_file:
                shutil.copyfileobj(in_stream, out_file)        
            self.window.evaluate_js("twjsImportWiki('" + local_file + "')")
        self.to_maketw = False             


def start_twpy_manager():
    twpy_parser = argparse.ArgumentParser(description='twpy args')
    twpy_parser.add_argument('-l', '--list', dest='list', type=str, help='Path of the workspace file containing the list of all active TiddlyWiki files.')
    twpy_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose terminal output.')
    twpy_args = twpy_parser.parse_args()
    global twpy_verbose
    twpy_verbose = hasattr(twpy_args, 'verbose') and twpy_args.verbose
    print("twpym: verbose mode: '" + str(twpy_verbose) + "'")
    twpy_configdir = os.path.join(os.path.abspath(os.path.expanduser('~')), '.twpy') # /home/username/.twpy/
    print("twpym: twpy_configdir: '" + twpy_configdir + "'")
    twpy_codedir = os.path.dirname(os.path.abspath(__file__))
    print("twpym: twpy_codedir: '" + twpy_codedir + "'")
    twpy_blanklistpath = os.path.join(twpy_codedir, 'defaultworkspacelist.html')
    print("twpym: twpy_blanklistpath: '" + twpy_blanklistpath + "'")
    twpy_listpath = twpy_args.list if hasattr(twpy_args, 'list') and twpy_args.list else os.path.join(twpy_configdir, 'workspacelist.html')
    print("twpym: twpy_listpath: '" + twpy_listpath + "'")
    if not os.path.exists(twpy_configdir):
        os.mkdir(twpy_configdir)
    if not os.path.exists(twpy_listpath):
        shutil.copyfile(twpy_blanklistpath, twpy_listpath)
    print("twpym: list file: '" + twpy_listpath + "'")
    if twpy_testing:
        twpy_listpath = twpy_blanklistpath
    twpy_window = TwPyManagerWebview(twpy_listpath)
    webview.start(twpy_thread_loop, debug=True)
 

# start_twpy_manager()
print("--end-twpy-manager--")





