import json
import time
from dataclasses import dataclass, fields
from typing import Optional

import requests
from requests.models import PreparedRequest

from .jwks import JWKS


class TokenExpired(Exception):
    pass


@dataclass
class FHIRData:
    content: list
    type: str
    url: str


@dataclass
class Token:
    # expected parameters
    access_token: str
    scope: list[str]
    expires_in: int = 300
    token_type: str = ""
    token_created: int = int(time.time())

    # captures unknown parameters and assigns them to the object
    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)


@dataclass
class ExportJob:
    content_location: str
    retry_after: int = 120

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)


@dataclass
class Manifest:
    request: str
    output: list[dict[str, str]]
    transactionTime: str | None = ""
    error: list | None = None
    requiresAccessToken: bool | None = None

    def list_types(self) -> list[str]:
        manifest_types = []
        for _output in self.output:
            manifest_types.add(_output["type"])
        manifest_types = list(manifest_types)

        return manifest_types


class FHIRResponse:
    # TODO make dataclass
    def __init__(self, response: requests.Response):
        self.response = response

    def Manifest(self) -> Manifest:
        return Manifest(**self.response.json())

    def ContentLocation(self) -> str:
        return self.response.headers["Content-Location"]

    def Token(self) -> Token:
        return Token(**self.response.json())

    def SmartConfiguration(self) -> dict:
        if self.response.status_code != 200:
            raise Exception("Getting Smart configuration failed")
        return self.response.json()

    def ExportJob(self) -> ExportJob:
        content_location = self.response.headers.get("Content-Location")
        retry_after = self.response.headers.get("Retry-After")
        params = {
            "content_location": content_location,
            # if retry exists add it to dictionary
            **({"retry_after": int(retry_after)} if retry_after else {}),
        }
        return ExportJob(**params)


@dataclass
class FHIRRequest:
    base_url: str

    def smart_configuration(self):
        url = self.base_url + ".well-known/smart-configuration"
        return {"url": url}

    def authenticate(
        self, token_endpoint: str, client_assertion: str, scopes: list[str]
    ):
        headers = {
            "Accept": "*/*",
            "User-Agent": "Aspen Insights",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = {
            "grant_type": "client_credentials",
            "client_assertion": client_assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",  # noqa: E501
            "scope": " ".join(scopes),
        }

        return {
            "url": token_endpoint,
            "data": payload,
            "headers": headers,
            "allow_redirects": True,
        }

    def export(
        self, token: str, group_id: str, params: Optional[dict[str, str]] = None
    ):
        url = f"{self.base_url}Group/{group_id}/$export"
        req = PreparedRequest()
        req.prepare_url(url, params)
        headers = {
            "Authorization": f"Bearer {token}",
            "Prefer": "respond-async",
            "Accept": "application/fhir+json",
        }

        return {"url": req.url, "headers": headers}

    @staticmethod
    def download_file(url: str, client_assertion: str):
        headers = {
            "Authorization": f"Bearer {client_assertion}",
            "Accept": "*/*",
        }
        return {"url": url, "headers": headers}

    @staticmethod
    def export_job_status(content_locaion: str, client_assertion: str):
        url = content_locaion
        headers = {
            "Authorization": f"Bearer {client_assertion}",
            "Prefer": "respond-async",
            "Accept": "*/*",
        }

        return {"url": url, "headers": headers}


class FHIRAPI:
    def __init__(self, base_url: str, jwks: JWKS, scopes: list[str]):
        self.base_url = (
            base_url if base_url.endswith("/") else f"{base_url}/"
        )  # add trailing / if it doesn't exist
        self.jwks = jwks
        self.scopes = scopes
        self._smart_configuration: dict | None = None
        self.token: Token | None = None

    def smart_configuration(self):
        smart_configuration = FHIRResponse(
            requests.get(**FHIRRequest(self.base_url).smart_configuration(), timeout=1)
        ).SmartConfiguration()
        self._smart_configuration = smart_configuration
        return smart_configuration

    def token_endpoint(self):
        return self._smart_configuration["token_endpoint"]

    def authorization_endpoint(self):
        return self._smart_configuration["authorization_endpoint"]

    def authorize(self):
        token_endpoint = self._smart_configuration["token_endpoint"]
        token = self.jwks.get_jwt(token_endpoint)
        response = requests.post(
            **FHIRRequest(self.base_url).authenticate(
                token_endpoint=token_endpoint,
                client_assertion=token,
                scopes=self.scopes,
            )
        )

        if response.status_code != 200:
            if response.headers:
                print(f"ERROR response.header {response.headers}")
                print(f"ERROR response.content {response.content}")
            raise Exception(
                f"Authorization failed with status code {response.status_code} "
            )

        self.token = FHIRResponse(response).Token()

    def export(
        self, group_id: str, params: Optional[dict[str, str]] = None
    ) -> ExportJob:
        self.reauthorize()
        if self.token and self.token.access_token:
            response = requests.get(
                **FHIRRequest(self.base_url).export(
                    group_id=group_id, params=params, token=self.token.access_token
                ),
                timeout=500,
            )
            if response.status_code != 202:
                print(response.headers)
                print(response.content)
                print(response.status_code)
                raise Exception("Job not started")

            exportJob = FHIRResponse(response).ExportJob()

            return exportJob
        else:
            raise Exception("Not authorized")

    def validate_token(self) -> bool:
        if self.token is None:
            raise Exception("Not authorized")
        if self.token.expires_in and self.token.token_created:
            # if token expires in less than 5 seconds raise token expired exception
            if self.token.token_created + self.token.expires_in < time.time() + 5:
                raise TokenExpired("Token expired")
        return True

    def wait_for_export(self, job: ExportJob) -> Manifest:
        if self.token is None:
            raise Exception("Not authorized")
        if self.token.access_token is None:
            raise Exception("Not authorized")
        timeout = time.time() + 60 * 10  # 10 minutes from now timeout
        while True:
            if time.time() > timeout:
                raise Exception("Timed out waiting for export to finish")
            self.reauthorize()
            response = requests.get(
                **FHIRRequest.export_job_status(
                    content_locaion=job.content_location,
                    client_assertion=self.token.access_token,
                )
            )
            if response.headers.get("X-Progress"):
                percent_complete = response.headers.get("X-Progress").split("%")[0]
                print(f"Percent complete: {percent_complete}")
            if response.status_code == 200:
                manifest = FHIRResponse(response).Manifest()
                return manifest
            else:
                time.sleep(job.retry_after)

    def reauthorize(self):
        try:
            self.validate_token()
        except TokenExpired:
            self.authorize()

    def download_file(self, url: str, type: str) -> FHIRData:
        self.validate_token()
        if self.token and self.token.access_token:
            response = requests.get(
                **FHIRRequest.download_file(
                    url=url, client_assertion=self.token.access_token
                )
            )

            json_objects = []
            for line in response.text.splitlines():
                json_objects.append(json.loads(line))

            return FHIRData(content=json_objects, type=type, url=url)
        else:
            raise Exception("Not authorized")
