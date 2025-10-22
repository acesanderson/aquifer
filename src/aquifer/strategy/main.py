from pathlib import Path
from aquifer.research.perplexity.main import research_query_with_perplexity
from aquifer.research.exa.main import research_query_with_exa
from aquifer.research.openai.main import research_query_with_openai
import json

PROMPTS_PATH = Path(__file__).parent / "prompts"
PROMPT_FILES = list(PROMPTS_PATH.glob("*.*"))
BOILERPLATE = [p for p in PROMPT_FILES if p.suffix == ".jinja2"][0].read_text()
OTHER_PROMPTS = [p for p in PROMPT_FILES if p.suffix == ".json"][0]
PROMPTS = json.loads(OTHER_PROMPTS.read_text(encoding="utf-8"))
OUTPUT_PATH = Path(__file__).parent / "output.md"

prompts = []
for category in PROMPTS.keys():
    for prompt in PROMPTS[category]:
        prompts.append(prompt["query"])


def construct_prompt(prompt: str) -> str:
    return BOILERPLATE + "\n" + "<query>" + prompt + "</query>"


example_query = construct_prompt(prompts[0])


def research_query(query: str) -> str:
    print("Perplexity")
    perp = research_query_with_perplexity(example_query)
    print("Perplexity finished.")
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        f.write(perp)
    print("Exa")
    exa = research_query_with_exa(example_query)
    print("Exa finished.")
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        f.write(exa)
    print("OpenAI")
    oai = research_query_with_openai(example_query)
    print("OpenAI finished.")
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        f.write(oai)
    print("query finished")


if __name__ == "__main__":
    for index, prompt in enumerate(prompts[11:]):
        print(f"Processing prompt {index + 1} of {len(prompts)}")
        full_prompt = construct_prompt(prompt)
        research_query(full_prompt)
