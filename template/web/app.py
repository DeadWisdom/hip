from flask import *
import static
import {{name}}

app = Flask('web')


### Flat Pages ###
@app.route('/')
def index():
    if app.config['DEBUG']:
        static.compile()
    return render_template('index.html', **locals())