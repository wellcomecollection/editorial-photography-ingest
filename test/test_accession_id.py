from transferrer.make_zip import shoot_number_to_accession_id
import pytest


def test_accession_id():
    assert shoot_number_to_accession_id("1234", "PB000123") == "1234_PB000123"


def test_no_accession_number():
    with pytest.raises(ValueError):
        shoot_number_to_accession_id("", "PB000123")


def test_no_shoot_number():
    with pytest.raises(ValueError):
        shoot_number_to_accession_id("1234", "")
