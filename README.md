bigarms
=======

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

 # Update requirements
 make -C requirements/
```

## Deployment

Deploy dynamodb tables

```

# To deploy action log
make -C deployment deploy-actionlog
# deploy bigarms club
make -C deployment deploy-bigarmsclub
```

## Make Targets

The lambda is already deployed with a Twilio configuration as lambda variables, which can be updated by setting calling `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in the local environment and calling `make config`

`make test`: Run unit tests

`make start`: start a docker-compose network with a webserver front-end and dynamodb backend

`make open`: Open the homepage

`make fixtures` (run on host): load dynamo db data and fixtures into local mock

`make -b deployment/ package`: create zip files

`make -b deployment/ publish`: publish lambda zipfile