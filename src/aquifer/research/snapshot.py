"""
Research in parallel.
"""

from conduit.batch import (
    ModelAsync,
    AsyncConduit,
    Prompt,
    Verbosity,
    ConduitCache,
)
from conduit.parser.parser import Parser
from datetime import date
from pathlib import Path
from rich.console import Console
from pydantic import BaseModel
import asyncio
import json


class TextResponse(BaseModel):
    content: str


# Constants
CACHE = ConduitCache(name="aquifer")
SNAPSHOT_PROMPT_STRING = (Path(__file__).parent / "query_string.jinja2").read_text()
QUESTIONS_PROMPT_JSONL = (Path(__file__).parent / "question_areas.jsonl").read_text()
QUESTIONS = [
    json.loads(line) for line in QUESTIONS_PROMPT_JSONL.splitlines() if line.strip()
]
TODAYS_DATE = date.today().strftime("%B %d, %Y")
VERBOSITY = Verbosity.PROGRESS
CONSOLE = Console()
SEMAPHORE = asyncio.Semaphore(2)

# Configs
ModelAsync.cache = CACHE
ModelAsync.console = CONSOLE


def create_prompt(title: str, question: str) -> str:
    prompt = Prompt(SNAPSHOT_PROMPT_STRING)
    return prompt.render(
        {"TODAYS_DATE": TODAYS_DATE, "TITLE": title, "QUESTION": question}
    )


# For async, assemble all the prompt strings
prompt_strings = []
for q in QUESTIONS:
    title = q["title"]
    for question in q["questions"]:
        prompt = create_prompt(title, question)
        prompt_strings.append(prompt)

# Our batch conduit
parser = Parser(TextResponse)
model = ModelAsync(model="sonar")
conduit = AsyncConduit(model=model, parser=parser)
responses = conduit.run(
    prompt_strings=prompt_strings, verbose=VERBOSITY, semaphore=SEMAPHORE
)

# Combine outputs into a single markdown file
combined_output = ""
for response in responses:
    combined_output += response.content.content + "\n\n"

output_path = "snapshot_output.md"
with open(output_path, "w") as f:
    f.write(combined_output)
