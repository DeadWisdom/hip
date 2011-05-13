#!/usr/bin/env python
import os, sys, shutil, hashlib

TEMPLATE = os.path.abspath( os.path.join(__file__, '..', 'template') )
EXTRAPOLATE = ['settings.py', '__init__.py', 'web/__init__.py', 'web/app.py', 'tests/base.py']

def fail(txt='usage: %s project-name' % sys.argv[0]):
    print txt
    sys.exit(1)

def touch(path):
    with open(path, 'w') as o:
        o.write('')

def extrapolate(path, vars):
    """
    Opens up the path, reads the file, and replaces any {{var}} tags with
    the correct var.
    """
    with open(path, 'r') as o:
        src = o.read()
    for k, v in vars.items():
        src = src.replace('{{%s}}' % k, v)
    with open(path, 'w') as o:
        o.write(src)

def create_project():
    if len(sys.argv) <= 1:
        fail()
    name = sys.argv[1].strip()
    if '/' in name or not name:
        fail()
    if name in ['tests', 'web', 'schema']:
        fail("failure: that name cannot be used, try another")
    if os.path.exists(name):
        fail("failure: directory already exists: %r" % name)
    
    shutil.copytree(TEMPLATE, name)
    print "- copied template to directory: %s" % os.path.abspath(name)
    
    context = {'name': name,
               'secret_key': hashlib.new('md5', os.urandom(128)).hexdigest()}
    for filename in EXTRAPOLATE:
        extrapolate(os.path.join(name, filename), context)
    print "- extrapolated files"
    
    shutil.move(os.path.join(name, 'api'), os.path.join(name, name))
    print "- renamed api directory: %s" % os.path.abspath(os.path.join(name, name))
    
    os.system('pip -E %s/env install -r %s/requirements.txt' % (name, name))
    print "- installed base requirements"
    
    print "- complete"
    
if __name__ == '__main__':
    create_project()