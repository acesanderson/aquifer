import feedparser
import requests
import os
from pathlib import Path

RSS_URL = "https://anchor.fm/s/f061c650/podcast/rss"
PODCASTS_ENV_VAR = os.getenv("PODCASTS")
PODCASTS_DIR = Path(PODCASTS_ENV_VAR).expanduser()
assert PODCASTS_DIR is not None, "Please set the PODCASTS environment variable."


def get_audio_url_for_entry(entry) -> str | None:
    audio_url = None
    if "enclosures" in entry:
        for enclosure in entry.enclosures:
            # Check if the MIME type is audio
            if "audio" in enclosure.type:
                audio_url: str = enclosure.href
                break  # Found the audio file

    if audio_url:
        print(f"Download URL: {audio_url}")
    else:
        print("No audio enclosure found for this entry.")
        return
    return audio_url


def download_mp3_file(url: str, file_path: Path) -> None:
    """
    Downloads a file in chunks to save memory.
    """
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Ensure we notice bad responses

            with open(file_path, "wb") as file:
                # Download in 1MB chunks
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    file.write(chunk)
        print(f"Downloaded: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")


if __name__ == "__main__":
    feed = feedparser.parse(RSS_URL)

    entry = feed.entries[0]
    audio_url = get_audio_url_for_entry(entry)
    if audio_url:
        # Create podcasts directory if it doesn't exist
        PODCASTS_DIR.mkdir(parents=True, exist_ok=True)

        # Use the entry title to create a filename
        safe_title = "".join(
            c for c in entry.title if c.isalnum() or c in (" ", "_", "-")
        ).rstrip()
        filename = f"{safe_title}.mp3"

        download_mp3_file(audio_url, filename)
