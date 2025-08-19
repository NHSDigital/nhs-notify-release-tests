import os
import json
from helpers.constants import PATH_TO_EVIDENCE

def save_evidence(response, evidence_location):
    evidence = f"{PATH_TO_EVIDENCE}/{evidence_location}".replace(' ', '_')
    os.makedirs(os.path.dirname(evidence), exist_ok=True)
    ext = os.path.splitext(evidence)[1].lower()

    if ext == ".json":
        with open(evidence, "w") as f:
            f.write(json.dumps(response, indent=2))
    elif ext in [".pdf", ".png"]:
        if hasattr(response, "getvalue"):
            data = response.getvalue()
        else:
            data = response
        with open(evidence, "wb") as f:
            f.write(data)
    elif ext == ".csv":
        if isinstance(response, bytes):
            with open(evidence, "wb") as f:
                f.write(response)
        else:
            with open(evidence, "w") as f:
                f.write(response)