"""
Create zips from editorial photography folders for uploading to born-digital-accessions
"""

import csv
import shutil
import os
import itertools


def shoot_number_to_accession_id(accession_number, shoot_number):
    """
    The accession id is simply the shoot_number prefixed with the accession number
    >>> shoot_number_to_accession_id("2754", "CP000159")
    '2754_CP000159'
    """
    if accession_number and shoot_number:
        return accession_number + "_" + shoot_number
    else:
        raise ValueError(
            f"misssing accession or shoot number - accession: '{accession_number}' shoot: '{shoot_number}'"
        )


def generate_metadata_csv(csvfile, accession_id):
    """
    The metadata csv consists of a header and a single row
    The accession id is placed in the final cell
    >>> import io
    >>> generate_metadata_csv(io.StringIO(), shoot_number_to_accession_id("2754", "CP000159")).getvalue()
    'filename,collection_reference,accession_number\\r\\n/objects,WT,2754_CP000159\\r\\n'
    """
    writer = csv.DictWriter(
        csvfile, fieldnames=["filename", "collection_reference", "accession_number"]
    )
    writer.writeheader()
    writer.writerow(
        {
            "filename": "/objects",
            "collection_reference": "WT",
            "accession_number": accession_id,
        }
    )
    return csvfile


def create_born_digital_folder(source_files, target_directory, accession_id):
    os.makedirs(os.path.join(target_directory, "metadata"), exist_ok=True)
    with open(os.path.join(target_directory, "metadata", "metadata.csv"), "w") as csvfile:
        generate_metadata_csv(csvfile, accession_id)
    move_files_to_objects_folder(source_files, target_directory)
    return target_directory


def move_files_to_objects_folder(source_files, target_directory):
    """
    Move the contents of source directory into the objects subfolder in the target directory

    """
    os.makedirs(os.path.join(target_directory, "objects"))
    for file_abspath in source_files:
        shutil.move(file_abspath, os.path.join(target_directory, "objects"))


def files_in_folder(source_directory):
    """
    Return a list of relevant files in the given directory.
    """
    return [
        filename
        for filename in os.listdir(source_directory)
        if not discard_file(filename)
    ]


def full_paths(source_directory, filenames):
    """
    Prepends source_directory onto each filename in filenames

    >>> list(full_paths("/path/to", ["file1.erl", "file2.erl"]))
    ['/path/to/file1.erl', '/path/to/file2.erl']

    """
    return (os.path.join(source_directory, filename) for filename in filenames)


def create_born_digital_zips(
    source_directory, target_directory, accession_number, shoot_number, max_batch_size
):
    filenames = files_in_folder(source_directory)

    if len(filenames) == 0:
        raise FileNotFoundError(
            "Attempt to build born digital accession zip from empty folder"
        )

    if len(filenames) > max_batch_size:
        # In order to produce predictable/repeatable zips, the filename list is sorted before batching.
        # This is only necessary when an input directory results in multiple zips
        batches = batched(sorted(filenames), max_batch_size)
        for ix, batch in enumerate(batches, 1):
            accession_id = f"{shoot_number_to_accession_id(accession_number, shoot_number)}_{ix:03d}"
            yield create_born_digital_zip(
                full_paths(source_directory, batch),
                os.path.join(target_directory, accession_id),
                accession_id,
            )
    else:
        accession_id = shoot_number_to_accession_id(accession_number, shoot_number)
        yield create_born_digital_zip(
            full_paths(source_directory, filenames),
            os.path.join(target_directory, accession_id),
            accession_id,
        )


def create_born_digital_zip(source_files, target_directory, accession_id):
    folder = create_born_digital_folder(source_files, target_directory, accession_id)
    return shutil.make_archive(accession_id, "zip", folder)


# copied from itertools 3.12 documentation.
# When we start using Python >= 3.12, we can get rid of this
# but other applications nearby use 3, so I've shimmed it for now.


def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        yield batch


def discard_file(file):
    """
    The metadata files from the original upload are not wanted, and should be discarded
    shoot.csv is one such file...

    >>> discard_file("/path/to/shoot.csv")
    True

    ...as is an XML file that is eponymous with the shoot number.

    >>> discard_file("/path/to/CP_000159.xml")
    True

    For ease of writing, all XML files are discarded.

    >>> discard_file("/path/to/HelloWorld.xml")
    True

    The intent is to retain *.tif files...

    >>> discard_file("/path/to/C0007851.tif")
    False

    ...but this function focuses on discarding the files we know we don't want
    rather than retaining certain files, in case a future ingest needs to
    import other formats, such as video.

    >>> discard_file("/path/to/C0007851.mpg")
    False

    """
    return os.path.basename(file) == "shoot.csv" or file[-4:] == ".xml"
