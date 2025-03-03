# HOWTO: Delete a shoot collection from Mediagraph

Deleting a shoot from Mediagraph consists of two steps.

1. get the information about the collection and its assets 
2. use that information to delete them

## Prerequisites

Set the following environment variables:

MEDIAGRAPH_ORG=
MEDIAGRAPH_TOKEN=

See https://docs.mediagraph.io for details on getting the values for these.

## Get the information

This is done first, and as a separate step, for three reasons:

1. In case there is anything that needs to be checked by a human, 
   * This is because the correspondence between shoot and collection is by the shoot number
       matching the first part of the title. This can lead to false positives, and there are some unexpected duplicates 
       in Mediagraph that need to be verified before the actual deletion takes place.
2.  To minimise the risk when Mediagraph refuses to service some requests
    * When this was first run, it appears that Mediagraph would handle roughly 1000 shoots, then
      decline all subsequent requests 
3.  It allows a PoLP approach, where a user without delete permissions can prepare the data before running the deletion.

Provide a line-separated list of shoot numbers on STDIN to list_shoot_assets, thus:
```commandline
echo 'CP 12345
CP 67890' | python list_shoot_assets.py > shoot_assets_example.json
```

Anything that needs to be checked will be reported to STDERR, any shoots that were found without issue will be reported
to STDOUT.

To get the details for a single shoot.

## Delete the collections

```commandline
cat shoot_assets_example.json | python delete_collections.py
```

This performs the deletion and reports on how it went.  The results are in JSON, thus.

```json
{
  "CP 67890": {
    "success": true,
    "results": {
      "https://api.mediagraph.io/api/assets/1234567": 200,
      "https://api.mediagraph.io/api/collections/9876543": 204
    }
  }
}
```
