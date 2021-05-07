import pytest

from src.s3 import parse_s3


def test_parse_s3_happy():
    s3_path = "s3://test_bucket/test_filename.csv"
    tuple_true = ("test_bucket", "test_filename.csv")
    tuple_test = parse_s3(s3_path)
    assert tuple_test == tuple_true


def test_parse_s3_unhappy():
    s3_path = "invalid/path_to_file"
    with pytest.raises(AttributeError):
        parse_s3(s3_path)
