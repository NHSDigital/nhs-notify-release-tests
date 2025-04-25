import pytest
from helpers.aws_client import AWSClient
from helpers.generators import Generators

def test_dynamodb_query(api_client):
    # Create request item
    body = Generators.generate_single_message_body("test ddb query")
    response = api_client.post_single_message(body)
    assert response.status_code == 201
    request_item_id = response.json().get("data").get("id")

    # Query request item
    aws_client = AWSClient(region_name="eu-west-2")
    table_name = "comms-uat-api-stg-comms-mgr"
    key_condition = "PK = :PK"
    expression_values = {
        ":PK": {"S": f"REQUEST_ITEM#{request_item_id}"}
    }
    result = aws_client.query_dynamodb(table_name, key_condition, expression_values)
    
    assert len(result) > 0  # Make sure there are some results

# Checks for existing files so if TTL has expired this test will fail.
def test_s3_file_contents():
    aws_client = AWSClient(region_name="eu-west-2")
    # S3 Bucket that contains letter supplier csvs
    bucket_name = "comms-736102632839-eu-west-2-uat-api-lspl-letter-csv"
    # Paths to the letter supplier csv locations
    prefix = [
        "PRECISIONPROCO/uploaded/pp-release-testing/",
        "MBA/uploaded/hh-release-testing/",
        "SYNERTEC/uploaded/synertec-release-testing/"
    ]
    # On request item plan for a successful channel request item should have batchId field in dynamo will contain the file name
    batchId = "testing"
    
    # Iterate over available letter supplier locations and assert that available csvs contain expected content
    files = aws_client.list_s3_bucket_contents(bucket_name, prefix[0])
    file_key = next(
        obj['Key'] 
        for obj in files
        if batchId in obj['Key'] and "MANIFEST" not in obj['Key']
    )
    content = aws_client.get_s3_object(bucket_name, file_key)

    assert "Letter" in content