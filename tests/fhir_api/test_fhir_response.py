import json

import pytest
import requests

from fhirpy.fhir import FHIRResponse, Manifest

pytestmark = pytest.mark.fhirapi


def test_token():
    response = requests.Response()
    response.status_code = 200
    test_access_token = "test_token"
    response._content = json.dumps(
        {"access_token": test_access_token, "expires_in": 300}
    ).encode("utf-8")
    token = FHIRResponse(response).Token()

    assert token.access_token == test_access_token


def test_token_with_unknown_param():
    response = requests.Response()
    response.status_code = 200
    test_access_token = "test_token"
    response._content = json.dumps(
        {"access_token": test_access_token, "unknown": "test_unknown"}
    ).encode("utf-8")
    token = FHIRResponse(response).Token()

    assert token.access_token == test_access_token


def test_export():
    expected_headers = requests.structures.CaseInsensitiveDict(
        {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, GET, PUT, OPTIONS, DELETE",
            "Access-Control-Max-Age": "3600",
            "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, remember-me, X-AUTH-TOKEN",  # noqa: E501
            "Retry-After": "120",
            "Content-Location": "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/$export-poll-location?job_id=11e0f05a-8e25-4fe8-8bed-e9195ceddda5",  # noqa: E501
        }
    )

    response = requests.Response()
    response.status_code = 202
    response.headers = expected_headers
    exportJob = FHIRResponse(response).ExportJob()

    assert exportJob.content_location == expected_headers["Content-Location"]
    assert exportJob.retry_after == int(expected_headers["Retry-After"])
    assert exportJob.retry_after == 120


def test_export_missing_retry_after():
    expected_headers = requests.structures.CaseInsensitiveDict(
        {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, GET, PUT, OPTIONS, DELETE",
            "Access-Control-Max-Age": "3600",
            "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, remember-me, X-AUTH-TOKEN",  # noqa: E501
            "Content-Location": "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/$export-poll-location?job_id=11e0f05a-8e25-4fe8-8bed-e9195ceddda5",  # noqa: E501
        }
    )

    response = requests.Response()
    response.status_code = 202
    response.headers = expected_headers
    exportJob = FHIRResponse(response).ExportJob()

    assert exportJob.retry_after == 120


def test_parse_ecw_manifest():
    expected_headers = requests.structures.CaseInsensitiveDict(
        {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, GET, PUT, OPTIONS, DELETE",
            "Access-Control-Max-Age": "3600",
            "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, remember-me, X-AUTH-TOKEN",  # noqa: E501
            "Content-Location": "https://fhir.test.com/fhir/r4/FFBJCD/$export-poll-location?job_id=11e0f05a-8e25-4fe8-8bed-e9195ceddda5",  # noqa: E501
        }
    )

    response = requests.Response()
    response.status_code = 202
    response.headers = expected_headers

    with open("tests/fhir_api/manifest.json") as f:
        expected_json = json.load(f)
    response._content = json.dumps(expected_json).encode("utf-8")

    expected_manifest = Manifest(**expected_json)

    manifest = FHIRResponse(response).Manifest()

    assert manifest == expected_manifest


def test_parse_unknown_params_manifest():
    expected_headers = requests.structures.CaseInsensitiveDict(
        {
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, GET, PUT, OPTIONS, DELETE",
            "Access-Control-Max-Age": "3600",
            "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, remember-me, X-AUTH-TOKEN",  # noqa: E501
            "Content-Location": "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/$export-poll-location?job_id=11e0f05a-8e25-4fe8-8bed-e9195ceddda5",  # noqa: E501
        }
    )

    response = requests.Response()
    response.status_code = 202
    response.headers = expected_headers

    with open("tests/fhir_api/manifest.json") as f:
        expected_json = json.load(f)
    response._content = json.dumps(expected_json).encode("utf-8")

    expected_manifest = Manifest(**expected_json)

    manifest = FHIRResponse(response).Manifest()

    assert manifest == expected_manifest


# def test_token(fhir_response):
#     token = fhir_response.Token()
#     assert token is None  # Replace with the expected value
