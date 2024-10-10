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
    'filename,collection_reference,accession_number\\r\\nobjects/,WT,2754_CP000159\\r\\n'
    """
    writer = csv.DictWriter(
        csvfile, fieldnames=["filename", "collection_reference", "accession_number"]
    )
    writer.writeheader()
    writer.writerow(
        {
            "filename": "objects/",
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
    Move the contents of source directory into the target directory
    """
    os.makedirs(target_directory, exist_ok=True)
    for file_abspath in source_files:
        shutil.move(file_abspath, target_directory)


def full_paths(source_directory, filenames):
    """
    Prepends source_directory onto each filename in filenames

    >>> list(full_paths("/path/to", ["file1.erl", "file2.erl"]))
    ['/path/to/file1.erl', '/path/to/file2.erl']

    """
    return (os.path.join(source_directory, filename) for filename in filenames)


def make_zip_from(files, source_folder, target_folder, accession_id, suffix):
    os.makedirs(target_folder, exist_ok=True)
    return create_born_digital_zip(
        full_paths(source_folder, files),
        target_folder,
        accession_id + suffix,
    )


def create_born_digital_zip(source_files, target_directory: str, accession_id: str):
    accession_path = os.path.join(target_directory, accession_id)
    folder = create_born_digital_folder(source_files, accession_path, accession_id)
    return shutil.make_archive(accession_path, "zip", folder)


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


if __name__ == "__main__":
    import sys
    list(create_born_digital_zips(sys.argv[1], '.', "1234", sys.argv[2], 99))
