import json
import time
import uuid
from dataclasses import dataclass

import requests
from jwcrypto.jwk import JWK, JWKSet
from jwcrypto.jwt import JWT


@dataclass(frozen=True)
class JWKS:
    client_id: str
    jku: str
    json_key: str

    def get_jwt(self, token_endpoint: str, timeout: int = 5) -> str:
        key = self.get_key(self.json_key)
        token = JWT(
            header={
                "alg": "RS384",
                "jku": self.jku,
                "typ": "JWT",
                "kid": "rsa_aspen_insights",
            },
            claims={
                "sub": self.client_id,
                "iss": self.client_id,
                "aud": token_endpoint,
                "iat": int(time.time()),
                "exp": int(time.time() + (timeout * 60)),
                "jti": uuid.uuid4().hex,
            },
        )
        token.make_signed_token(key)
        return token.serialize()

    def validate(self, jwt_token: dict) -> JWT:
        jwks_response = requests.get(self.jku)
        jwks_data = jwks_response.json()
        jwk_set = JWKSet.from_json(json.dumps(jwks_data))

        try:
            jwt = JWT()
            jwt.deserialize(jwt_token)
            jwt.verify(
                jwk_set, algorithms=["ES384"]
            )  # Specify the algorithm used for signing

            # If verification is successful, you can access the JWT claims
            claims = jwt.claims
            print("JWT is valid")
            print(claims)
        except Exception as e:
            print("JWT validation failed:", e)

        return jwt

    def get_key(self, json_key: str | dict) -> JWK:
        if json_key is None:
            raise Exception("No key provided")
        if isinstance(json_key, str):
            json_key = json.loads(json_key)
        key = JWK(**json_key)

        return key
