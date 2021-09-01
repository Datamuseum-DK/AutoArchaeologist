'''
   Render a unix mode word in standard ls(1) rwxrwxrwx format
'''

class StdStat():
    ''' Default unix mode bits '''
    S_ISFMT = 0o170000
    S_IFBLK = 0o060000
    S_IFDIR = 0o040000
    S_IFCHR = 0o020000
    S_IFPIP = 0o010000
    S_IFREG = 0o100000

    S_ISUID = 0o004000
    S_ISGID = 0o002000
    S_ISVTX = 0o001000
    S_IRUSR = 0o000400
    S_IWUSR = 0o000200
    S_IXUSR = 0o000100
    S_IRGRP = 0o000400
    S_IWGRP = 0o000200
    S_IXGRP = 0o000100
    S_IROTH = 0o000400
    S_IWOTH = 0o000200
    S_IXOTH = 0o000100

def unix_file_mode(mode, stat=None):
    ''' ... '''
    txt = ""
    if stat is None:
        stat = StdStat()
    txt += "r" if mode & stat.S_IRUSR else '-'
    txt += "w" if mode & stat.S_IWUSR else '-'
    if mode & stat.S_IXUSR and mode & stat.S_ISUID:
        txt += "s"
    elif mode & stat.S_IXUSR:
        txt += "x"
    else:
        txt += "-"
    txt += "r" if mode & stat.S_IRGRP else '-'
    txt += "w" if mode & stat.S_IWGRP else '-'
    if mode & stat.S_IXGRP and mode & stat.S_ISGID:
        txt += "s"
    elif mode & stat.S_IXUSR:
        txt += "x"
    else:
        txt += "-"
    txt += "r" if mode & stat.S_IROTH else '-'
    txt += "w" if mode & stat.S_IWOTH else '-'
    if mode & stat.S_ISVTX and mode & stat.S_IXOTH:
        txt += "t"
    elif mode & stat.S_ISVTX:
        txt += "T"
    else:
        txt += "-"
    return txt
