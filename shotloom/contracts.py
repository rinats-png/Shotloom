"""Content-addressed creative contract. Changed bibles invalidate stale render approvals."""
import hashlib
import json


def contract_hash(project: dict, episode: dict) -> str:
    relevant = {"creative": project["creative"], "characters": project["characters"],
                "locations": project["locations"], "props": project["props"],
                "delivery": project["delivery"], "episode": episode}
    canonical = json.dumps(relevant, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
