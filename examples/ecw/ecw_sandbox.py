# %%
import os

from fhirpy import emr_smart_scopes
from fhirpy.fhir import FHIRAPI, JWKS

# %%
base_url = "https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/"
key_json = '{"test_key_json": "test_key_json"}'
jwks = JWKS(
    client_id=os.getenv("ECW_SANDBOX_CLIENT_ID"), jku=os.getenv("JKU"), key=key_json
)
scopes = emr_smart_scopes.ECW()
fhirapi = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)

# %%
while True:
    try:
        smart_config = fhirapi.smart_configuration()
        break
    except Exception as e:
        print(e)
        continue


# %%
fhirapi.authorize()

# %%
group_id = "f0eea0a7-0793-49af-930e-7928bae10567"
export_job = fhirapi.export(group_id=group_id)

# %%
manifest = fhirapi.wait_for_export(export_job)

# %%
# ExportJob(content_location='https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/$export-poll-location?job_id=f5823cae-ac97-40e4-be70-79c0376c10a0', retry_after=120) # noqa: E501
