# general_helpers.py
# A standalone helper utilities module not tied to imports from the User model.

from datetime import datetime
from typing import Optional, Union
import re
import math
import unicodedata

import numpy as np
import pandas as pd
from difflib import SequenceMatcher


# -----------------------------------
# Basic Normalizations & Parsing
# -----------------------------------

def normalize(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def clean_list(list_to_clean: list) -> list:
    if not isinstance(list_to_clean, list):
        return []

    cleaned = []
    for x in list_to_clean:
        if x in (None, "", [], {}, ()):
            continue
        cleaned.append(x)
    return cleaned


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val = value.strip().lower()
        if val in ("yes", "true", "1"): return True
        if val in ("no", "false", "0"): return False
    if isinstance(value, int):
        if value == 1: return True
        if value == 0: return False
    return None


def parse_any_nan(val, replace_with=None):
    if isinstance(val, (list, np.ndarray, pd.Series)):
        return [parse_any_nan(v, replace_with) for v in val]
    if isinstance(val, float) and math.isnan(val):
        return replace_with
    if isinstance(val, str) and val.strip().lower() in ("nan", "none", "null", ""):
        return replace_with
    if pd.isna(val):
        return replace_with
    return val


def float_to_str_no_dot(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).replace(".", "")
    return str(value)


# -----------------------------------
# Date Parsing
# -----------------------------------

month_fix_map = {
    "janu": "jan",
    "febr": "feb",
    "marc": "mar",
    "apri": "apr",
    "mayy": "may",
    "june": "jun",
    "july": "jul",
    "augu": "aug",
    "sept": "sep",
    "octo": "oct",
    "nove": "nov",
    "dece": "dec",
}

_formats = [
    "%m/%d/%Y %I:%M:%S %p",
    "%m/%d/%Y %I:%M %p",
    "%m/%d/%Y",
    "%b %d, %Y",
    "%B %d, %Y",
    "%Y/%m/%d",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%Y.%m.%d",
    "%d.%m.%Y",
]


def parse_date(value: Union[str, datetime, int, float]) -> Optional[datetime]:
    if isinstance(value, datetime): return value
    if isinstance(value, (int, float)): return None
    if not isinstance(value, str) or not value.strip(): return None

    value = value.strip().lower()

    for wrong, correct in month_fix_map.items():
        value = re.sub(rf"\b{wrong}\b", correct, value)

    value = re.sub(r"\s*,\s*", ", ", value)
    value = re.sub(r"\s*/\s*", "/", value)
    value = re.sub(r"\s+", " ", value)

    for fmt in _formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


# -----------------------------------
# Range Parsing
# -----------------------------------

def parse_range(range_str: str, min_limit=None, max_limit=None):
    if not isinstance(range_str, str):
        return None
    range_str = range_str.strip().lower()
    if "to" not in range_str:
        return None
    parts = range_str.split("to")
    if len(parts) != 2:
        return None

    left, right = parts[0].strip(), parts[1].strip()

    if not left or not right:  # prevents "", "to", "10 to"
        return None

    def parse_val(v):
        if v == "any": return None
        if v.isdigit(): return int(v)
        return v

    lower, upper = parse_val(left), parse_val(right)

    if lower is None and left == "any": lower = min_limit
    if upper is None and right == "any": upper = max_limit

    if lower is None or upper is None:
        return None
    return lower, upper


# -----------------------------------
# Height Parsing
# -----------------------------------
def height_to_cm(height_str):
    # Reject iterable/collection types
    if isinstance(height_str, (pd.Series, np.ndarray, list, dict, set, tuple)):
        return None
    # -------- Handle numeric input --------
    if isinstance(height_str, (int, float)):
        if isinstance(height_str, float) and (math.isnan(height_str) or math.isinf(height_str)):
            return None

        val = float(height_str)

        # <3 means meters
        if val < 3:
            return round(val * 100)

        # ≥3 means cm
        return round(val)

    # -------- Reject non-string --------
    if not height_str or not isinstance(height_str, str):
        return None

    s = _sanitize(height_str)

    # -------- FULL-STRING MATCHES ONLY --------
    # 1) Hebrew format: "153 ס\"מ"
    result = _parse_hebrew_cm(s)
    if result is not None:
        return result

    # 2) Metric: "180 cm"
    result = _parse_cm(s)
    if result is not None:
        return result

    # 3) Metric meters: "1.80 m"
    result = _parse_m(s)
    if result is not None:
        return result

    # 4) Feet + inches: "5' 10"
    result = _parse_feet_inches(s)
    if result is not None:
        return result

    # 5) Decimal feet with inch symbol: 5.5"
    result = _parse_decimal_feet(s)
    if result is not None:
        return result

    # 6) Plain number → interpret
    result = _parse_just_number(s)
    if result is not None:
        return result

    return None


def find_key_by_value(data, target):
    for key, value in data.items():
        if value == target:
            return key
    return None

def fetch_exact_option(source: str, options: list, threshold: float = 0.89) -> Union[str, None]:
    if not isinstance(source, str):
        return None

    normalized_source = normalize(source)
    best_score = -1
    best_match = None

    for option in options:
        if isinstance(option, bool) or not isinstance(option, str):
            continue  # Skip booleans and non-strings

        normalized_option = normalize(option)
        score = similarity(normalized_source, normalized_option)

        if score > best_score:
            best_score = score
            best_match = option

    if best_score < threshold:
        return None

    return best_match



def _from_numeric(value: Union[int, float]) -> int:
    return round(value * 100) if value < 3 else round(value)


def _is_hebrew_cm(s: str) -> bool:
    return re.search(r'ס["”]?מ', s) is not None

def _sanitize(s: str) -> str:
    s = s.strip().lower()
    s = s.replace(",", ".")

    # Normalize all apostrophe/prime variants to single quote
    s = s.replace("′", "'")
    s = s.replace("’", "'")
    s = s.replace("‵", "'")
    s = s.replace("`", "'")

    # Normalize all inch/quote variants to double quote
    s = s.replace("″", '"')
    s = s.replace("”", '"')
    s = s.replace("❞", '"')

    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def _parse_hebrew_cm(s: str):
    # FULL match only
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*ס\"?מ", s)
    if not match:
        return None
    return round(float(match.group(1)))


def _parse_cm(s: str):
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*cm", s)
    if not match:
        return None
    return round(float(match.group(1)))


def _parse_m(s: str):
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*m", s)
    if not match:
        return None
    meters = float(match.group(1))
    # Convert meters <3 into cm
    return round(meters * 100) if meters < 3 else round(meters)


def _parse_feet_inches(s: str):
    s2 = s.replace("′", "'").replace("″", '"')

    # Full feet+inch match with arbitrary spaces
    feet_inch = re.match(
        r"^\s*(\d+)\s*[']\s*(\d+)\s*(?:\"|)?\s*$",
        s2
    )
    if feet_inch:
        ft = int(feet_inch.group(1))
        inch = int(feet_inch.group(2))
        return round(ft * 30.48 + inch * 2.54)

    # Feet only "6'"
    feet_only = re.match(r"^\s*(\d+)\s*[']\s*$", s2)
    if feet_only:
        ft = int(feet_only.group(1))
        return round(ft * 30.48)
    return None


def _parse_decimal_feet(s: str):
    match = re.fullmatch(r"(\d+\.\d+)\s*\"", s)  # quote REQUIRED
    return round(float(match.group(1)) * 30.48) if match else None



def _parse_just_number(s: str):
    if not re.fullmatch(r"\d+(\.\d+)?", s):
        return None

    val = float(s)

    # <3 → meters
    if val < 3:
        return round(val * 100)

    # >=3 → centimeters
    return round(val)
