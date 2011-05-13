#!env/bin/python
# -*- coding: utf-8 -*-

import static
from werkzeug.debug import DebuggedApplication
from app import app

### Config ###
app.config.from_object('settings')
app.config.from_envvar('FLASK_SETTINGS', silent=True)

if app.config['DEBUG']:
    app.debug = True
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
else:
    static.compile()

## Middleware ##
def SimulateMethodMiddleware(application):
    """
    Catches "METHOD" header, if provided; this allows the browser to override
    the Method it sends so we can simulate "GET", "DELETE", etc.
    """
    def inner(environ, start_response):
        method = environ.get('HTTP_METHOD', environ['REQUEST_METHOD'].upper())
        environ['REQUEST_METHOD'] = method
        return application(environ, start_response)
    return inner

app.wsgi_app = SimulateMethodMiddleware(app.wsgi_app)

## Database ##
import {{name}}.data
{{name}}.data.set_redis(*app.config['REDIS'])