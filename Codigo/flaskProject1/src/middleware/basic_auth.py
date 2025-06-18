from flask import jsonify
from basicauth import decode, encode


class BasicAuth:
    
    @classmethod
    def encode_auth(cls, username: str, password: str) -> str:
        try:
            if not username or not password or len(username) == 0 or len(password) == 0:
                return None
            
            enconded_str =  encode(username, password)
            return enconded_str
        
        except Exception as e:
            return None

    @classmethod
    def decode_auth(cls, auth: str) -> tuple:
        try:
            username, password = decode(auth)
            
            return username, password
        
        except Exception as e:
            return None, None