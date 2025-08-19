

import os
import json
from helpers.constants import PATH_TO_EVIDENCE

def save_response_to_json_file(response, evidence_location):
    evidence = f"{PATH_TO_EVIDENCE}/{evidence_location}".replace(' ', '_')
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    with open(evidence, "w") as f:
            f.write(json.dumps(response))

def save_response_to_file(response, evidence_location):
    evidence = f"{PATH_TO_EVIDENCE}/{evidence_location}".replace(' ', '_')
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    with open(evidence, "w") as f:
        f.write(response)

def save_response_to_pdf_file(pdf, evidence_location):
    evidence = f"{PATH_TO_EVIDENCE}/{evidence_location}".replace(' ', '_')
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    # If pdf is a BytesIO object, get its bytes
    if hasattr(pdf, "getvalue"):
        pdf_bytes = pdf.getvalue()
    else:
        pdf_bytes = pdf
    with open(evidence, "wb") as f:
        f.write(pdf_bytes)