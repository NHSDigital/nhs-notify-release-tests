import pytest

from helpers.constants import get_account_id, get_comms_bucket_name


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    return None


def test_get_account_id_prefers_assumed_role_account(monkeypatch):
    monkeypatch.setenv("ACCOUNT_ID", "736102632839")
    monkeypatch.setenv("AWS_ACCOUNT_ID", "815490582396")

    assert get_account_id() == "815490582396"


def test_get_account_id_falls_back_to_requested_account(monkeypatch):
    monkeypatch.delenv("AWS_ACCOUNT_ID", raising=False)
    monkeypatch.setenv("ACCOUNT_ID", "736102632839")

    assert get_account_id() == "736102632839"


def test_get_account_id_raises_when_no_account_is_available(monkeypatch):
    monkeypatch.delenv("AWS_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("ACCOUNT_ID", raising=False)

    with pytest.raises(RuntimeError, match="AWS_ACCOUNT_ID or ACCOUNT_ID"):
        get_account_id()


def test_get_comms_bucket_name_uses_runtime_account(monkeypatch):
    monkeypatch.delenv("ACCOUNT_ID", raising=False)
    monkeypatch.setenv("AWS_ACCOUNT_ID", "815490582396")

    assert get_comms_bucket_name("ref", "api-stg-comms-mgr") == "comms-815490582396-eu-west-2-ref-api-stg-comms-mgr"