# Contribute

- Pull requests welcome
- Before pull requests run
  - `black src`
  - `isort src`
  - Use https://www.conventionalcommits.org/en/v1.0.0/ for tagging commits and pull requests to the best of your ability.

## Linux
- Install python 3.10 from here [here](https://www.python.org/downloads/).
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

### Sandbox

BASE FHIR URL: `https://staging-fhir.ecwcloud.com/fhir/r4/<practice>`

FHIR Capabilities URL: `https://staging-fhir.ecwcloud.com/fhir/r4/<practice>/metadata?_format=json`

### Production

`https://oauthserver.eclinicalworks.com/oauth/oauth2/authorize`

`https://oauthserver.eclinicalworks.com/oauth/oauth2/token`
