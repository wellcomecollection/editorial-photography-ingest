# editorial-photography-ingest

Tool for transferring editorial photography from Glacier Storage to Archivematica, so they can then be ingested into the storage-service. 

## Background

Editorial photography shoots are stored in Glacier Flexible Retrieval, and are to be imported into Archivematica
when each batch is ready.

Each batch is provided as a list of identifiers for the shoot.

Shoots consist of the photographs themselves, and some metadata  which is irrelevant for this purpose.

## Procedure

The Digital Production team provides us with a list of shoots to ingest.

1. Generate the list of expected ingests using [compile_expected_list.py](src/scripts/compile_expected_list.py). This will be useful to check the progress of the shoots through the pipeline.
2. Using the [start_restores.py](src/scripts/start_restores.py) script, queue the whole list of shoots. The S3 objects will be restored for 7 days, after which they will be moved back into Glacier Flexible Retrieval storage class. From the `restore_shoots` queue, shoots will automatically move through the pipeline at a rate that all systems involved can manage. 
3. Check the progress using [compile_pending_list.py](src/scripts/compile_pending_list.py) with the list of expected ingests generated in 1. Once all lines are marked as True, the job is done! 

See [diagrams](terraform/README.md) describing the components and flow. 

## When it goes wrong

Due to the nature of the data being handled, the limitations of lambda functions and the relative fragility of the target system (Archivematica), this pipeline has been built with retries in mind. See below for the most common failure scenarios:

### Large shoot fails to transfer

Shoots are downloaded from `wellcomecollection-editorial-photography` (platform account), then uploaded into `wellcomecollection-archivematica-transfer-source` (digitisation account) where Archivematica picks them up. The download/upload of some large shoots can exceed the maximum lambda timeout. In this case you will see that some parts of the shoot have been transferred while others failed to do so. 
Take a large shoot CP003524 that is meant to result in the following bags:
```
CP003524_001
CP003524_002
CP003524_003
CP003524_004
```
If the lambda times out before `_003` and `_004` have been transferred, the original message will end up on `transfer-shoots-production_dlq`. Simply redrive this message to `queue_shoot_transfers-production` so that the transfer is attempted again. The transfer lambda checks whether a shoot/part is already in the target bucket before starting the download/upload so the amount of data to move will be less the second time around. 

### Archivematica fails to process the bag

In this scenario, the shoot zip(s) has been created and transferred to the transfer source bucket, but failed at some point in Archivematica (could be marked as "failed", or nowhere to be found in the storage-service).
It does not need to go through the whole restore-transfer process again.

Instead, the zip in the transfer source bucket can be ["touched"](terraform/modules/toucher_lambda/README.md). Essentially we make it look like the zip was just uploaded, which prompt Archivematica to process it again.

1. Generate a list of "touchable" S3 keys using [compile_touchable](src/scripts/compile_touchable.py). 

2. Feed the list to [start_touches.py](src/scripts/start_touches.py) to queue the S3 objects to be touched.