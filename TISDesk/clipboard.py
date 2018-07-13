import win32clipboard as wc
import win32con
def get():
    wc.OpenClipboard()
    d=wc.GetClipboardData(win32con.CF_TEXT)
    wc.CloseClipboard()
    return d

def write(aString):
    wc.OpenClipboard()
    wc.EmptyClipboard()
    #wc.SetClipboardData(win32con.CF_TEXT,aString) #Only write the first letter ?
    wc.SetClipboardText(aString.encode('utf-8'),win32con.CF_TEXT)
    wc.CloseClipboard()