

import os
import json
from helpers.constants import PATH_TO_EVIDENCE

def store_evidence_to_json_file(response, evidence_location):
    evidence = f"{PATH_TO_EVIDENCE}/{evidence_location}".replace(' ', '_')
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    with open(evidence, "w") as f:
            f.write(json.dumps(response))

def save_response_to_file(response, evidence_location):
    evidence = f"{PATH_TO_EVIDENCE}/{evidence_location}".replace(' ', '_')
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    with open(evidence, "w") as f:
        f.write(response)