from pathlib import Path
from exa_query.main import research_query_with_exa
from openai_query.main import research_query_with_openai
from perplexity_query.main import research_query_with_perplexity


query = Path("query_string.jinja2").read_text()

if not Path("response_exa.txt").exists():
    response_exa = research_query_with_exa(query)
    with open("response_exa.txt", "w") as f:
        f.write(response_exa)
if not Path("response_openai.txt").exists():
    response_openai = research_query_with_openai(query)
    with open("response_openai.txt", "w") as f:
        f.write(response_openai)
if not Path("response_perplexity.txt").exists():
    response_perplexity = research_query_with_perplexity(query)
    with open("response_perplexity.txt", "w") as f:
        f.write(response_perplexity)
