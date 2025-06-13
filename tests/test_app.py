
import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_login_page(self):
        response = self.client.get('/admin_login')
        self.assertEqual(response.status_code, 200)

    def test_cashier_login_page(self):
        response = self.client.get('/cashier_login')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
