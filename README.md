# editorial-photography-ingest

Tool for transferring editorial photography from Glacier Storage to Archivematica.

## Background

Editorial photography shoots are stored in Glacier Flexible Retrieval, and are to be imported into Archivematica
when each batch is ready.

Each batch is provided as a list of identifiers for the shoot.

Shoots consist of the photographs themselves, and some metadata  which is irrelevant for this purpose.

## Procedure

1. Restore the shoots from Glacier using batch restore
2. When they have been successfully restored, run the tool to transfer from the editorial photography bucket to the ingest bucket
3. The receiving system may be down, so step 2 may need to be retried, without having to restore again from step 1

## How

1. Restoration is asynchronous and can be triggered from a command line.
2. Once restored, the transfer should be triggered. This will run on Lambda, driven by a queue.