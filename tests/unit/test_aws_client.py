import pytest

from helpers.aws.aws_client import AWSClient


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    return None


class StubLambdaClient:
    def __init__(self, existing_names):
        self.existing_names = set(existing_names)
        self.calls = []

    def update_env_var_if_exists(self, lambda_name, var_key, var_value):
        self.calls.append((lambda_name, var_key, var_value))
        return lambda_name in self.existing_names


def build_aws_client(existing_names):
    aws_client = AWSClient.__new__(AWSClient)
    aws_client.lambda_ = StubLambdaClient(existing_names)
    return aws_client


def test_reset_enrichment_lambda_cache_prefers_current_lambda_name():
    aws_client = build_aws_client({"comms-ref-api-requestenrichmentlambda-enrich"})

    aws_client.reset_enrichment_lambda_cache("ref")

    assert [call[0] for call in aws_client.lambda_.calls] == [
        "comms-ref-api-requestenrichmentlambda-enrich",
    ]


def test_reset_enrichment_lambda_cache_falls_back_to_legacy_lambda_name():
    aws_client = build_aws_client({"comms-ref-api-ecl-enrich"})

    aws_client.reset_enrichment_lambda_cache("ref")

    assert [call[0] for call in aws_client.lambda_.calls] == [
        "comms-ref-api-requestenrichmentlambda-enrich",
        "comms-ref-api-ecl-enrich",
    ]


def test_reset_enrichment_lambda_cache_raises_when_no_candidate_exists():
    aws_client = build_aws_client(set())

    with pytest.raises(RuntimeError, match="Unable to reset enrichment lambda cache"):
        aws_client.reset_enrichment_lambda_cache("ref")