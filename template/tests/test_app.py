from base import BaseTest


class TestFlat(BaseTest):
    def test_index(self):
        r = self.app.get('/')
        assert r.status_code == 200
