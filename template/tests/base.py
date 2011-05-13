import os, unittest
import web
import {{name}}

from flask import json

class BaseTest(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_SETTINGS'] = 'settngs_test'
        self.app = web.app.test_client()
    
    def tearDown(self):
        pass
    
    def ajax(self, method, url, headers=[], query_string=None, data=None):
        method = method.lower()
        assert method in ("get", "post", "delete", "put", "head")
        method = getattr(self.app, method)
        if method == self.app.get:
            response = method(url, query_string=query_string, headers=headers)
        else:
            response = method(url, data=json.dumps(data), query_string=query_string, headers=headers)
        
        if response.status_code == 200:
            response.result = json.loads(response.data)
        
        return response