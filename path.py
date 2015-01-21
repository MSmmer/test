'''
#path
'''
import os
a = '/usr/share/pyshared/test/a.py'
b = '/usr/lib/dist/test/a.py'
c = '/qihoo/app/a/b/c/d/new.c'
d = '/qihoo/app/1/2/test.c'
print os.path.relpath(a, b)
print os.path.relpath(c,d)
print os.path.relpath(d,c)#d相对于c的路径
