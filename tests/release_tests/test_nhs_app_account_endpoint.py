from helpers.api.apim_request import APIHelper
from helpers.evidence import save_evidence

def test_nhsapp_account(api_client, url):
    api_helper = APIHelper(api_client)

    ods_code = "T00001"
    pages = [1,2,3,4]
    
    for page in pages:
        response = api_helper.get_nhsapp_account(
            {
                "ods-organisation-code": ods_code,
                "page": page
            }
        )

        assert response.status_code == 200

        resp = response.json()

        assert resp.get("data").get("id") is not None
        assert resp.get("data").get("id") == ods_code
        assert resp.get("data").get("type") == "NhsAppAccounts"
        assert resp.get("data").get("attributes").get("accounts") is not None
        assert len(resp.get("data").get("attributes").get("accounts")) > 0
        for i in range(len(resp.get("data").get("attributes").get("accounts"))):
            assert resp.get("data").get("attributes").get("accounts")[i].get("NhsNumber") is not None
            assert resp.get("data").get("attributes").get("accounts")[i].get("NhsNumber") != ""
            assert resp.get("data").get("attributes").get("accounts")[i].get("NotificationsEnabled") is not None
        assert resp.get("links").get("self").startswith(url)
        assert resp.get("links").get("self") \
            .endswith(f"/channels/nhsapp/accounts?ods-organisation-code={ods_code}&page={page}")
        save_evidence(resp, f"NHSApp_Account/{ods_code}_page_{page}.json")
