import pytest

from fhirpy import emr_smart_scopes
from fhirpy.fhir import FHIRRequest

pytestmark = pytest.mark.fhirapi


def test_smart_configuration():
    base_url = "https://fhir.test.com/fhir/r4/FFBJCD/"
    params = FHIRRequest(base_url).smart_configuration()

    expect_params = {"url": "".join([base_url, ".well-known/smart-configuration"])}

    assert params == expect_params


def test_authenticate():
    base_url = "https://fhir.test.com/fhir/r4/FFBJCD"
    token_endpoint = "https://staging-oauthserver.ecwcloud.com/oauth/oauth2/token"
    client_assertion = "test_client_assertion"
    scopes = emr_smart_scopes.ECW()
    params = FHIRRequest(base_url).authenticate(
        token_endpoint=token_endpoint, client_assertion=client_assertion, scopes=scopes
    )

    scopes = " ".join(scopes)

    expected_payload = {
        "grant_type": "client_credentials",
        "client_assertion": client_assertion,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",  # noqa: E501
        "scope": scopes,
    }

    expect_params = {
        "url": token_endpoint,
        "data": expected_payload,
        "headers": {
            "Accept": "*/*",
            "User-Agent": "Aspen Insights",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "allow_redirects": True,
    }

    assert params == expect_params


def test_export():
    base_url = "https://fhir.test.com/fhir/r4/FFBJCD/"
    test_token = "test_token"
    params = FHIRRequest(base_url).export(token=test_token, group_id="test_group_id")

    expect_params = {
        "url": f"{base_url}" + "Group/test_group_id/$export",
        "headers": {
            "Authorization": f"Bearer {test_token}",
            "Prefer": "respond-async",
            "Accept": "application/fhir+json",
        },
    }

    assert params == expect_params


def test_export_job_status():
    test_token = "test_token"
    content_locaion = "https://fhir.test.com/fhir/r4/FFBJCD/$export-poll-location?job_id=11e0f05a-8e25-4fe8-8bed-e9195ceddda5"  # noqa: E501
    params = FHIRRequest.export_job_status(
        content_locaion=content_locaion, client_assertion=test_token
    )

    expect_params = {
        "url": content_locaion,
        "headers": {
            "Authorization": f"Bearer {test_token}",
            "Prefer": "respond-async",
            "Accept": "*/*",
        },
    }

    assert params == expect_params


def test_download_file():
    client_assertion = "test_token"
    url = "https://fhir.test.com/fhir/r4/FFBJCD/$dummmy=dummy.ndjson"  # noqa: E501
    params = FHIRRequest.download_file(url=url, client_assertion=client_assertion)

    expect_params = {
        "url": url,
        "headers": {
            "Authorization": f"Bearer {client_assertion}",
            "Accept": "*/*",
        },
    }

    assert params == expect_params
