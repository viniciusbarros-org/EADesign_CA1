# Sync and Async message aggregator

This project was created as part of the **Enterprise Architecture Design**

## Apps Diagram

![Async and Sync Stacks](/diagram.png)

## Strategies to collect information

### Performance

![Performance Strategy](/performance-strategy.png)

### Recovery time

![Recovery Time Strategy](/recovery-time-strategy.png)

## Report

To check the results of the performances a Flask website app was created.
The 3 reports consist of:
- Report 1 - Response time Sync vs Async
- Report 2 - Async - Response in function of the frequency of events
- Report 3 - Application Recovery times

To run it locally:
```sh 
python3 results/main.py
```

From there you'll be able to access:
- http://localhost:5000 (homepage)
- http://localhost:5000/report1 ()
- http://localhost:5000/report2 ()
- http://localhost:5000/report3 ()

The same "website" was deployed to **GCP** using **Cloud Functions**. Accessible at:
- https://europe-west1-chrome-pointer-261620.cloudfunctions.net/index
- https://europe-west1-chrome-pointer-261620.cloudfunctions.net/report1
- https://europe-west1-chrome-pointer-261620.cloudfunctions.net/report2
- https://europe-west1-chrome-pointer-261620.cloudfunctions.net/report3


### Prints of reports

#### Report 1

![Report 1](/results/examples/report1.png)

#### Report 2

![Report 2](/results/examples/report2.png)

#### Report 3

![Report 3](/results/examples/report3.png)