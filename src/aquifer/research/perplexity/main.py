from conduit.sync import (
    Conduit,
    Prompt,
    Model,
    Verbosity,
    ConduitCache,
    Response,
)
# from pathlib import Path

# PROMPT_FILE = Path(__file__).parent / "prompts.md"
PREFERRED_MODEL = "sonar"
VERBOSITY = Verbosity.COMPLETE
CACHE = ConduitCache()
Model.conduit_cache = CACHE

system_prompt = """
You are searching for news and developments from the past two weeks only (September 25 - October 9, 2025). Focus on factual announcements with specific details: company names, partnership terms, funding amounts, program launches, and pricing changes. Exclude opinion pieces, general trend articles, and speculation unless they contain hard data or named sources. Prioritize primary sources and official announcements.
""".strip()

# prompts = PROMPT_FILE.read_text()
# prompts = prompts.split("\n")
# prompt_strings = [system_prompt + "\n\n" + p for p in prompts]


# Our chain
def research_query_with_perplexity(
    query: str, index: int = 0, total: int = 0, preferred_model=PREFERRED_MODEL
) -> str:
    model = Model(preferred_model)
    prompt = Prompt(query)
    conduit = Conduit(model=model, prompt=prompt)
    response = conduit.run(verbose=VERBOSITY, index=index, total=total)
    assert isinstance(response, Response)
    return str(response.content)
