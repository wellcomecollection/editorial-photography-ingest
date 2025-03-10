from unittest import mock

import pytest
from mediagraph import *
from requests import Session, Response


@mock.patch.multiple(
    Mediagraph,
    get_shoot_collection=lambda _self, _id: [{"id": 123456, "visible_assets_count": 3, "name": "CP 5318008: hello"}],
    get_collection_assets=lambda _self, _id: {"ids":[1234567,1234568,1234569]}
)
def test_list_assets():
    """
    The pertinent shoot data is a list of the asset identifiers
    that make up the Mediagraph Collection corrsponding to the given shoot
    """

    m = Mediagraph("", "")
    result = m.get_shoot_data("CP 5318008")
    assert result == ('CP 5318008', {'collection': 123456, 'assets': [1234567, 1234568, 1234569]})


@mock.patch.object(Mediagraph, attribute="get_shoot_collection", return_value=[])
def test_empty_shoot(_):
    """
    An empty list may be returned if the shoot does not exist on Mediagraph
    """
    result = Mediagraph("","").get_shoot_data("CP 123456")
    assert result[0] == 'CP 123456'
    assert isinstance(result[1], MissingCollectionError)


@mock.patch.object(Mediagraph, attribute="get_shoot_collection", return_value=[{"id": 123456}, {"id": 56789}])
def test_multiple_shoots(_):
    """
    Multiple collections may be returned by mediagraph from a search for the shoot number.
    These may be legitimate duplicates, e.g. where a shoot is in "unknown year" as well as
    the correct year.

    Or it may be because that shoot number forms part the name of a different collection.
    One example of this is when the input shoot number has been mistyped and truncated.
    In that situation, CP 12345 will match CP 123456 and CP 123457 etc.

    This is a scenario that requires a human to check it.
    """
    result = Mediagraph("","").get_shoot_data("CP 654321")
    assert result[0] == 'CP 654321'
    assert isinstance(result[1], TooManyCollectionsError)


@mock.patch.object(Mediagraph, attribute="get_shoot_collection", return_value=[{"id": 1, "name": "CP 123456: hello"}])
def test_dodgy_shoot_name(_):
    """
    As with test_multiple_shoots, the requested shoot number may be found in the names of other shoots.
    Particularly if it has been truncated on input.

    To guard against deleting the wrong thing, get_shoot_data checks that the whole shoot number is followed
    immediately by a colon at the start of the collection name.  This prevents those truncated shoot numbers
    causing a problem even when there is only one match.
    """
    result = Mediagraph("","").get_shoot_data("CP 12345")
    assert result[0] == 'CP 12345'
    assert isinstance(result[1], UnexpectedCollectionNameError)

@mock.patch.multiple(
    Mediagraph,
    get_shoot_collection=lambda _self, _id: [{"id": 123456, "visible_assets_count": 5, "name": "CP 999999: hello"}],
    get_collection_assets=lambda _self, _id: {"ids":[1234567,1234568,1234569]}
)
def test_asset_count_mismatch():
    """
    This is not a problem I have seen in real data, but to ensure that the second request has actually
    returned the data expected based on what we know about the first one, get_shoot_data checks that
    the right number of assets is returned.
    """
    m = Mediagraph("", "")
    result = m.get_shoot_data("CP 999999")
    assert result[0] == 'CP 999999'
    assert isinstance(result[1], AssetCountError)

@mock.patch.object(Mediagraph, attribute="get_shoot_collection", side_effect=FloatingPointError("No"))
def test_unexpected_error(_):
    """
    Other things may go wrong, e.g. if Mediagraph returns an unsuccessful response for some reason
    This is reported alongside any other exceptions.
    """
    m = Mediagraph("","")
    result = m.get_shoot_data("CP 999999")
    assert result[0] == 'CP 999999'
    assert isinstance(result[1], FloatingPointError)

@mock.patch.object(Session, attribute="delete", side_effect=FloatingPointError("No"))
def test_delete_exception(_):
    """
    If an exception is raised during deletion,
    the success value will be False,
    and the exception is returned as the "data" part of the return value
    """
    m = Mediagraph("","")
    result = m.delete_collection("CP 999999", 12345, [56789,45678])
    assert result[0] == 'CP 999999'
    assert result[1] == False
    assert isinstance(result[2], FloatingPointError)


@pytest.mark.parametrize("hint, urls_to_status_codes, success",
    [
        (
            "total failure",
            {
                'https://api.mediagraph.io/api/assets/45678': 400,
                'https://api.mediagraph.io/api/assets/56789': 400,
                'https://api.mediagraph.io/api/collections/12345': 400
            },
            False
        ),
        (
            "asset failure",
            {
                'https://api.mediagraph.io/api/assets/45678': 200,
                'https://api.mediagraph.io/api/assets/56789': 400,
                'https://api.mediagraph.io/api/collections/12345': 204
            },
            False
        ),
        (
            "collection failure",
            {
                'https://api.mediagraph.io/api/assets/45678': 200,
                'https://api.mediagraph.io/api/assets/56789': 200,
                'https://api.mediagraph.io/api/collections/12345': 422
            },
            False
        ),
        (
            "no problems",
            {
                'https://api.mediagraph.io/api/assets/45678': 200,
                'https://api.mediagraph.io/api/assets/56789': 200,
                'https://api.mediagraph.io/api/collections/12345': 204
            },
            True
        )

    ]
)
def test_delete(hint, urls_to_status_codes, success):
    """
    If the responses from Mediagraph are not OK,
    the success value will be False,
    the data part of the return value maps the URL to the status code.
    """

    def generate_delete_response(url):
        mock_response = mock.Mock(spec=Response)
        response_code = urls_to_status_codes[url]
        mock_response.status_code = response_code
        mock_response.url = url
        mock_response.ok = response_code in [200, 204]
        return mock_response

    with mock.patch.object(Session, attribute="delete") as mock_delete:
        mock_delete.side_effect = generate_delete_response
        m = Mediagraph("","")
        result = m.delete_collection("CP 999999", 12345, [56789,45678])
        assert result[0] == 'CP 999999'
        assert result[1] == success
        assert result[2] == urls_to_status_codes