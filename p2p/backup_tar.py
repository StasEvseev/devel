#!/usr/bin/python
#backup_tar.py
#
# <<<COPYRIGHT>>>
#
#
#
#

"""
.. module:: backup_tar

We want a pipe output or input so we don't need to store intermediate data.
Our backup code only takes data from this pipe when it is ready and form blocks one by one.

The class ``lib.nonblocking.Popen`` starts another process - that process can block but we don't.

We call that "tar" because standard TAR utility is used
to read data from files and folders and create a single data stream.
This data stream is passed via ``Pipe`` to the main process.
 
This module execute a sub process "bppipe" - pretty simple TAR compressor, 
see ``p2p.bppipe`` module.
"""

import os
import sys
# import subprocess

from logs import lg

from lib import bpio
from lib import child_process

#------------------------------------------------------------------------------ 

def backuptar(directorypath, recursive_subfolders=True, compress=None):
    """
    Returns file descriptor for process that makes tar archive.
    In other words executes a child process and create a Pipe to communicate with it.
    """
    if not bpio.pathIsDir(directorypath):
        lg.out(1, 'backup_tar.backuptar ERROR %s not found' % directorypath)
        return None
    subdirs = 'subdirs'
    if not recursive_subfolders:
        subdirs = 'nosubdirs'
    if compress is None:
        compress = 'none'
    # lg.out(14, "backup_tar.backuptar %s %s compress=%s" % (directorypath, subdirs, compress))
    if bpio.Windows():
        if bpio.isFrozen():
            commandpath = "bppipe.exe"
            cmdargs = [commandpath, subdirs, compress, directorypath]
        else:
            commandpath = "bppipe.py"
            cmdargs = [sys.executable, commandpath, subdirs, compress, directorypath]
    else:
        commandpath = "bppipe.py"
        cmdargs = [sys.executable, commandpath, subdirs, compress, directorypath]
    if not os.path.isfile(commandpath):
        lg.out(1, 'backup_tar.backuptar ERROR %s not found' % commandpath)
        return None
    # lg.out(14, "backup_tar.backuptar going to execute %s" % str(cmdargs))
    # p = run(cmdargs)
    p = child_process.pipe(cmdargs)
    return p


def backuptarfile(filepath, compress=None):
    """
    Almost same - returns file descriptor for process that makes tar archive.
    But tar archive is created from single file, not folder.
    """
    if not os.path.isfile(filepath):
        lg.out(1, 'backup_tar.backuptarfile ERROR %s not found' % filepath)
        return None
    if compress is None:
        compress = 'none'
    # lg.out(14, "backup_tar.backuptarfile %s compress=%s" % (filepath, compress))
    if bpio.Windows():
        if bpio.isFrozen():
            commandpath = "bppipe.exe"
            cmdargs = [commandpath, 'nosubdirs', compress, filepath]
        else:
            commandpath = "bppipe.py"
            cmdargs = [sys.executable, commandpath, 'nosubdirs', compress, filepath]
    else:
        commandpath = "bppipe.py"
        cmdargs = [sys.executable, commandpath, 'nosubdirs', compress, filepath]
    if not os.path.isfile(commandpath):
        lg.out(1, 'backup_tar.backuptarfile ERROR %s not found' % commandpath)
        return None
    # lg.out(12, "backup_tar.backuptarfile going to execute %s" % str(cmdargs))
    # p = run(cmdargs)
    p = child_process.pipe(cmdargs)
    return p


def extracttar(tarfile, outdir):
    """
    Opposite method, run bppipe to extract files and folders from ".tar" file.
    """
    if not os.path.isfile(tarfile):
        lg.out(1, 'backup_tar.extracttar ERROR %s not found' % tarfile)
        return None
    lg.out(6, "backup_tar.extracttar %s %s" % (tarfile, outdir))
    if bpio.Windows():
        if bpio.isFrozen():
            commandpath = 'bppipe.exe'
            cmdargs = [commandpath, 'extract', tarfile, outdir]
        else:
            commandpath = "bppipe.py"
            cmdargs = [sys.executable, commandpath, 'extract', tarfile, outdir]
    else:
        commandpath = "bppipe.py"
        cmdargs = [sys.executable, commandpath, 'extract', tarfile, outdir]
    if not os.path.isfile(commandpath):
        lg.out(1, 'backup_tar.extracttar ERROR %s is not found' % commandpath)
        return None
    # p = run(cmdargs)
    p = child_process.pipe(cmdargs)
    return p


#------------------------------------------------------------------------------ 

if __name__ == "__main__":
    lg.set_debug_level(20)
    p = backuptar(sys.argv[1])
    p.make_nonblocking()
    print p
    print p.wait()
    
