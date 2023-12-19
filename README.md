# Contribute

## Linux
- Install python 3.10
- `python3.10 -m venv ~/.venvs/poetry`
- `source ~/.venv/poetry/bin/activate`
- `python -m pip install poetry`
- `python -m poetry install --with dev,test`

## Windows TBD

## Testing

## Module Tests

`poetry run pytest -m fhirapi`

## Integration Tests

`poetry run pytest -m ecw`

# AdvancedMD

## Well Known Configuration

`https://providerapi.advancedmd.com/v1/r4/.well-known/smart-configuration`

## Testing Public JWKS

`https://providerapi.advancedmd.com/v1/fhir-jwks/jwks.json`

# ECW

## Token endpoints

### Production

`https://oauthserver.eclinicalworks.com/oauth/oauth2/authorize`

`https://oauthserver.eclinicalworks.com/oauth/oauth2/token`

### Sandbox

BASE FHIR URL: `https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD`

FHIR Capabilities URL: `https://staging-fhir.ecwcloud.com/fhir/r4/FFBJCD/metadata?_format=json`
