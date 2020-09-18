# Delphi API

Skip to the file API.md in the same directory to get information to use the api.

## How it Works

The project can be split into three parts. Two parts are deployed as Heroku Dyno's while the sync part is done manually.

## Intro

    a. The first part involves listening to past events and updating local storage.This is done using BigQuery.

    b. The second part is an API that acesses this storage to caclulate some stats and returns over a get method.

    c. The third part is a live web3 py event listener that grabs new events and updates local storage accordingly.

## Detailed Explanation

1.  Past Event Listener

    This is the mode where the project will connect to BigQuery and scan for all past events.

    It then uses an archive node to calculate APR in the past and stores this into a REDIS Storage.

    This currently takes about 12 minutes

    This process is usually run locally.

    You can run `poetry run python3 sync.py`, but please setup everything before hand. (this is usually run locally)

2.  API

    This mode is used to calculate realtime APY and Reward information based on local storage that has been updated from either the sync and listen stages.

    ` poetry run python3 wsgi.py`

3.  Live Event Listener

    This mode creates web3 contract event filters to listen into the main contract events.

    Whenever a new event is braodcasted it updates its local storage recalculating apr for the period between events.

    ` poetry run python3 listener.py`

## Set-up

You need the following credentials. Please copy .env.example into .env and set them all up

1. Infura ws url
2. Archive node https url
3. Google BigQuery and BigStorage credentials
4. Contract ABIS: already set up in .env.example (keep as is)
5. Contract Deployment Address: set up in .env.example

## Running

Each file can be run using `poetry run python3 filename`

1. First you need to populate your Redis storage. This is done by running `sync.py `This takes some time upto 15 minutes currently.
2. Now you are ready to launch the event listener by running `listener.py`
3. Finally you can run the api to get real time values from Redis using `wsgy.py`

## Deployment

## APi

Switch to master branch , push to heroku

## Listener

Switch to listener branch, push to heroku using `git push heroku listener:master`

### Stop

`heroku ps:scale worker=0`

### Start

`heroku ps:scale worker=1`
