import os

import pytest

from fhirpy import emr_smart_scopes
from fhirpy.fhir import FHIRAPI
from fhirpy.jwks import JWKS


@pytest.fixture
@pytest.mark.ecw
def base_url():
    return "https://providerapi.advancedmd.com/v1/r4"


@pytest.fixture
@pytest.mark.advancedmd
def client_id():
    return os.getenv("ADVANCED_MD_CLIENT_ID")


@pytest.mark.advancedmd
def test_smart_configuration(base_url, client_id):
    jwks = JWKS(client_id=client_id)
    scopes = emr_smart_scopes.AdvancedMD()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    smart_config = fhir_api.smart_configuration()
    # override for advancedmd
    smart_config["token_endpont"] = "https://providerapi.advancedmd.com/v1/oauth2/token"
    fhir_api._smart_configuration[
        "token_endpoint"
    ] = "https://providerapi.advancedmd.com/v1/oauth2/token"

    assert (
        "https://providerapi.advancedmd.com/v1/oauth2/token"
        == fhir_api.token_endpoint()
    )


@pytest.mark.advancedmd
def test_authorize(base_url, client_id):
    jwks = JWKS(client_id=client_id)
    scopes = emr_smart_scopes.AdvancedMD()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    _ = fhir_api.smart_configuration()
    # override for advancedmd
    fhir_api._smart_configuration[
        "token_endpoint"
    ] = "https://providerapi.advancedmd.com/v1/oauth2/token"

    fhir_api.authorize()

    assert fhir_api.token.expires_in is not None
    assert fhir_api.token.access_token is not None
