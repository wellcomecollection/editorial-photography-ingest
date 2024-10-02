The Toucher is to be used when shoots fail within Archivematica, 
having been successfully transferred to the born-digital-ingest folder.

This happens occasionally because Archivematica can fail for ephemeral reasons
e.g. when it is a bit overworked.


The Toucher system consists of:

* The toucher Lambda itself
  * This touches Objects in the ingest folder
  * touching (i.e. a NOOP update) causes Archivematica to process the file again.
  * It pulls a manageable number of keys (10) from the input queue and invokes the toucher
* An input queue.  
  * Messages on here contain the keys of Objects to be touched.
* An Eventbridge scheduler.
  * This scheduler runs six times on weekdays between 0830 and 1730.
  * It invokes the toucher lambda
* A client script
  * Constructs the list of Object keys based on expected vs actually ingested shoots
  * Puts them on the queue


