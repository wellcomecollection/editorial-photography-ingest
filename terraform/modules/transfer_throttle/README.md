# Transfer throttle

The transfer throttle moves messages from the restored queue to the transfer queue,
in batches of a suitable size for Archivematica to handle.
It runs when Archivematica starts in the morning, and spreads the load across the day

## Why

This exists for two reasons:

* Restoration takes up to 12 hours
* Archivematica needs to be fed slowly over the day

