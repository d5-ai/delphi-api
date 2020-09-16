# Delphi API

## How it Works

The project can be split into two parts. One involved listening to events and updating local storage. The second part is an API that acesses this storage to caclulate some values.

1. Event Listener

a. Sync

This is the mode where the project will connect to BigQuery and scan for all past events.

It then uses an archive node to calculate APR in the past and stores this.

This currently takes about X minutes

b. Listen

This mode creates web3 contract event filters to listen into the main contract events.

Whenever a new event is braodcasted it updates its local storage recalculating apr for the period between events.

2. API

This mode is used to calcualte realtime APY and Reward information based on local storage that has been updated from either the sync and listen stages.

## Set-up

You need the following credentials. Please copy .env.example into .env and set them all up

1. Infura ws url
2. Archive node https url
3. Google BigQuery and BigStorage credentials
4. Contract ABIS: already set up in .env.example (keep as is)
5. Contract Deployment Address: set up in .env.example

## Running

First run `app.py` , enabling BigQuery sync, to creat local record. This takes some time. After the first run it will automatically go into listening for events. Please disable bq sync for the next run to save costs.

Now you can run `api.py` to host the flask api that acesses this storage and calculates rewards and apy
