from typing import Any, Dict, List, Optional
import requests

CLIPS_URL = "https://api.twitch.tv/helix/clips"


def get_game_clips(
    game_id: str,
    client_id: str,
    access_token: str,
    first: int = 20,
    after: Optional[str] = None,
    started_at: Optional[str] = None,
    ended_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch clips for a specific game ID from Twitch Helix API."""
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }
    params: Dict[str, Any] = {
        "game_id": game_id,
        "first": min(first, 100),
    }

    if after:
        params["after"] = after
    if started_at:
        params["started_at"] = started_at
    if ended_at:
        params["ended_at"] = ended_at

    response = requests.get(CLIPS_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    return response.json()
