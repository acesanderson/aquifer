from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dbclients.clients.postgres import get_db_connection
from pydantic import BaseModel, Field
from datetime import datetime
import os

EXAMPLE_CHANNEL = "https://www.youtube.com/@NateBJones"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DB_NAME = "youtube_metadata"

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


class VideoMetadata(BaseModel):
    video_id: str = Field(..., description="YouTube Video ID")
    title: str = Field(..., description="Video Title")
    description: str = Field(..., description="Video Description")
    published_at: str = Field(..., description="Publication Date")
    duration: str = Field(..., description="Video Duration in ISO 8601 format")
    view_count: int = Field(..., description="Number of Views")
    like_count: int = Field(..., description="Number of Likes")


def get_channel_id_from_url(channel_url):
    """
    Extract channel ID from various YouTube channel URL formats.
    Handles: /channel/ID, /c/customname, /user/username, /@handle
    """
    if "/channel/" in channel_url:
        return channel_url.split("/channel/")[-1].split("/")[0]
    elif "/@" in channel_url or "/c/" in channel_url or "/user/" in channel_url:
        # For custom URLs, we need to resolve them via API
        username = channel_url.split("/")[-1].replace("@", "")
        try:
            request = youtube.search().list(
                part="snippet", q=username, type="channel", maxResults=1
            )
            response = request.execute()
            if response["items"]:
                return response["items"][0]["snippet"]["channelId"]
        except HttpError as e:
            print(f"Error resolving channel: {e}")
            return None
    return None


def get_all_videos_from_channel(channel_id) -> list[str]:
    """
    Get all video IDs from a channel.
    Returns list of video IDs.
    """
    video_ids = []

    # First, get the channel's "uploads" playlist ID
    try:
        channel_response = (
            youtube.channels().list(part="contentDetails", id=channel_id).execute()
        )

        if not channel_response["items"]:
            print(f"Channel {channel_id} not found")
            return []

        uploads_playlist_id = channel_response["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]

        # Now get all videos from the uploads playlist
        next_page_token = None

        while True:
            playlist_response = (
                youtube.playlistItems()
                .list(
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=50,  # Max allowed per request
                    pageToken=next_page_token,
                )
                .execute()
            )

            # Extract video IDs
            for item in playlist_response["items"]:
                video_ids.append(item["contentDetails"]["videoId"])

            # Check if there are more pages
            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break

        return video_ids

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []


def get_video_metadata(video_ids):
    """
    Get metadata for videos (title, description, etc.)
    Takes list of video IDs, returns list of video info dicts.
    """
    videos_info: list[VideoMetadata] = []

    # API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]

        try:
            video_response = (
                youtube.videos()
                .list(part="snippet,contentDetails,statistics", id=",".join(batch))
                .execute()
            )

            for item in video_response["items"]:
                video_metadata = VideoMetadata(
                    video_id=item["id"],
                    title=item["snippet"]["title"],
                    description=item["snippet"]["description"],
                    published_at=item["snippet"]["publishedAt"],
                    duration=item["contentDetails"]["duration"],
                    view_count=int(item["statistics"].get("viewCount", 0)),
                    like_count=int(item["statistics"].get("likeCount", 0)),
                )
                videos_info.append(video_metadata)

        except HttpError as e:
            print(f"Error fetching video metadata: {e}")

    return videos_info


def load_video_metadata_into_db(videos_info: list[VideoMetadata]):
    """
    Load video metadata into PostgreSQL database.
    """
    with get_db_connection(DB_NAME) as conn, conn.cursor() as cursor:
        # Ensure table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS video_metadata (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                published_at TIMESTAMP,
                duration TEXT,
                view_count INTEGER,
                like_count INTEGER
            )
            """
        )
        # Insert or update video metadata
        for video in videos_info:
            cursor.execute(
                """
                INSERT INTO video_metadata (video_id, title, description, published_at, duration, view_count, like_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (video_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    published_at = EXCLUDED.published_at,
                    duration = EXCLUDED.duration,
                    view_count = EXCLUDED.view_count,
                    like_count = EXCLUDED.like_count
                """,
                (
                    video.video_id,
                    video.title,
                    video.description,
                    video.published_at,
                    video.duration,
                    video.view_count,
                    video.like_count,
                ),
            )
        conn.commit()

    print(f"Inserted/Updated {len(videos_info)} videos into the database.")


def get_a_video_metadata_from_db() -> VideoMetadata:
    """
    Retrieve a single video's metadata from the database for verification.
    """
    with get_db_connection(DB_NAME) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM video_metadata LIMIT 1")
        row = cursor.fetchone()
        if row:
            return VideoMetadata(
                video_id=row[0],
                title=row[1],
                description=row[2],
                published_at=row[3].isoformat()
                if isinstance(row[3], datetime)
                else row[3],
                duration=row[4],
                view_count=row[5],
                like_count=row[6],
            )
    return None


# Example usage
if __name__ == "__main__":
    channel_id = get_channel_id_from_url(EXAMPLE_CHANNEL)

    print(f"Fetching videos from channel: {channel_id}")
    video_ids = get_all_videos_from_channel(channel_id)
    print(f"Found {len(video_ids)} videos")

    # Get metadata for all videos
    videos = get_video_metadata(video_ids)
    print(f"Fetched metadata for {len(videos)} videos")
    # Load metadata into database
    load_video_metadata_into_db(videos)
    # Verify by fetching one video from DB
    sample_video = get_a_video_metadata_from_db()
    print(f"Sample video from DB: {sample_video.model_dump_json(indent=2)}")
