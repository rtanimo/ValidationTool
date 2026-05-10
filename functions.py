import re
import pandas as pd
from rapidfuzz import process, fuzz


def normalize_text(text, replacements):
    if pd.isna(text):
        return ""

    text = str(text).lower()

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def build_full_address(row):
    parts = [
        row.get("address", ""),
        row.get("city", ""),
        row.get("state", ""),
        row.get("zip", ""),
    ]

    parts = [str(p).strip() for p in parts if pd.notna(p) and str(p).strip() != ""]

    return " ".join(parts)


def normalize_company(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()

    replacements = {
        " corporation": "",
        " corp": "",
        " inc": "",
        " llc": "",
        ".": "",
        ",": "",
    }

    name = normalize_text(name, replacements)

    name = re.sub(r"\s+", " ", name)

    return name.strip()


def normalize_address(address):
    if pd.isna(address):
        return ""

    address = str(address).lower()

    # normalize unit markers
    address = re.sub(r"(#|apt\.?|apartment|suite|ste\.?)\s*", "ste ", address)

    # collapse accidental duplicates like "ste ste"
    address = re.sub(r"\b(ste\s+)+", "ste ", address)

    replacements = {
        " street": " st",
        " avenue": " ave",
        " boulevard": " blvd",
        " road": " rd",
        " lane": " ln",
        ".": "",
        ",": "",
    }

    address = normalize_text(address, replacements)

    # clean spacing
    address = re.sub(r"\s+", " ", address).strip()

    return address.strip()


def match_company(incoming_name: str, known_names: list[str]):
    if not known_names:
        return None

    return process.extractOne(incoming_name, known_names, scorer=fuzz.token_sort_ratio)


def score_match(a, b, method="token_sort"):
    if method == "token_sort":
        return fuzz.token_sort_ratio(a, b)
    elif method == "partial":
        return fuzz.partial_ratio(a, b)
    else:
        return fuzz.ratio(a, b)
