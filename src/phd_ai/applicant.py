from __future__ import annotations

import json
from pathlib import Path


DEFAULT_APPLICANT_PROFILE_PATH = Path("applicant_profile.json")


def load_applicant_profile(profile_path: Path | None) -> dict:
    if profile_path is None or not profile_path.exists():
        return {}
    return json.loads(profile_path.read_text(encoding="utf-8"))


def save_applicant_profile(profile: dict, profile_path: Path) -> Path:
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return profile_path


def prompt_for_applicant_profile() -> dict:
    print("Enter applicant details for cover letter generation. Leave fields blank if you want to skip them.")

    full_name = input("Full name: ").strip()
    address_line_1 = input("Address line 1: ").strip()
    address_line_2 = input("Address line 2: ").strip()
    city = input("Town/City: ").strip()
    postcode = input("Postcode/ZIP: ").strip()
    country = input("Country: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    current_role = input("Current role or degree programme: ").strip()
    institution = input("Current institution: ").strip()
    english_variant = input("Preferred English (`UK` or `US`) [UK]: ").strip().upper() or "UK"
    if english_variant not in {"UK", "US"}:
        english_variant = "UK"

    return {
        "full_name": full_name,
        "address": {
            "line_1": address_line_1,
            "line_2": address_line_2,
            "city": city,
            "postcode": postcode,
            "country": country,
        },
        "email": email,
        "phone": phone,
        "current_role": current_role,
        "institution": institution,
        "english_variant": english_variant,
    }


def ensure_applicant_profile(profile_path: Path | None) -> tuple[dict, Path]:
    resolved_path = profile_path or DEFAULT_APPLICANT_PROFILE_PATH
    if resolved_path.exists():
        return load_applicant_profile(resolved_path), resolved_path

    print(f"No applicant profile found at {resolved_path}. Let's create one now.")
    profile = prompt_for_applicant_profile()
    save_applicant_profile(profile, resolved_path)
    return profile, resolved_path
