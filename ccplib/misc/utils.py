#!/usr/bin/env python
#
# utils.py
#
# Hannah Aizenman, 2011-06
#
# http://www.opensource.org/licenses/bsd-license.php

"""This module contains routines for directory 
   creation/maintenance and logging
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html
import os
# http://docs.python.org/2.7/library/shutil.html
import shutil

def new_dir(new_path):
    """Creates a blank directory with a path new_path, deleting
    any directories that already exist. 
    """
    if os.path.exists(new_path):
            shutil.rmtree(new_path)
    try:
        os.mkdir(new_path)
    except OSError, e:
        os.makedirs(new_path)
    return new_path

def create_folder(save_path, overwrite = False):
    """Manages creating folders.
    """
    if overwrite or not os.path.exists(save_path):
        new_dir(save_path)
    else:
        pass
    return
                                                              
    
# http://docs.python.org/2.7/library/logging.html
import logging
# http://docs.python.org/2.7/library/logging.handlers.html
import logging.handlers

# User can change this through ccplib.misc.utils.logname = name
# Must be set before unpack methods are called
# should probably switch to using a .conf file:
# http://docs.python.org/library/logging.config.html#logging-config-api

LOGNAME = 'ccplog'

def setup_logging(save_path, scrnlog=True, txtlog=True, loglevel=logging.DEBUG):
    """
    sets up a log in the logging directory, 
    adds new logs on every run
    an old log gets a number added to it, so for example:
    ccp.log becomes ccp.log.1
    """
    
    log = logging.getLogger(LOGNAME)
    log.setLevel(loglevel)
    
    log_format_str = "%(asctime)s - %(levelname)s :: %(message)s"
    log_formatter = logging.Formatter(log_format_str)
    
    lgfn = ".".join([LOGNAME, 'log']) 
    
    if txtlog:
        logdir = os.path.join(save_path, 'logs')
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        txt_handler = logging.handlers.RotatingFileHandler(
                                os.path.join(logdir, lgfn), backupCount=5)
        txt_handler.doRollover()
        txt_handler.setLevel(loglevel)
        txt_handler.setFormatter(log_formatter)
        log.addHandler(txt_handler)
        log.info("Logger initialised.")
            
    if scrnlog:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_formatter)
        log.addHandler(console_handler)
        

# http://docs.python.org/2.7/library/smtplib.html    
import smtplib                                          
                                                        
def alert(body, username, password, recipient):
    """Used to send an email alert to user after job failure or completion.
    """
    
    mail_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    mail_server.set_debuglevel(1)                        
    mail_server.login(username, password)               
    try:                                                
        mail_server.sendmail(username, recipient, body)        
    finally:                                            
        mail_server.quit()    
        
