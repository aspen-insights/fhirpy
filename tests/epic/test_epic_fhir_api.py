import json
import os

import pytest

from fhirpy import emr_smart_scopes
from fhirpy.fhir import FHIRAPI, ExportJob
from fhirpy.jwks import JWKS


@pytest.fixture
@pytest.mark.epic
def base_url():
    #  Sandbox URL https://open.epic.com/MyApps/Endpoints
    return "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"


@pytest.fixture
@pytest.mark.epic
def group_id():
    #  https://fhir.epic.com/Documentation?docId=testpatients
    return "e3iabhmS8rsueyz7vaimuiaSmfGvi.QwjVXJANlPOgR83"


@pytest.fixture
@pytest.mark.epic
def client_id():
    return os.getenv("EPIC_SANDBOX_CLIENT_ID")


@pytest.mark.epic
def test_smart_configuration(base_url, client_id):
    jwks = JWKS(client_id=client_id)
    scopes = emr_smart_scopes.Default()
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)
    smart_config = fhir_api.smart_configuration()

    with open("tests/epic/smart-configuration.json") as f:
        expected_mart_config_json = json.load(f)

    assert expected_mart_config_json == smart_config
    assert expected_mart_config_json["token_endpoint"] == fhir_api.token_endpoint()
    assert (
        expected_mart_config_json["authorization_endpoint"]
        == fhir_api.authorization_endpoint()
    )


@pytest.mark.epic
def test_authorize(base_url, client_id):
    jwks = JWKS(client_id=client_id)
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes="")
    _ = fhir_api.smart_configuration()

    fhir_api.authorize()

    assert fhir_api.token.expires_in is not None
    assert fhir_api.token.access_token is not None


@pytest.fixture
@pytest.mark.epic
def authorized_api(base_url, client_id) -> FHIRAPI:
    jwks = JWKS(client_id=client_id)
    fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes="")
    _ = fhir_api.smart_configuration()

    fhir_api.authorize()

    return fhir_api


@pytest.mark.epic
def test_export(authorized_api: FHIRAPI, group_id):
    fhir_api = authorized_api

    authorized_api.authorize()

    # group id from ecw sandbox environment
    # https://fhir.epic.com/Documentation?docId=testpatients
    # have to send a request to open@epic.com with client id to use bulk api
    export_job = fhir_api.export(group_id=group_id)
    print(export_job)

    assert export_job.content_location is not None
    assert export_job.retry_after > 0


@pytest.mark.epic
def test_wait_for_export(authorized_api: FHIRAPI):
    fhir_api = authorized_api

    # group id from ecw sandbox environment
    # https://fhir.eclinicalworks.com/ecwopendev/dashboard/view-published-app
    export_job = ExportJob(
        content_location="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/BulkRequest/000000000025C13217C5E15243C46E8D",
        retry_after=120,
    )

    mainfest = fhir_api.wait_for_export(export_job)

    with open("mainfest.json", "w") as f:
        json.dump(mainfest.output, f)

    assert len(mainfest.transactionTime) is not None
    assert len(mainfest.request) is not None
    assert len(mainfest.output) > 0
