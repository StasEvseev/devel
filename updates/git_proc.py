#!/usr/bin/python
#git_proc.py
#
#
# <<<COPYRIGHT>>>
#
#
#
#
#

"""
.. module:: git_proc

A code for all platforms to perform source code updates from official Git repo at:
   
   http://gitlab.bitdust.io/devel/bitdust.git
   
"""

#------------------------------------------------------------------------------ 

_Debug = True
_DebugLevel = 6

#------------------------------------------------------------------------------ 

import os
import sys
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in git_proc.py')

from twisted.internet import protocol

#------------------------------------------------------------------------------ 

if __name__ == '__main__':
    import os.path as _p
    sys.path.insert(0, _p.abspath(_p.join(_p.dirname(_p.abspath(sys.argv[0])), '..')))

#------------------------------------------------------------------------------ 

from logs import lg

from lib import schedule
from lib import maths

from system import bpio

from main import settings

#------------------------------------------------------------------------------ 

_CurrentProcess = None
_FirstRunDelay = 3600
_LoopInterval = 3600 * 6
_ShedulerTask = None

#------------------------------------------------------------------------------ 

def init():
    lg.out(4, 'git_proc.init')
    reactor.callLater(0, loop, True)

def shutdown():
    lg.out(4, 'git_proc.shutdown')
    global _ShedulerTask
    if _ShedulerTask is not None:
        if _ShedulerTask.active():
            _ShedulerTask.cancel()
            lg.out(4, '    loop stopped')
        _ShedulerTask = None

#------------------------------------------------------------------------------ 

def update_callback():
    lg.out(6, 'git_proc.update_callback')

def sync_callback(result):
    lg.out(6, 'git_proc.sync_callback: %s' % result)
    try:
        from system import tray_icon
        if result == 'error':
            # tray_icon.draw_icon('error')
            # reactor.callLater(5, tray_icon.restore_icon)
            return
        elif result == 'new-data':
            tray_icon.set_icon('updated')
            return
    except:
        pass

def run_sync():
    lg.out(6, 'git_proc.run_sync')
    reactor.callLater(0, sync, sync_callback)
    reactor.callLater(0, loop)
    
def loop(first_start=False):
    global _ShedulerTask
    lg.out(4, 'git_proc.loop')
    if first_start:
        nexttime = time.time() + _FirstRunDelay
    else:
        nexttime = time.time() + _LoopInterval
    # DEBUG
    # nexttime = time.time() + 10.0
    delay = nexttime - time.time()
    if delay < 0:
        lg.warn('delay=%s %s %s' % (str(delay), nexttime, time.time()))
        delay = 0
    lg.out(6, 'git_proc.loop run_sync will start after %s minutes' % str(delay/60.0))
    _ShedulerTask = reactor.callLater(delay, run_sync)

#------------------------------------------------------------------------------ 

class GitProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, callback):
        self.callback = callback
        self.out = ''
        self.err = ''
    
    def errReceived(self, inp):
        self.err += inp
        for line in inp.splitlines():
            if _Debug:
                lg.out(_DebugLevel, '[git:err]: %s' % line)

    def outReceived(self, inp):
        self.out += inp
        for line in inp.splitlines():
            if _Debug:
                lg.out(_DebugLevel, '[git:out]: %s' % line)
            
    def processEnded(self, reason):
        if _Debug:
            lg.out(_DebugLevel, 'git process FINISHED : %s' % reason.value.exitCode)
        if self.callback:
            self.callback(self.out, reason.value.exitCode)

#------------------------------------------------------------------------------ 

def sync(callback_func=None):
    """
    """
    if _Debug:
        lg.out(_DebugLevel, 'git_proc.sync')
    def _run_callback(response, retcode):
        # print '_run_callback', response, retcode
        if callback_func is None:
            return
        if response.count('Already up-to-date.'):
            callback_func('up-to-date')
        elif response.count('Unpacking objects') or response.count('Fast-forward') or response.count('Updating'):
            callback_func('new-data')
        else:
            if retcode == 0: 
                callback_func('unknown-state')
            else:
                callback_func('sync-error')
    if bpio.Windows():
        cmdargs = ['git', 'pull',]
        exec_dir = bpio.getExecutableDir()
        git_exe = bpio.portablePath(os.path.join(exec_dir, '..', 'git', 'bin', 'git.exe'))
        if not os.path.isfile(git_exe):
            if _Debug:
                lg.out(_DebugLevel, '    not found git.exe, try to run from shell')
            try:
                response, retcode = execute_in_shell(cmdargs)
            except:
                response = ''
                retcode = 1
            _run_callback(response, retcode)
            return
        if _Debug:
            lg.out(_DebugLevel, '    found git in %s' % git_exe)
        cmdargs = [git_exe, 'pull',]
    else:
        cmdargs = ['/usr/bin/git', 'pull',]
    execute(cmdargs, callback=_run_callback)
    
#------------------------------------------------------------------------------ 

def execute(cmdargs, base_dir=None, process_protocol=None, callback=None):
    global _CurrentProcess
    if _Debug:
        lg.out(_DebugLevel, 'git_proc.execute: "%s"' % (' '.join(cmdargs)))
    executable = cmdargs[0]
    if bpio.Windows():
        from twisted.internet import _dumbwin32proc
        real_CreateProcess = _dumbwin32proc.win32process.CreateProcess
        def fake_createprocess(_appName, _commandLine, _processAttributes,
                            _threadAttributes, _bInheritHandles, creationFlags,
                            _newEnvironment, _currentDirectory, startupinfo):
            import win32con
            import _subprocess
            flags = win32con.CREATE_NO_WINDOW
            startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = _subprocess.SW_HIDE
            return real_CreateProcess(_appName, _commandLine,
                            _processAttributes, _threadAttributes,
                            _bInheritHandles, flags, _newEnvironment,
                            _currentDirectory, startupinfo)        
        setattr(_dumbwin32proc.win32process, 'CreateProcess', fake_createprocess)
    
    if process_protocol is None:
        process_protocol = GitProcessProtocol(callback)    
    try:
        _CurrentProcess = reactor.spawnProcess(
            process_protocol, executable, cmdargs, path=base_dir)
    except:
        lg.exc()
        return None
    if bpio.Windows():
        setattr(_dumbwin32proc.win32process, 'CreateProcess', real_CreateProcess)
    return _CurrentProcess

#------------------------------------------------------------------------------ 

def execute_in_shell(cmdargs, base_dir=None, process_protocol=None):
    global _CurrentProcess
    from system import nonblocking
    import subprocess
    if _Debug:
        lg.out(_DebugLevel, 'git_proc.execute_in_shell: "%s"' % (' '.join(cmdargs)))
    _CurrentProcess = nonblocking.Popen(
        cmdargs,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,)    
    out_data = _CurrentProcess.communicate()[0]
    returncode = _CurrentProcess.returncode
    if _Debug:
        lg.out(_DebugLevel, 'git_proc.execute_in_shell returned: %s\n%s' % (returncode, out_data))
    return (out_data, returncode) # _CurrentProcess

#------------------------------------------------------------------------------ 

if __name__ == "__main__":
    bpio.init()
    lg.set_debug_level(18)
    sync()
    reactor.run()
    