import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_bad_request_missing_text():
    """Test validation when text field is missing"""
    from lambda_handler import _bad_request
    response = _bad_request("Field 'text' is required")
    assert response['statusCode'] == 400
    assert 'error' in json.loads(response['body'])

def test_bad_request_short_text():
    """Test validation when text is too short"""
    from lambda_handler import _bad_request
    response = _bad_request("Text must be at least 10 characters")
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert "at least 10" in body['error']

def test_server_error():
    """Test server error response"""
    from lambda_handler import _server_error
    response = _server_error("Model load failed")
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])

if __name__ == '__main__':
    test_bad_request_missing_text()
    test_bad_request_short_text()
    test_server_error()
    print("All tests passed!")
