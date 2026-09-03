import secrets
import string
from datetime import datetime, timezone
from typing import Any, Dict, List
import math


def generate_cyclone_id(prefix: str = "CY") -> str:
    """Generate a deterministic-looking human-readable cyclone ID.

    Format: {prefix}{3_digits}-{4 random hex}.
    """
    digits = "".join(secrets.choice(string.digits) for _ in range(3))
    hex_tail = secrets.token_hex(2)
    return f"{prefix}{digits}-{hex_tail.upper()}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate great-circle distance in km using the haversine formula."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def round_dict_values(data: Dict[str, Any], digits: int = 4) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, float):
            out[k] = round(v, digits)
        elif isinstance(v, dict):
            out[k] = round_dict_values(v, digits)
        elif isinstance(v, list):
            out[k] = [
                round_dict_values(x, digits) if isinstance(x, dict) else x
                for x in v
            ]
        else:
            out[k] = v
    return out
