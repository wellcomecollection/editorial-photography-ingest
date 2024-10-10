import fnmatch
import os
import zipfile
import csv
import pytest
import glob

from transferrer.make_zip import make_zip_from


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
            "filename": "objects/",
            "collection_reference": "WT",
            "accession_number": accession_id,
        }
        assert not next(reader, False)  # The CSV should have only one row


def test_missing_folder(fs):
    """Trying to create an zip with files that do not exist will raise an exception"""
    with pytest.raises(FileNotFoundError):
        make_zip_from(["one.tif", "two.tif"], "/not_here", "/out", "1234_G00DCAFE", "")
    assert fnmatch.filter(os.listdir("."), "*zip") == []


def test_empty_folder(fs):
    """Trying to create an empty zip will not work"""
    fs.create_dir("/in")
    make_zip_from([], "/in", "/out", "1234_G00DCAFE", "")
    assert fnmatch.filter(os.listdir("."), "*zip") == []


def test_single_zip(fs):
    # When a shoot results in a single zip,
    populate_source_dir_with_images(fs, "G00DCAFE", 2)
    make_zip_from(os.listdir("/in"), "/in", "./out", "1234_G00DCAFE", "")
    # it creates a zip named using the accession and shoot numbers
    with zipfile.ZipFile("./out/1234_G00DCAFE.zip") as zip_file:
        zip_file.extractall("/unzipped")
        # with a metadata csv in the root of the zip
        assert_csv_has_accession_id("/unzipped/metadata/metadata.csv", "1234_G00DCAFE")
        # and the photos in an . folder
        assert os.path.exists("/unzipped/G00DCAFE_001.tif")
        assert os.path.exists("/unzipped/G00DCAFE_002.tif")

#