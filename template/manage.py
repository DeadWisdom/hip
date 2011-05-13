#!env/bin/python
import os, getpass
from werkzeug import script
from getpass import getpass

from web import app

def load_app():
    return app

def make_shell():
    return {'app': app}

action_runserver = script.make_runserver(load_app, use_reloader=True, threaded=True)
action_shell = script.make_shell(make_shell)

script.run()