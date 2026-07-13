import sys
import argparse
import json
from pathlib import Path
import os


def manifest_path_for(skill_dir: Path) -> Path | None:
    for candidate in (
        skill_dir / "references" / "membrane_manifest.json",
        skill_dir / "membrane_manifest.json",
    ):
        if candidate.exists():
            return candidate
    return None


def load_gate_config(skill_dir: Path) -> dict | None:
    path = manifest_path_for(skill_dir)
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest.get("model_gate", {})


def resolve_host_model(explicit_model: str | None) -> str | None:
    if explicit_model:
        return explicit_model
    for env_key in ("MEMBRANE_HOST_MODEL", "GROK_MODEL", "CURSOR_MODEL"):
        value = os.environ.get(env_key, "").strip()
        if value:
            return value
    return None


def cmd_verify_model(
    skill_dir: Path,
    explicit_model: str | None = None,
    *,
    strict: bool = True,
) -> int:
    gate_config = load_gate_config(skill_dir)
    if gate_config is None:
        print("Manifest not found. Denying access.")
        return 3

    if not gate_config.get("enabled", False):
        print("Model Gate is disabled. Proceeding.")
        return 0

    current_model = resolve_host_model(explicit_model)
    if not current_model:
        print("WARNING: No model identifier provided. The Model Gate cannot verify compatibility.")
        if strict:
            print("Assuming Tier 3 (Incompatible) and initiating DORMANT mode.")
            return 3
        print("Non-strict mode: proceeding without model verification.")
        return 0

    allowed = gate_config.get("allowed_models", [])
    pending = gate_config.get("pending_tier2", [])

    if current_model in allowed:
        print(f"Model '{current_model}' recognized as Tier 1 (Native). Access Granted.")
        return 0

    if current_model in pending:
        if os.environ.get("MEMBRANE_ALLOW_TIER2", "").strip() == "1":
            print(f"Model '{current_model}' recognized as Tier 2 (explicit override). Access Granted.")
            return 0
        print(
            f"Model '{current_model}' is Tier 2 — blocked until Architect local tests pass. "
            "Set MEMBRANE_ALLOW_TIER2=1 after verification."
        )
        return 3

    print(f"Model '{current_model}' is NOT recognized or is Tier 3 (Incompatible). Access Denied.")
    return 3


def main():
    parser = argparse.ArgumentParser(description="Model Gate for Resonance Membrane")
    parser.add_argument(
        "--model",
        type=str,
        help="The model identifier trying to boot the Membrane",
        default=None,
    )
    parser.add_argument(
        "--skill-dir",
        type=str,
        default=None,
        help="Path to resonance-membrane skill folder",
    )
    parser.add_argument(
        "--non-strict",
        action="store_true",
        help="Allow boot when host model cannot be detected",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else Path(__file__).parent.parent
    sys.exit(
        cmd_verify_model(
            skill_dir,
            args.model,
            strict=not args.non_strict,
        )
    )


if __name__ == "__main__":
    main()