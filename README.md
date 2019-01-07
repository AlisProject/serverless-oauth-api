# Serverless OAuth API

OAuth API for ALIS with backed Authlete.

## Setup

Install this project
```bash
# Install this project
$ git clone git@github.com:horike37/serverless-python-development-kit.git
$ cd serverless-python-development-kit
$ npm install

# Setup libraries
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

Edit enviroment variables

```bash
# Create .envrc to suit your environment.
$ cp -pr .envrc.sample .envrc
$ vi .envrc # edit

# allow
$ direnv allow
```


## Test

Run Unit test
```bash
$ pytest tests/unit/ -s
```

Run Integration test
```bash
$ pytest tests/integration/ --stage $INTEGRATION_TEST_STAGE --region $AWS_DEFAULT_REGION -s
```

## Release
This project includes DB and API stack. You can deploy each stack with tagging with `db-` prefix or `api-` to GitHub.

```bash
$ git tag db-1.0.0
$ git push origin db-1.0.0
$ git tag api-1.0.0
$ git push origin api-1.0.0
```
