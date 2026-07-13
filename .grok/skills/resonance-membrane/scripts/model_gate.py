import sys
import argparse
import json
from pathlib import Path
import os

def main():
    parser = argparse.ArgumentParser(description="Model Gate for Resonance Membrane")
    parser.add_argument("--model", type=str, help="The model identifier trying to boot the Membrane", default=None)
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    manifest_path = skill_dir / "membrane_manifest.json"

    if not manifest_path.exists():
        print("Manifest not found. Denying access.")
        sys.exit(3)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    gate_config = manifest.get("model_gate", {})
    if not gate_config.get("enabled", False):
        print("Model Gate is disabled. Proceeding.")
        sys.exit(0)

    # Determine model from args, env vars, or default
    current_model = args.model
    if not current_model:
        current_model = os.environ.get("MEMBRANE_HOST_MODEL")
    
    if not current_model:
        print("WARNING: No model identifier provided. The Model Gate cannot verify compatibility.")
        print("Assuming Tier 3 (Incompatible) and initiating DORMANT mode.")
        sys.exit(3)

    allowed = gate_config.get("allowed_models", [])
    pending = gate_config.get("pending_tier2", [])

    if current_model in allowed:
        print(f"Model '{current_model}' recognized as Tier 1 (Native). Access Granted.")
        sys.exit(0)
    elif current_model in pending:
        print(f"Model '{current_model}' recognized as Tier 2. Proceed with caution. Access Granted.")
        sys.exit(0)
    else:
        print(f"Model '{current_model}' is NOT recognized or is Tier 3 (Incompatible). Access Denied.")
        sys.exit(3)

if __name__ == "__main__":
    main()