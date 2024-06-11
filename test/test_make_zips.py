import fnmatch
import os
import zipfile
import csv
import pytest

from transferrer.make_zip import create_born_digital_zips


def populate_source_dir_with_images(fs, name, count):
    populate_source_dir(fs, (f"/in/{name}_{ix:03d}.tif" for ix in range(1, count + 1)))


def populate_source_dir(fs, filenames):
    for filename in filenames:
        fs.create_file(filename)


def assert_csv_has_accession_id(csv_path, accession_id):
    """
    Checks that a metadata.csv has the correct format, and that the accession number matches the expected value
    """
    with open(csv_path, "r") as csv_file:
        reader = csv.DictReader(
            csv_file
        )  # Ensures that the header row is present and correct
        assert next(reader) == {
            "filename": "/objects",
            "collection_reference": "WT",
            "accession_number": accession_id,
        }
        assert not next(reader, False)  # The CSV should have only one row


def test_missing_folder(fs):
    with pytest.raises(FileNotFoundError):
        list(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 10))
    assert fnmatch.filter(os.listdir("."), "*zip") == []


def test_empty_folder(fs):
    fs.create_dir("/in")
    with pytest.raises(FileNotFoundError):
        list(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 10))
    assert fnmatch.filter(os.listdir("."), "*zip") == []


def test_single_zip(fs):
    # When a shoot results in a single zip,
    populate_source_dir_with_images(fs, "G00DCAFE", 2)
    next(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 10))
    # it creates a zip named using the accession and shoot numbers
    with zipfile.ZipFile("./1234_G00DCAFE.zip") as zip_file:
        zip_file.extractall("/unzipped")
        # with a metadata csv in the root of the zip
        assert_csv_has_accession_id("/unzipped/metadata/metadata.csv", "1234_G00DCAFE")
        # and the photos in an ./objects folder
        assert os.path.exists("/unzipped/objects/G00DCAFE_001.tif")
        assert os.path.exists("/unzipped/objects/G00DCAFE_002.tif")


def test_multiple_zips(fs):
    # When a shoot results in multiple zips,
    populate_source_dir_with_images(fs, "BBB", 10)
    populate_source_dir_with_images(fs, "AAA", 10)

    list(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 10))
    # it creates zips named using the accession and shoot numbers, with a three-digit numeric suffix
    with zipfile.ZipFile("./1234_G00DCAFE_001.zip") as zip_file:
        zip_file.extractall("/unzipped_001")
        assert_csv_has_accession_id("/unzipped_001/metadata/metadata.csv", "1234_G00DCAFE_001")
        # The objects chosen for each zip are predictable and consistent.
        # They are sorted alphanumerically before being sliced into groups to place into each zip
        objects = os.listdir("/unzipped_001/objects")
        assert len(objects) == 10
        assert set(filename[:3] for filename in objects) == {"AAA"}

    with zipfile.ZipFile("./1234_G00DCAFE_002.zip") as zip_file:
        zip_file.extractall("/unzipped_002")
        assert_csv_has_accession_id("/unzipped_002/metadata/metadata.csv", "1234_G00DCAFE_002")
        objects = os.listdir("/unzipped_002/objects")
        assert len(objects) == 10
        assert set(filename[:3] for filename in objects) == {"BBB"}


# The metadata files (shoot.csv, *.xml) present in the original shoot are to be ignored
# They are not expected to be restored/downloaded, but if they are present, then they
# will not be included in the zips.
# The application behaves    entirely as though they are not there
def test_ignored_files_empty_folder(fs):
    populate_source_dir(fs, ("shoot.csv", "HELLO.xml"))
    fs.create_dir("/in")
    with pytest.raises(FileNotFoundError):
        list(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 10))
    assert fnmatch.filter(os.listdir("."), "*zip") == []


def test_ignored_files_single_zip(fs):
    populate_source_dir_with_images(fs, "HELLO", 10)
    populate_source_dir(fs, ("shoot.csv", "HELLO.xml"))
    list(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 10))
    assert fnmatch.filter(os.listdir("."), "*zip") == ["1234_G00DCAFE.zip"]


def test_ignored_files_multiple_zips(fs):
    populate_source_dir_with_images(fs, "HELLO", 20)
    populate_source_dir(fs, ("shoot.csv", "HELLO.xml"))
    list(create_born_digital_zips("/in", "/out", "1234", "G00DCAFE", 5))
    zips = fnmatch.filter(os.listdir("."), "*zip")
    # 20/5 == 4, ceil 22/5 > 4
    assert len(zips) == 4
