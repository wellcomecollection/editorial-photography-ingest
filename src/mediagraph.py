
import requests
from urllib.parse import urlencode


class MediagraphError(RuntimeError):
    def __init__(self, shoot_number, reason):
        super().__init__( f"{shoot_number}: {reason}")

class TooManyCollectionsError(MediagraphError):
    def __init__(self, shoot_number, collection_ids):
        super().__init__(shoot_number, f"More than one collection found: {', '.join(collection_ids)}")

class MissingCollectionError(MediagraphError):
    def __init__(self, shoot_number):
        super().__init__(shoot_number, "No collection found")

class UnexpectedCollectionNameError(MediagraphError):
    def __init__(self, shoot_number, collection_name):
        super().__init__(shoot_number, f"Collection name does not look right {collection_name}")

class AssetCountError(MediagraphError):
    pass

class ServerError(RuntimeError):
    pass


class Mediagraph:
    def __init__(self, api_token, org_number):
        self.org_number = org_number
        self.session = requests.Session()
        self.session.auth = ("", api_token)
        self.session.headers.update({"OrganizationId": self.org_number})


    @staticmethod
    def _validate_response(response):
        # If Mediagraph responds with something other than 200, we don't know what to do,
        # The most likely reason is a 500 error, having overwhelmed it, so rather than
        # continuing or retrying, we should just quit.
        if response.status_code != 200:
            raise ServerError(f"{response.status_code}: {response.reason}")
        return response

    def get_shoot_collection(self, shoot_number):
        # A shoot should be a collection whose title starts with the shoot number.
        # The only way to find this is by a search.
        # q searches in Collection names, but not necessarily at the beginning of the name,
        # so there is a possibility for a clash, if someone has included a different shoot as
        # part of another collection's name.
        querystring = urlencode({"q": shoot_number})
        return self._validate_response(
            self.session.get(f"https://api.mediagraph.io/api/collections?{querystring}")
        ).json()

    def get_collection_assets(self, collection_id):
        querystring = urlencode({"collection_id": collection_id, "all_ids": True})
        response = self._validate_response(
            self.session.get(f"https://api.mediagraph.io/api/assets/search?{querystring}")
        )
        return response.json()

    def get_shoot_data(self, shoot_number):
        """
        Get the collection and assets that correspond to a shoot.

        :param shoot_number: (typically begins with CP or EP)
        """
        try:
            # first get the shoot.  This corresponds to a Collection in Mediagraph.
            collections = self.get_shoot_collection(shoot_number)
            # There should be only one.
            # If there are none, then someone needs to find the corresponding shoot manually
            # If there are more, then someone needs to work out which one to delete
            if not collections:
                raise MissingCollectionError(shoot_number)

            if len(collections) >  1:
                raise TooManyCollectionsError(shoot_number, [str(c['id']) for c in collections])

            collection = collections[0]
            if not collection['name'].startswith(f"{shoot_number}:"):
                raise UnexpectedCollectionNameError(shoot_number, ['collection_name'])
            # then get all the assets in that shoot (i.e. with the shoot's id)
            assets = self.get_collection_assets(collection['id'])
            visible_assets = collection['visible_assets_count']
            returned_entries = len(assets['ids'])
            # The number of assets should match the visible assets count of the collection
            if visible_assets != returned_entries:
                # if not, a human needs to work out why.
                raise AssetCountError(shoot_number, f"{collection['id']}: {visible_assets} != {returned_entries}")
            return shoot_number, {'collection': collection['id'], 'assets':assets['ids']}
        except Exception as e:
            return shoot_number, e


    def delete_collection(self, shoot_number, collection_id, asset_ids):
        """
        Delete a collection and its contents from Mediagraph.

        Two things have to happen here:
        * delete the assets that make up a collection
        * delete the collection itself.

        A Mediagraph collection is not a container in the sense that the assets belong to it.  As such, in order to genuinely
        delete a collection, the assets also have to be deleted independently.

        Doing so will result in an empty collection sitting on Mediagraph, so the collection itself also needs to be
        deleted.

        According to the documentation, collections themselves are [not actually deletable via the API](https://docs.mediagraph.io/#tag/Collections),
        but they are [deletable through the UI](https://damsoftware.zendesk.com/hc/en-us/articles/4411539744532-Delete-a-Collection)

        It turns out that they can be deleted through the API, it's just undocumented, which is risky, as this functionality
        could be removed at any time, but it works for now.

        """
        try:
            responses = [
                self.session.delete(f"https://api.mediagraph.io/api/assets/{asset}") for asset in asset_ids
            ]  + [self.session.delete(f"https://api.mediagraph.io/api/collections/{collection_id}")]
            success = all(response.ok for response in responses)
            return shoot_number, success, {response.url: response.status_code for response in responses}
        except Exception as e:
            return shoot_number, False, e