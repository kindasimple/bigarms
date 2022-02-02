bigarms
=======

![example workflow](https://github.com/kindasimple/bigarms/actions/workflows/unit_test.yml/badge.svg)

This silly little service recieves messages forwarded from twillio and processes the payload. The message is an emoji and a value. The results are stored in dynamo db. It has a front-end that retrieves dynamodb results as a dashboard.

*Technologies:*

* dynamodb
* aws lambda
* aws api gateway
* docker

## Quickstart


```
 # run unit tests with tox
 make test
```

## Deployment

```
# Update requirements
make -C requirements/
# dynamodb tables

# To deploy action log
make -C deployment/ deploy-db-actionlog
# deploy bigarms club
make -C deployment/ deploy-db-bigarmsclub

# build function.zip
make -C deployment/ package

# deploy lambda to AWS
make -C deployment/ publish
```

## Make Targets

The lambda is already deployed with a Twilio configuration as lambda variables, which can be updated by setting calling `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in the local environment and calling `make config`

`make test`: Run unit tests

`make start`: start a docker-compose network with a webserver front-end and dynamodb backend

`make open`: Open the homepage

`make fixtures` (run on host): load dynamo db data and fixtures into local mock

## Build requirements
docker-compose run

