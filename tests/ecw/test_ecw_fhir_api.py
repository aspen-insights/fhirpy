import json
import os

import pytest

from fhirpy import emr_smart_scopes
from fhirpy.fhir import FHIRAPI, ExportJob
from fhirpy.jwks import JWKS


@pytest.fixture
@pytest.mark.ecw
def base_url():
    return "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD"


@pytest.fixture
@pytest.mark.ecw
def client_id():
    return os.getenv("ECW_CLIENT_ID"), os.getenv("JKU"), os.getenv("JKU_KEY")


@pytest.mark.ecw
def test_smart_configuration(base_url, client_id):
    jwks = JWKS(client_id=client_id, jku="your_json_key", json_key="your_json_key")
    scopes = emr_smart_scopes.ECW()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    smart_config = fhir_api.smart_configuration()

    with open("tests/ecw/smart-configuration.json") as f:
        expected_mart_config_json = json.load(f)

    assert expected_mart_config_json == smart_config
    assert expected_mart_config_json["token_endpoint"] == fhir_api.token_endpoint()
    assert (
        expected_mart_config_json["authorization_endpoint"]
        == fhir_api.authorization_endpoint()
    )


@pytest.mark.ecw
def test_authorize(base_url, client_id):
    jwks = JWKS(client_id=client_id)
    scopes = emr_smart_scopes.ECW()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    _ = fhir_api.smart_configuration()

    fhir_api.authorize()

    assert fhir_api.token.expires_in is not None
    assert fhir_api.token.access_token is not None


@pytest.fixture
@pytest.mark.ecw
def authorized_api(base_url, client_id) -> FHIRAPI:
    jwks = JWKS(client_id=client_id)
    scopes = emr_smart_scopes.ECW()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    _ = fhir_api.smart_configuration()

    fhir_api.authorize()

    return fhir_api


@pytest.mark.ecw
def test_export(authorized_api: FHIRAPI):
    fhir_api = authorized_api

    authorized_api.authorize()

    authorized_api.validate_token()

    # group id from ecw sandbox environment
    # https://fhir.eclinicalworks.com/ecwopendev/dashboard/view-published-app
    export_job = fhir_api.export(group_id="f0eea0a7-0793-49af-930e-7928bae10567")
    print(export_job)

    assert export_job.content_location is not None
    assert export_job.retry_after > 0


@pytest.mark.ecw
def test_wait_for_export(authorized_api: FHIRAPI):
    fhir_api = authorized_api

    # group id from ecw sandbox environment
    # https://fhir.eclinicalworks.com/ecwopendev/dashboard/view-published-app
    export_job = fhir_api.export(group_id="f0eea0a7-0793-49af-930e-7928bae10567")

    mainfest = fhir_api.wait_for_export(export_job)

    assert len(mainfest) > 0


@pytest.mark.ecw
# this export is good for 30 days
def test_export_status(authorized_api: FHIRAPI):
    fhir_api = authorized_api
    export_job = ExportJob(
        content_location="https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/$export-poll-location?job_id=a7785569-6a7b-4985-9e04-ef5f3a0889d1",  # noqa: E501
        retry_after=120,
    )

    mainfest = fhir_api.wait_for_export(export_job)

    assert mainfest is not None
    assert mainfest.output is not None
    assert len(mainfest.output) > 0


@pytest.mark.ecw
def test_download_manifest_content(authorized_api: FHIRAPI):
    fhir_api = authorized_api
    export_job = ExportJob(
        content_location="https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/$export-poll-location?job_id=a7785569-6a7b-4985-9e04-ef5f3a0889d1",  # noqa: E501
        retry_after=120,
    )

    mainfest = fhir_api.wait_for_export(export_job)

    data = fhir_api.download_file(**mainfest.output[0])

    assert data is not None  # Can Load like pd.read_json(data.content, lines=True)
