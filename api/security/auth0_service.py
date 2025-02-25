from http import HTTPStatus

import jwt

from api.utils import json_abort
import logging
logger = logging.getLogger("myapp")

class Auth0Service:
    """Perform JSON Web Token (JWT) validation using PyJWT"""

    def __init__(self):
        logger.debug("__init__ start")
        self.issuer_url = None
        self.audience = None
        self.algorithm = 'RS256'
        self.jwks_uri = None
        logger.debug("__init__ end")

    def initialize(self, auth0_domain, auth0_audience):
        logger.debug(f"initialize {auth0_domain} {auth0_audience} start")
        self.issuer_url = f'https://{auth0_domain}/'
        self.jwks_uri = f'{self.issuer_url}.well-known/jwks.json'
        self.audience = auth0_audience
        logger.debug(f"initialize {auth0_domain} {auth0_audience} end")

    def get_signing_key(self, token):
        logger.debug("get_signing_key start")
        try:
            jwks_client = jwt.PyJWKClient(self.jwks_uri)

            logger.debug("get_signing_key end")
            return jwks_client.get_signing_key_from_jwt(token).key
        except Exception as error:
            json_abort(HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "signing_key_unavailable",
                "error_description": error.__str__(),
                "message": "Unable to verify credentials"
            })

    def validate_jwt(self, token):
        logger.debug("validate_jwt start")
        try:
            jwt_signing_key = self.get_signing_key(token)

            payload = jwt.decode(
                token,
                jwt_signing_key,
                algorithms=self.algorithm,
                audience=self.audience,
                issuer=self.issuer_url,
            )
        except Exception as error:
            json_abort(HTTPStatus.UNAUTHORIZED, {
                "error": "invalid_token",
                "error_description": error.__str__(),
                "message": "Bad credentials"
            })
            return

        logger.debug("validate_jwt end")
        return payload


auth0_service = Auth0Service()
