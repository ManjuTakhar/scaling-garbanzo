# import json
# from typing import Any, Dict

# from hkdf import Hkdf
# from jose.jwe import decrypt, encrypt

token = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiZGZpWHl6ZXhCb0VldFY4RFpDNk1McjNFdlZ6ZzFoRWZtNXBYc19rY1dDTXpXUHFFVmM1VmpFWHM0RVNCVnM2X2tmTFMxRmNRdTQ1cmFxdHAycmVwYkEifQ..0JFv1al3O3q8dWMyi4Zt5w.GfwmroRElnQUvoHDwEf0bunkUwMEUvQEWKNog06ehdg8LgWqbEULjkO4_ppj5opGrEDCBjfyLTfC0eQNx-HunPB8ZpvNs_MDPRUeFjd3xFKT9T8CaAgC6f_NKAYhZiHfabHQ1CFJ_wUpIy6Xn2-SKFlpYOFcHBKrnktMbOgMnjxa1sBtJq-y7ALHcG-IbMGTKcDJVbb7JP0YX4vX0hrkMmXxUExq4FEDx9qVIHtWLgWU5eLlMPF_iThpZ2MBmA3n8H9LGEoZ_GPQ0cM29-kK6I4NotRQcEktAhK1CFhS1OVAVweE-0o1C6Ng_k21G9etukxqYzZ982xYOx4ib2UPFGrXhsN5F8lmayzDeeYF9nUplNCgiYzeX3N9TbrffEgx5trVwlqWQaR-epxo3nslYw.1am2n3zIzYBOX20sLBv7rVqY5swpRxsjYtmfXj5D8yA"
secret = "03f13061781d1cc91c8714e28cee1459d939339b0ed081299e98d42fd195fbd3"

import json
from typing import Any, Dict
import base64
from hkdf import Hkdf 
from jose.jwe import decrypt, encrypt #pip install python-jose

class AuthJSDecoder:
    def __init__(self,secret:str,secure_cookies:bool) -> None:
        self.secret = secret
        self.salt = None
        
        if secure_cookies == True:
            self.salt = "__Secure-authjs.session-token"
        else:
            self.salt = "authjs.session-token"

    def __encryption_key(self):
        return Hkdf(bytes(self.salt,"utf-8"), bytes(self.secret, "utf-8")).expand(
            f"Auth.js Generated Encryption Key ({self.salt})".encode("utf-8"), 
            64
        )
    
    def encode_jwe(self,payload: Dict[str, Any]):
        data = bytes(json.dumps(payload), "utf-8")
        key = self.__encryption_key()
        return bytes.decode(encrypt(data, key), "utf-8")

    def decode_jwe(self,token: str):
        e_key=  self.__encryption_key()
        decrypted = decrypt(token,e_key)
        if decrypted:
            return json.loads(bytes.decode(decrypted, "utf-8"))
        else:
            return None