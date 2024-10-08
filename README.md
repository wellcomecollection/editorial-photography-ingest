# editorial-photography-ingest

Tool for transferring editorial photography from Glacier Storage to Archivematica, so they can then be ingested into the storage-service. 

## Background

Editorial photography shoots are stored in Glacier Flexible Retrieval, and are to be imported into Archivematica
when each batch is ready.

Each batch is provided as a list of identifiers for the shoot.

Shoots consist of the photographs themselves, and some metadata  which is irrelevant for this purpose.

## Procedure
Starting with a file containing one shoot identifier per line:

1. Slice the input file into manageable chunks, that the downstream system can manage.  
Currently hardcoded as 20 in the Makefile `sliced` command.
```
make path_to/your_shoot_identifiers_file.sliced
```
2. Restore the shoots from Glacier using batch restore.  
The files are restored for 1 day by default.  
It will take several hours to restore the files.
```
AWS_PROFILE=platform-developer make path_to/a_slice_file.restored
```
3. When they have been successfully restored, run the tool to transfer from the editorial photography bucket to the ingest bucket.
```
AWS_PROFILE=digitisation-developer make path_to/a_slice_file.transferred.production
```
4. The receiving system may be down, so step 5 may need to be run, without having to restore again from step 2.  
You can use this [dashboard](https://c783b93d8b0b4b11900b5793cb2a1865.eu-west-1.aws.found.io:9243/s/storage-service/app/dashboards#/view/04532600-2dfc-11ed-8fbf-7d74cdf8bbb4?_g=(filters:!(),refreshInterval:(pause:!t,value:60000),time:(from:now-1d,to:now))) to check whether the files have been successfully ingested into the storage-service. Filter by `bag.info.externalIdentifier`, the bag's `status.id` should be `succeeded`.   

## When it goes wrong

### Touching transferred zips

If you cannot find your bag(s) in the above dashboard, the ingest may have failed for ephemeral reasons.
In this scenario, the shoot zip has been created and transferred to the transfer source bucket. 
It does not need to go through the whole restore-transfer process again.

Instead, the zip in the transfer source bucket can be "touched".  There are two approaches:

1. If there is a small number (<=20ish), you can trigger this update using `touch.py`. Feed it a file containing one S3 key to touch per line, thus:
```
AWS_PROFILE=digitisation-developer make path_to/your_list_of_S3_keys_to_touch.touched.production
```

2. If there are many, or Archivematica is already busy with other things, then this is better managed by the toucher Lambda.

```
cat path_to/your_list_of_S3_keys_to_touch | AWS_PROFILE=digitisation-developer client/queue_touches.py production
```

## How
See `Makefile` for more detail about each step 
1. Restoration is asynchronous and can be triggered from a command line.
2. Once restored, the transfer should be triggered. This will run on Lambda, driven by a queue.