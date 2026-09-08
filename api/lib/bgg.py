import contextlib
from xml.etree.ElementTree import Element

import defusedxml.ElementTree as ET
import httpx

import lib.db.settings as settings_db

BGG_API_BASE = "https://boardgamegeek.com/xmlapi2"

_bgg_token: str | None = None
_bgg_token_fallback: str = ""


def set_bgg_token(token: str) -> None:
    global _bgg_token
    _bgg_token = token


def set_bgg_token_fallback(token: str) -> None:
    """Stores the env/SSM-resolved token as the fallback used when no DB
    override is set, then applies whichever currently wins."""
    global _bgg_token_fallback
    _bgg_token_fallback = token
    refresh_token_from_db()


def refresh_token_from_db() -> None:
    """Re-applies token precedence: a DB override (set via PUT /api/settings)
    wins over the env/SSM fallback when present."""
    db_token = settings_db.get_settings().get("bggToken")
    set_bgg_token(db_token or _bgg_token_fallback)


def _fetch_xml(url: str, params: dict | None = None) -> Element:
    headers = {}
    if _bgg_token:
        headers["Authorization"] = f"Bearer {_bgg_token}"
    response = httpx.get(url, params=params, headers=headers, timeout=15.0, follow_redirects=True)
    response.raise_for_status()
    return ET.fromstring(response.text)


def bgg_search(query: str) -> list[dict]:
    root = _fetch_xml(f"{BGG_API_BASE}/search", params={"query": query, "type": "boardgame"})
    results = []
    for item in root.findall("item")[:10]:
        bgg_id = item.get("id")
        if not bgg_id:
            continue
        name_el = item.find("name")
        year_el = item.find("yearpublished")
        year = year_el.get("value") if year_el is not None else None
        results.append(
            {
                "bggId": int(bgg_id),
                "name": name_el.get("value", "") if name_el is not None else "",
                "yearPublished": int(year) if year else None,
            }
        )
    return results


def bgg_detail(bgg_id: int) -> dict:
    root = _fetch_xml(f"{BGG_API_BASE}/thing", params={"id": bgg_id, "stats": 1})
    item = root.find("item")
    if item is None:
        raise ValueError(f"BGG game not found: {bgg_id}")

    primary_name = ""
    for name_el in item.findall("name"):
        if name_el.get("type") == "primary":
            primary_name = name_el.get("value", "")
            break

    detail: dict = {"bggId": int(item.get("id", bgg_id)), "name": primary_name}

    year_el = item.find("yearpublished")
    if year_el is not None:
        detail["yearPublished"] = int(year_el.get("value", 0))

    image_el = item.find("image")
    if image_el is not None and image_el.text:
        detail["imageUrl"] = image_el.text.strip()

    for field, xml_tag in [
        ("minPlayers", "minplayers"),
        ("maxPlayers", "maxplayers"),
        ("playTime", "playingtime"),
    ]:
        el = item.find(xml_tag)
        if el is not None:
            val = el.get("value")
            if val:
                detail[field] = int(val)

    weight_el = item.find(".//averageweight")
    if weight_el is not None:
        val = weight_el.get("value")
        if val:
            with contextlib.suppress(ValueError):
                detail["weight"] = float(val)

    return detail
