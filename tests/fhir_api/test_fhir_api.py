import json
import time
from urllib.parse import urljoin

import pytest
import requests_mock

from fhirpy import emr_smart_scopes
import jwcrypto.jwk as jwk
from fhirpy.fhir import FHIRAPI, FHIRRequest, TokenExpired
from fhirpy.jwks import JWKS

pytestmark = pytest.mark.fhirapi


@pytest.fixture
def base_url():
    #  Smart on fhir testing url
    return "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/"  # noqa 501


@pytest.fixture
def generate_keys():
    keys = {
        "test": jwk.JWK.generate(
            kty="RSA",
            alg="RS384",
            size=2048,
            kid="rsa_aspen_insights_ecw",
            use="sig",
            key_ops=["verify", "sign"],
            jwt_header={"jku": "https://test.com/fhir/jwks.json"},
        )
    }

    public_key = keys["test"].export_public(as_dict=True)
    private_key = keys["test"].export_private()

    return private_key, public_key


def test_ecw_smart_configuration(base_url, generate_keys):
    client_id = "test_client_id"
    private_json_key = generate_keys[0]
    jku = "https://test.com/jwks.json"
    jwks = JWKS(client_id=client_id, jku=jku, json_key=private_json_key)
    scopes = emr_smart_scopes.ECW()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)

    with requests_mock.Mocker(real_http=True) as mock:
        with open("tests/fhir_api/smart-configuration.json") as f:
            expected_mart_config_json = json.load(f)
        mock.get(
            FHIRRequest(base_url).smart_configuration()["url"],
            json=expected_mart_config_json,
        )

        smart_config = fhir_api.smart_configuration()

    with open("tests/fhir_api/smart-configuration.json") as f:
        expected_mart_config_json = json.load(f)

    assert expected_mart_config_json == smart_config
    assert expected_mart_config_json["token_endpoint"] == fhir_api.token_endpoint()
    assert (
        expected_mart_config_json["authorization_endpoint"]
        == fhir_api.authorization_endpoint()
    )


def test_authorize(base_url, generate_keys):
    client_id = "test_client_id"
    private_json_key = generate_keys[0]
    jku = "https://test.com/jwks.json"
    jwks = JWKS(client_id=client_id, jku=jku, json_key=private_json_key)
    scopes = emr_smart_scopes.ECW()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)

    with requests_mock.Mocker(real_http=True) as mock:
        with open("tests/fhir_api/smart-configuration.json") as f:
            expected_mart_config_json = json.load(f)
        mock.get(
            FHIRRequest(base_url).smart_configuration()["url"],
            json=expected_mart_config_json,
        )
        _ = fhir_api.smart_configuration()

        mock.post(
            fhir_api.token_endpoint(),
            json={"access_token": "test_access_token", "expires_in": 300},
        )
        fhir_api.authorize()

    assert fhir_api.validate_token()

    assert fhir_api.token is not None


def test_valid_expired_token(base_url, generate_keys):
    client_id = "test_client_id"
    private_json_key = generate_keys[0]
    jku = "https://test.com/jwks.json"
    jwks = JWKS(client_id=client_id, jku=jku, json_key=private_json_key)
    scopes = emr_smart_scopes.ECW()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    with requests_mock.Mocker(real_http=True) as mock:
        with open("tests/fhir_api/smart-configuration.json") as f:
            expected_mart_config_json = json.load(f)
        mock.get(
            urljoin(base_url, ".well-known/smart-configuration"),
            json=expected_mart_config_json,
        )
        _ = fhir_api.smart_configuration()
        mock.post(
            fhir_api.token_endpoint(),
            json={"access_token": "test_access_token", "expires_in": 1},
        )
        fhir_api.authorize()

    time.sleep(1)
    try:
        fhir_api.validate_token()
    except TokenExpired:
        assert True
