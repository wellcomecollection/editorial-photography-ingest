from src.transferrer.transfer import transfer_shoot
import os


def test_transfer_single_batch_shoot(moto_session, available_shoot_bucket, target_bucket, fs):
    """
    When a shoot fits into a single package, it should be uploaded in a zip named by
    concatenating the accession number and shoot number only.
    """
    transfer_shoot(moto_session, moto_session, "PITEST", "1234")
    assert [o.key for o in target_bucket.objects.all()] == ['born-digital-accessions/1234_PITEST.zip']


def test_transfer_large_shoot(moto_session, huge_shoot_bucket, target_bucket, fs):
    """
    "large" shoots are those that cannot be uploaded in a single package.
    In theory, there is a number of objects constraint on sending to Archivematica,
    but there is also a size on disk constraint present in Lambda, so this is likely
    to be hit first, given the nature of the objects in question.

    For this test, a small number of small objects and a small filesystem stand in for
    the large numbers of large files on a not-quite-big-enough filesystem.

    There are five objects in huge_shoot_bucket.  They are all 10000B.
    By setting max_batch_size to 35000, we expect them to be uploaded in two batches
    one containing three and the other two images.

    When a shoot needs to be transferred in multiple batches, each batch is to be suffixed
    with a three digit sequence number.
    """
    fs.set_disk_usage(70000)
    transfer_shoot(moto_session, moto_session, "PITEST", "1234", max_batch_bytes=35000)
    sizes = {o.key: o.size for o in target_bucket.objects.all()}
    assert len(sizes) == 2
    assert sizes['born-digital-accessions/1234_PITEST_001.zip'] > sizes['born-digital-accessions/1234_PITEST_002.zip']


