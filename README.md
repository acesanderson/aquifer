# Aquifer

A toolkit for automating data collection and research from various online sources, including RSS feeds, YouTube, SEC filings, and multiple AI-powered search agents.

## Table of Contents

- [Quick Start: Find an Earnings Call Transcript](#quick-start-find-an-earnings-call-transcript)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)

## Quick Start: Find an Earnings Call Transcript

This example uses the Brave Search API and an AI model to find, download, and extract the text from a company's most recent earnings call transcript. This entire process should take less than 5 minutes.

### 1. Installation

First, clone the repository and set up a virtual environment.

```bash
git clone https://github.com/your-username/aquifer-project.git
cd aquifer-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*(Note: The contents of `requirements.txt` are detailed in the [Installation](#dependencies) section below.)*

### 2. Configuration

The script requires an API key from Brave Search.

1.  Create a file named `.env` in the project root.
2.  Add your Brave API key to the file:

    ```ini
    # .env
    BRAVE_API_KEY="your_brave_api_key_here"
    ```

### 3. Run the Script

Execute the `brave` research module. The script is configured to search for Google's latest earnings call transcript by default.

```bash
python -m aquifer.research.brave
```

The script will perform a search, select the most relevant URL, and print the full text of the article to your console.

**Expected Output:**

```
Earnings Call Transcript for Google:

(Reuters) - Q3 2023 Alphabet Inc Earnings Call
October 24, 2023

**Executives**

Sundar Pichai - CEO, Alphabet
Philipp Schindler - SVP & Chief Business Officer, Google
Ruth Porat - President & Chief Investment Officer; CFO

**Analysts**

Brian Nowak - Morgan Stanley
Eric Sheridan - Goldman Sachs
Doug Anmuth - JPMorgan

**Operator**
Welcome, everyone, and thank you for standing by for the Alphabet Third Quarter 2023 Earnings Conference Call...

[...full transcript follows...]
```

## Installation

### Prerequisites

- Python 3.9+
- Git
- PostgreSQL (only required for the YouTube metadata module)

### Dependencies

Install all required packages using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

The project depends on the following packages:

```txt
# requirements.txt
feedparser
google-api-python-client
pydantic
requests
requests-cache
rich
markdownify
newspaper3k
exa_py
openai
python-dotenv
```
*Note: This project also utilizes internal libraries `conduit` and `dbclients` which are not publicly available. Modules depending on these libraries will require custom setup.*

### Environment Variables

Several modules require API keys or other credentials. Create a `.env` file in the project's root directory and add the necessary keys for the components you intend to use.

| Variable          | Description                                         | Required By Module(s)              |
| ----------------- | --------------------------------------------------- | ---------------------------------- |
| `BRAVE_API_KEY`   | API key for the Brave Search API.                   | `research.brave`                   |
| `YOUTUBE_API_KEY` | API key for the Google YouTube Data API v3.         | `youtube.retrieve_channel`         |
| `EXA_API_KEY`     | API key for the Exa (Metaphor) Search API.          | `research.exa`                     |
| `OPENAI_API_KEY`  | API key for OpenAI models.                          | `research.openai`, `research.10k`  |

## Usage Examples

Below are examples of how to run other scripts in the toolkit.

### Parse an RSS Feed

This script fetches and parses any RSS feed, printing the most recent articles.

```bash
python -m aquifer.rss.rss
```

**Output:**
```
Feed: QS-GEN - General
Latest items: 10

Title: What Can You Do With a Business Master’s Degree?
Published: Fri, 26 Jul 2024 09:30:00 +0100
Link: https://www.qs.com/what-can-you-do-with-a-business-masters-degree/

Title: How to Write a Personal Statement for Grad School
Published: Wed, 24 Jul 2024 12:45:00 +0100
Link: https://www.qs.com/how-to-write-a-personal-statement-for-grad-school/
...
```

### Retrieve SEC Filings

This script finds a company's CIK (Central Index Key) and fetches its most recent 10-K filing from the SEC EDGAR database. It requires an `OPENAI_API_KEY` to identify the CIK.

```bash
# Set OPENAI_API_KEY in your .env file
python -m aquifer.research.10k
```

**Output:**
```
Latest filing for Coursera (2024-02-23):
```

### Fetch YouTube Channel Metadata

This script retrieves metadata for all videos on a specified YouTube channel and saves it to a PostgreSQL database.

**Requirements:**
1.  Set `YOUTUBE_API_KEY` in your `.env` file.
2.  Have a running PostgreSQL instance.
3.  The internal `dbclients` library must be configured to connect to your database.

```bash
python -m aquifer.youtube.retrieve_channel
```

**Output:**
```
Fetching videos from channel: UCDyb_XxlM-stb-tL7v02g5w
Found 150 videos
Fetched metadata for 150 videos
Inserted/Updated 150 videos into the database.
Sample video from DB: {
  "video_id": "some_video_id",
  "title": "Example Video Title",
  "description": "This is an example video description...",
  ...
}
```

## Project Structure

The project is organized into modules based on data source and functionality.

-   `src/aquifer/rss/`: Contains tools for parsing RSS and Atom feeds.
-   `src/aquifer/youtube/`: Scripts for retrieving video and channel metadata from the YouTube API.
-   `src/aquifer/research/`: A suite of tools for advanced research, using SEC filings and AI-powered search APIs like Brave, Exa, and OpenAI.
-   `src/aquifer/strategy/`: Orchestrates calls to multiple research modules to synthesize complex reports.

```
