import os

def which(program):
    '''Find executable for a given name by PATH, or None if no executable could be found'''
    if os.name == 'nt':
        return _nt_which(program)
    elif os.name == 'posix':
        return _posix_which(program)
    raise NotImplementedError(os.platform)

def _nt_which(program):
    PATH = os.environ['PATH'].split(os.pathsep)
    EXT  = os.environ['PATHEXT'].split(os.pathsep)
    name, ext = os.path.splitext(program)
    if ext in EXT:
        # program is specified as foo.exe, for example, in which case
        # we don't go looking for foo.exe.exe or foo.exe.bat
        for p in PATH:
            n = os.path.join(p, program)
            if os.path.isfile(n):
                return n
    else:
        for p in PATH:
            for e in EXT:
                n = os.path.join(p, program + e)
                if os.path.isfile(n):
                    return n
    return None

def _posix_which(program):
    PATH = os.environ['PATH'].split(os.pathsep)
    for p in PATH:
        n = os.path.join(p, program)
        if os.path.isfile(n) and os.access(n, os.X_OK):
            return n
    return None
