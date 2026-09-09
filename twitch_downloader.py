import os
import re
from typing import Optional
import requests

TWITCH_GQL_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
GQL_URL = "https://gql.twitch.tv/gql"


def sanitize_filename(name: str) -> str:
    """Removes filesystem-incompatible characters from video titles."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def derive_mp4_from_thumbnail(thumbnail_url: str) -> Optional[str]:
    """Derives direct MP4 URL by trimming preview dimensions from thumbnail URL."""
    idx = thumbnail_url.find("-preview")
    if idx != -1:
        return thumbnail_url[:idx] + ".mp4"
    return None


def get_clip_source_via_gql(slug: str) -> Optional[str]:
    """Fetches direct MP4 stream URL with access token signature via Twitch GQL."""
    query = """
    query ClipPlaybackAccessToken($slug: ID!) {
      clip(slug: $slug) {
        playbackAccessToken {
          signature
          value
        }
        videoQualities {
          quality
          sourceURL
        }
      }
    }
    """
    payload = {"query": query, "variables": {"slug": slug}}
    headers = {"Client-ID": TWITCH_GQL_CLIENT_ID}

    try:
        res = requests.post(GQL_URL, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        clip_data = data.get("data", {}).get("clip")
        if not clip_data:
            return None

        token = clip_data["playbackAccessToken"]
        qualities = clip_data.get("videoQualities", [])
        if not qualities:
            return None

        # Pick highest available quality (typically the first entry)
        source_url = qualities[0]["sourceURL"]
        return f"{source_url}?sig={token['signature']}&token={token['value']}"
    except Exception:
        return None


def get_direct_mp4_url(slug: str, thumbnail_url: str) -> Optional[str]:
    """Attempts direct thumbnail derivation first; falls back to GQL playback token."""
    derived_url = derive_mp4_from_thumbnail(thumbnail_url)
    if derived_url:
        try:
            head = requests.head(derived_url, timeout=5)
            if head.status_code == 200:
                return derived_url
        except requests.RequestException:
            pass

    return get_clip_source_via_gql(slug)


def download_clip(
    slug: str,
    title: str,
    thumbnail_url: str,
    download_dir: str = "downloads",
) -> Optional[str]:
    """Streams the raw MP4 into the local downloads directory."""
    os.makedirs(download_dir, exist_ok=True)
    mp4_url = get_direct_mp4_url(slug, thumbnail_url)

    if not mp4_url:
        print(f"[-] Could not resolve direct MP4 for clip: {slug}")
        return None

    safe_title = sanitize_filename(title) or "clip"
    file_path = os.path.join(download_dir, f"{safe_title}_{slug}.mp4")

    print(f"[+] Downloading: {safe_title} ({slug})...")
    with requests.get(mp4_url, stream=True, timeout=20) as response:
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    print(f"[✓] Saved to: {file_path}")
    return file_path
