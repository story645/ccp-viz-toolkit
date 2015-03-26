#!/usr/bin/env python
#
# setup_venv.py
#
# Hannah Aizenman, 2011-06
# 
# http://www.opensource.org/licenses/bsd-license.php

"""
Installs a virtual_env containing all the libraries required for developing 
and using the toolkit.

setup_venv.py [--python python-binary]

Based on the install files used to deploy https://graphyte.org/
and the bootstrapping tutorial on http://pypi.python.org/pypi/virtualenv
"""

# General note: os.system is used even though subprocess.call is recommended 
# because subprocess.call raises OSError: [Errno 13] Permission denied

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html
import os

def setup_virtualenv(env_path, python_path):
    print 'Creating virtualenv...'
    python_var = "=".join(['--python', python_path])
    command = " ".join([python_path, 'virtualenv.py', 
                        '--no-site-packages', env_path])
    os.system(command)
    return 
					 
def with_virtual_env(env_path, installer, req):
    """Installs the requirement into the virtual env.
    """
    venv = os.path.join(env_path, 'bin', 'activate')
    command = " ".join(['.', venv, '&&', installer,  req])
    os.system(command)
    print " %s installed " % req

def install_in_virtualenv(env_path, prereqs):
    """Passes the requirement and one of the python install 
    tools to an install routine. The function tries easy_install
    if pip fails.
    """
    problems = []		
    for req in prereqs:
        try:
            with_virtual_env(env_path, 'pip install --use-mirrors', req)
        except Exception, exc:
            try:
                with_virtual_env(env_path, 'easy_install -i http://d.pypi.python.org/simple', req)
            except Exception, exc:
                print str(exc)
                problems.append((req, str(exc)))
    return problems
        
def main(argv=None):
    # http://docs.python.org/release/2.5.4/lib/module-getopt.html
    import getopt
    # http://docs.python.org/release/2.5.4/lib/module-sys.html
    import sys

    if argv is None:
        argv = sys.argv

    # These should be commandline args
    cur_path = os.getcwd()
    env_name = 'ccpenv'
    python_path = '/usr/local/bin/python2.7' 

    # tries to automatically find the python path
    py_ver = 'python2.7'
    # unix specfic so won't work elsewhere
    try:
        pybins = ['/usr/local/bin/{}'.format(py_ver),
                  '/usr/local/bin/{}'.format(py_ver)]
    except Exception,e:
        pybins = []
    python_bin = [pb for pb in pybins if os.path.exists(pb)]
    if python_bin:
        python_path = python_bin[0]
                                         
    opts,arg = getopt.getopt(argv[1:], '', ['python='])
    for o,v in opts:
        if o == '--python':
            python_path = v
    
    env_path = os.path.join(cur_path, env_name)
    
    # Deletes existing virtual_venv
    if os.path.exists(env_path):
        # http://docs.python.org/2.7/library/shutil.html#shutil.rmtree
        import shutil
        shutil.rmtree(env_path)
                                        
       
    # The matplotlib and basemap pipy listing is broken, 
    # so pip needs the download url for the source 
    matplotlib_url = "http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.0.1/matplotlib-1.0.1.tar.gz"
    basemap_url = "http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.1/basemap-1.0.1.tar.gz/download"
    
    ccpweb_path = os.path.join(cur_path, "ccpweb")
    
    # command for installing ccplib and ccpweb in develop mode:
    ccplib = "".join(['-e'," ", 'file:', cur_path])
    ccpweb = "".join(['-e'," ", 'file:', ccpweb_path])
    
    prereqs = ['pyramid==1.1',
               'docutils',
               'mercurial',
               'numpy==1.6.0',
               'scipy==0.9.0',
               'coards',
               matplotlib_url,
               basemap_url, 
               ccplib, 
               ccpweb]
    
    # creates venv and installs prereqs in it 
    setup_virtualenv(env_path, python_path)
    install_in_virtualenv(env_path, prereqs)
    
    
if __name__=="__main__":
    main()
            
