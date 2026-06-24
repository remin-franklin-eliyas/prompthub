from core.db import get_latest_version


def get_next_version_tag(prompt_id: int) -> str:
    latest = get_latest_version(prompt_id)
    if latest is None:
        return "v1"
    current_number = parse_version_number(latest.version_tag)
    return f"v{current_number + 1}"


def parse_version_number(version_tag: str) -> int:
    return int(version_tag.lstrip("v"))