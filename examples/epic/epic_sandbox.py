# %%
import os

import pandas as pd
import polars as pl
import pyspark
import pyspark.pandas as ps
import json

from fhirpy.fhir import FHIRAPI, JWKS, ExportJob

# %%
base_url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
jwks = JWKS(client_id=os.getenv("EPIC_SANDBOX_CLIENT_ID"))
fhir_api = FHIRAPI(base_url=base_url, jwks=jwks, scopes="")
_ = fhir_api.smart_configuration()

# %%
fhir_api.authorize()

# %% [markdown]
# # https://fhir.epic.com/Documentation?docId=testpatients

# %%
export_job = fhir_api.export(group_id="e3iabhmS8rsueyz7vaimuiaSmfGvi.QwjVXJANlPOgR83")

# %%
export_job = ExportJob(
    content_location="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/BulkRequest/000000000025C13217C5E15243C46E8D",  # noqa E501
    retry_after=120,
)

# %%
mainfest = fhir_api.wait_for_export(export_job)

# %%
manifest_types = set()
for _output in mainfest.output:
    manifest_types.add(_output["type"])
manifest_types = list(manifest_types)

# %%
patient_files = [
    fhir_file for fhir_file in mainfest.output if fhir_file["type"] == ("Patient")
]

# %%
for mainfest_type in manifest_types:
    print(mainfest_type)
    resrouce_files = [
            fhir_file
            for fhir_file in mainfest.output
            if fhir_file["type"] == mainfest_type
    ]
    fhir_data = []
    for fhir_file in resrouce_files:
        fhir_data.append(fhir_api.download_file(**fhir_file))

    with open("data/epic_sandbox_{}.ndjson".format(mainfest_type), "w") as f:
        for data in fhir_data:
            for line in data.content:
                f.write(json.dumps(line)+"\n")


# %%
fhir_data = []
for fhir_file in patient_files:
    fhir_data.append(fhir_api.download_file(**fhir_file))

# %%
# Load into polars
df = None
for data in fhir_data:
    if df is None:
        df = pl.DataFrame(data.content)
    else:
        df = df.vstack(pl.DataFrame(data.content))

# %%
# Load into pandas dataframe
df = None
for data in fhir_data:
    if df is None:
        df = pd.DataFrame(data.content)
    else:
        df = pd.concat(df, pd.DataFrame(data.content))

# %%
# Load into spark dataframe with pandas api
spark = (
    pyspark.sql.SparkSession.builder.master("local")
    .appName("epic_sandbox")
    .getOrCreate()
)

psdf = None
for data in fhir_data:
    if psdf is None:
        psdf = ps.DataFrame(data.content)
    else:
        psdf = ps.concat(psdf, ps.DataFrame(data.content))

spark.stop()
