bigarms
=======

![Unit Tests](https://github.com/kindasimple/bigarms/actions/workflows/unit_test.yml/badge.svg)

This silly little API service that forwards SMS messages to a "Big Arms Club" group. SMS messages that are received at a registered Twilio number are recorded and forwarded to a group. An AWS lambda service processes the payload. The message is an emoji and a value, e.g. "💪10". The processed results are sent to stored in dynamo db, and the message is forwarded to the group.

There is also a lambda that retrieves dynamodb results as a leaderboard.

*Technologies:*

* dynamodb
* aws lambda
* aws api gateway
* docker

## Quickstart


The lambda is already deployed with a Twilio configuration as lambda variables, which can be updated by setting calling `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in the local environment and calling `make fn-configure-action-log`

`make test`: Run unit tests

`make start`: start a docker-compose network with a webserver front-end and dynamodb backend

`make open`: Open the homepage

`make fixtures` (run on host): load dynamo db data and fixtures into local mock


## Deployment

```
# Update requirements
make -C requirements/

# dynamodb tables
## Deploy a dynamodb table for storing log messages & statistics
make -C deployment/ deploy-db-actionlog
## Deploy a dynamodb table for storing bigarms clubs for pushups
make -C deployment/ deploy-db-bigarmsclub

# build function.zip
make -C deployment/ package

# source environment variables for make configuration
source ~/.env

# deploy lambda to AWS
make -C deployment/ fn-update-leaderboard
```

The api gateway needs to be set up manually. Create an API with a $default route that points at the `bigarms_api` lambda function. Create another API with a `/*/POST/message` endpoint with an integration request to the `replyMessages` lambda function
