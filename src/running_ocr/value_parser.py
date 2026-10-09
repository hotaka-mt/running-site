import re
from datetime import datetime
from zoneinfo import ZoneInfo


def parse_value(text, field):
    """項目定義に従って候補の文字列を変換する。不正な値は None を返す。"""
    if text is None:
        return None
    text = text.strip()
    parser = field["parser"]
    if parser not in {"float", "int", "datetime", "duration", "pace"}:
        raise ValueError(f"Unknown parser: {parser}")
    try:
        if parser == "float":
            if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
                return float(text)
        elif parser == "int":
            unit = field.get("unit", "")
            match = re.fullmatch(r"([0-9]+)" + (r"\s*" + re.escape(unit) if unit else ""), text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        elif parser == "datetime":
            match = re.fullmatch(r"([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})\s*([0-9]{2}):([0-9]{2})", text)
            if match:
                return datetime(*map(int, match.groups()), tzinfo=ZoneInfo(field["timezone"]))
        elif parser == "duration":
            match = re.fullmatch(r"([0-9]+):([0-9]{2}):([0-9]{2})", text)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                if minutes < 60 and seconds < 60:
                    return hours * 3600 + minutes * 60 + seconds
        elif parser == "pace":
            match = re.fullmatch(r"([0-9]+)'([0-9]{2})\"", text)
            if match:
                minutes, seconds = map(int, match.groups())
                if seconds < 60:
                    return minutes * 60 + seconds
    except (ValueError, OverflowError):
        return None
    return None
