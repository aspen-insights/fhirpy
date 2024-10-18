import pytest
from fhirpy.parse import get_first_name, get_last_name

pytestmark = pytest.mark.fhirapi


def test_get_first_name_official():
    data = [{"use": "official", "given": "John", "family": "Doe"}]
    assert get_first_name(data) == "John"


def test_get_first_name_no_official():
    data = [{"use": "nickname", "given": "Johnny", "family": "Doe"}]
    assert get_first_name(data) is None


def test_get_first_name_empty():
    data = []
    assert get_first_name(data) is None


def test_get_last_name_official():
    data = [{"use": "official", "given": "John", "family": "Doe"}]
    assert get_last_name(data) == "Doe"


def test_get_last_name_no_official():
    data = [{"use": "nickname", "given": "Johnny", "family": "Doe"}]
    assert get_last_name(data) is None


def test_get_last_name_empty():
    data = []
    assert get_last_name(data) is None
