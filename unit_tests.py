import unittest
import json
from io import BytesIO
import app2

class TestApp(unittest.TestCase):

    def test_request_invalid_method_get(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/MoneyHack/',
        }
        response_body = self.call_app(environ)
        self.assertIn('unknown_time_zone', response_body)  
        
    def test_request_invalid_method_post(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/MoneyHack/',
        }
        response_body = self.call_app(environ)
        self.assertIn('unknown_request', response_body) 
        
    def test_request_invalid_method_other(self):
        environ = {
            'REQUEST_METHOD': 'PUT',
            'PATH_INFO': '/MoneyHack/',
        }
        response_body = self.call_app(environ)
        self.assertIn('unknown_request', response_body) 

    def test_request_invalid_method_type_post(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/MoneyHack/AddGazillionDollars',
        }
        response_body = self.call_app(environ)
        self.assertIn('unknown_request', response_body)   
        
    def test_get_time(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
        }
        response_body = self.call_app(environ)
        self.assertIn('GMT', response_body)

    def test_get_timezone_time(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/Asia/Tomsk',
        }
        response_body = self.call_app(environ)
        self.assertIn('+07', response_body)

    def test_post_convert_time(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/convert/GMT',
            'CONTENT_LENGTH': str(len(json.dumps({
                "date": "12.20.2021 22:21:05", "tz": "EST"
            }))),
            'wsgi.input': BytesIO(json.dumps({
                "date": "12.20.2021 22:21:05", "tz": "EST"
            }).encode('utf-8'))
        }
        response_body = self.call_app(environ)
        self.assertIn('GMT', response_body)

    def test_post_datediff(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/datediff',
            'CONTENT_LENGTH': str(len(json.dumps({
                "first_date": "12.06.2024 22:21:05", "first_tz": "EST",
                "second_date": "12:30pm 2024-02-01", "second_tz": "Europe/Moscow"
            }))),
            'wsgi.input': BytesIO(json.dumps({
                "first_date": "12.06.2024 22:21:05", "first_tz": "EST",
                "second_date": "12:30pm 2024-02-01", "second_tz": "Europe/Moscow"
            }).encode('utf-8'))
        }
        response_body = self.call_app(environ)
        self.assertIn('11440265.0', response_body)

    def test_post_convert_invalid_date_format(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/convert',
            'CONTENT_LENGTH': str(len(json.dumps({
                "date": "invalid-date", "tz": "EST", "target_tz": "Europe/Moscow"
            }))),
            'wsgi.input': BytesIO(json.dumps({
                "date": "invalid-date", "tz": "EST", "target_tz": "Europe/Moscow"
            }).encode('utf-8'))
        }
        response_body = self.call_app(environ)
        self.assertIn('post_req_process_err', response_body)
    
    def test_post_datediff_invalid_date_format(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/datediff',
            'CONTENT_LENGTH': str(len(json.dumps({
                "first_date": "12.06.2024 22:21:05", "first_tz": "GGG",
                "second_date": "12:30pm 2024-02-01", "second_tz": "Europe/Moscow"
            }))),
            'wsgi.input': BytesIO(json.dumps({
                "first_date": "12.06.2024 22:21:05", "first_tz": "GGG",
                "second_date": "12:30pm 2024-02-01", "second_tz": "Europe/Moscow"
            }).encode('utf-8'))
        }
        response_body = self.call_app(environ)
        self.assertIn('post_req_process_err', response_body)   

    def test_post_convert_time_invalid_json_fields(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/convert/GMT',
            'CONTENT_LENGTH': str(len(json.dumps({
                "date": "12.20.2021 22:21:05", "tzzz": "EST"
            }))),
            'wsgi.input': BytesIO(json.dumps({
                "date": "12.20.2021 22:21:05", "tzzz": "EST"
            }).encode('utf-8'))
        }
        response_body = self.call_app(environ)
        self.assertIn('post_req_input_err', response_body)

    def test_post_datediff_invalid_json_fields(self):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/datediff',
            'CONTENT_LENGTH': str(len(json.dumps({
                "first_date": "12.06.2024 22:21:05", "first_tzG": "EST",
                "second_date": "12:30pm 2024-02-01", "second_tzG": "Europe/Moscow"
            }))),
            'wsgi.input': BytesIO(json.dumps({
                "first_date": "12.06.2024 22:21:05", "first_tzG": "EST",
                "second_date": "12:30pm 2024-02-01", "second_tzG": "Europe/Moscow"
            }).encode('utf-8'))
        }
        response_body = self.call_app(environ)
        self.assertIn('post_req_input_err', response_body)

    def call_app(self, environ):
    
        def start_response(status, response_headers):
            self.status = status
            self.response_headers = response_headers
        
        result = app2.app(environ, start_response)
        response_body = b''.join(result).decode('utf-8')
        return response_body

if __name__ == '__main__':
    unittest.main()