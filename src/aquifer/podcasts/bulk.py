import feedparser
import os
import requests
import time
from pathlib import Path
from slugify import slugify  # pip install python-slugify

# --- Configuration ---
# Read env var or fall back to a local 'podcasts' directory
PODCASTS_ENV_VAR = os.getenv("PODCASTS", Path.cwd() / "podcasts")
PODCASTS_DIR = Path(PODCASTS_ENV_VAR).expanduser()
FEED_FILE = Path.cwd() / "podcasts.txt"  # File with one RSS URL per line
POLITE_DELAY_SECONDS = 1

# --- Functions ---
# (Your get_audio_url_for_entry and download_mp3_file functions go here)
# (Make sure download_mp3_file uses streaming)


def get_audio_url_for_entry(entry) -> str | None:
    # ... (same as before) ...
    pass


def download_mp3_file(url: str, file_path: Path) -> None:
    # ... (streaming version from previous answer) ...
    pass


# --- Main Execution ---
if __name__ == "__main__":
    if not FEED_FILE.exists():
        print(f"Error: Feed file not found at {FEED_FILE}")
        exit(1)

    with open(FEED_FILE, "r") as f:
        rss_urls = [line.strip() for line in f if line.strip()]

    print(f"Starting bulk download. Saving to: {PODCASTS_DIR}")

    # --- 1. Outer Loop (Over each podcast) ---
    for rss_url in rss_urls:
        print(f"\nParsing feed: {rss_url}")
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            print(f"WARNING: Feed is malformed. Skipping. {feed.bozo_exception}")
            continue

        podcast_title = slugify(feed.feed.title)
        download_dir = PODCASTS_DIR / podcast_title
        download_dir.mkdir(parents=True, exist_ok=True)
        print(f"Checking for new episodes in '{podcast_title}'...")

        # --- 2. Inner Loop (Over each episode) ---
        for entry in feed.entries:
            try:
                audio_url = get_audio_url_for_entry(entry)
                if not audio_url:
                    continue  # Skip if no audio

                # Create a unique, safe filename
                # Using 'published' or 'id' is safer than just the title
                entry_id = entry.get("published", entry.get("id", entry.title))
                safe_title = slugify(f"{entry_id}-{entry.title}", max_length=100)
                filename = f"{safe_title}.mp3"
                file_path = download_dir / filename

                # --- 3. Efficiency Check (Idempotency) ---
                if file_path.exists():
                    continue  # Skip if we already have it

                # --- 4. Download and Politeness ---
                print(f"  -> Downloading: {filename}")
                download_mp3_file(audio_url, file_path)
                time.sleep(POLITE_DELAY_SECONDS)

            except Exception as e:
                # --- 5. Resilience ---
                print(
                    f"  -> FAILED: Could not process {entry.get('title', 'NO TITLE')}. Error: {e}"
                )

    print("\nPodcast sync complete.")
