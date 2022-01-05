# DSBD_Server
Django Server module

## Brief info
This module is the _API Gateway_ the accepts (or rejects) all the requests coming from the Bot Client. It then forwards the
requests to the right module (in this case only one) and forwards its response to the Bot Client.

## Transaction and Rollback System
This module also contains the Transaction Orchestration which makes sure that the CSV File Upload process completes with no
database consistency issues (in case of failures).

![Transaction and Rollback System](https://i.imgur.com/YiGE02S.png "Transaction and Rollback System")