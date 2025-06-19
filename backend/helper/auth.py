from flask import request, jsonify
from jwt import encode, decode, exceptions
import jwt
from dotenv import load_dotenv
import os
from functools import wraps
from datetime import datetime, timedelta

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def create_token(username):
    payload = {
        'sub': username,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=86400)
    }
    return encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except exceptions.ExpiredSignatureError:
        return None  # Token expired
    except exceptions.InvalidTokenError:
        return None  # Token invalid

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            
        if not token:
            return jsonify({"error": "Token tidak ditemukan"}), 401
            
        try:
            payload = jwt.decode(
                token,
                os.getenv('SECRET_KEY'),
                algorithms=['HS256']
            )
        except exceptions.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except exceptions.InvalidTokenError:
            return jsonify({"error": "Token tidak valid"}), 401
            
        return f(payload, *args, **kwargs)
    
    return decorated