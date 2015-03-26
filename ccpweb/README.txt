/**
* ccpweb
*
* Hannah Aizenman, 2011-08
* 
* http://www.opensource.org/licenses/bsd-license.php
**/

Web interface to ccplib
A demo lives at: http://134.74.146.36/hannah/ccpviz.html

Install/testing/deployment instructions: 
https://code.google.com/p/ccp-viz-toolkit/wiki/WebDeploy

Expected urls:
https://code.google.com/p/ccp-viz-toolkit/wiki/urlAPI

All views (sites) are defined in ccpweb/views.py. Most of the views
are used to respond to ajax calls and populate the gui's menues.
Others are good for testing. For example, if a dataset is named xyz, 
host:/xyz should return some metadata about xyz.

Notes about html/js/static:
gui functionality is in ccpweb.js
ccpviz.html provides the html elements ccpweb uses.
All static files are served from /static so add new static content
there.
ccpviz.html (and any other static content that needs to be served but
can't be in /static for whatever reason) needs to be in the folder
SITE_LIB_ROOT points to. 

Instructions for writing the data config files 
are in the README file in configs/






