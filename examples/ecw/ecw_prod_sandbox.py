# %%
from fhirpy import emr_smart_scopes
from fhirpy.fhir import FHIRAPI, JWKS

# %%
base_url = "https://fhir4.eclinicalworks.com/fhir/r4/JAFJCD/"
scopes = emr_smart_scopes.ECW()
jwks = JWKS("", "jwks.json")
fhirapi = FHIRAPI(base_url=base_url, jwks=jwks, scopes=scopes)

# %%
smart_config = fhirapi.smart_configuration()

# %%
fhirapi.authorize()

# %%
group_id = "ba542a09-9f1a-44f9-943a-dad8310c99bd"  # bulk data - >1985
export_job = fhirapi.export(group_id=group_id)

# %%
manifest = fhirapi.wait_for_export(export_job)

# %%
