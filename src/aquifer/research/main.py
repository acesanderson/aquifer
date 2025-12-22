from pathlib import Path
from exa_query.main import research_query_with_exa
from openai_query.main import research_query_with_openai
from perplexity_query.main import research_query_with_perplexity

# The Biweekly prompt
# query = Path("query_string.jinja2").read_text()

query = """
Today's date is 2025-12-22.

You are analyzing this question for founders and operators of online learning businesses that serve BOTH consumer (B2C) and enterprise (B2B) customers.

Question:
How are large language models (LLMs) disrupting the business of online learning?

Instructions:
- Treat consumer and enterprise learning as distinct markets with different incentives, constraints, and success metrics.
- Analyze consumer (B2C) and enterprise (B2B) impacts separately before comparing them.
- For each, analyze disruption across the value chain: content creation, instruction, assessment, credentialing, distribution, pricing, and outcomes measurement.
- Highlight where LLM effects diverge, conflict, or create internal tensions for companies serving both segments.
- Ground claims in concrete examples, observed market behavior, or plausible economic mechanisms — not abstract benefits.
- Explicitly address second-order effects and failure modes (e.g., consumer substitution, enterprise risk aversion, credential trust erosion).
- Include at least 2 strong counterarguments where LLM impact is likely overstated or mispriced in BOTH B2C and B2B contexts.

Output format:
1. Executive summary (≤150 words)
2. Consumer (B2C) disruption analysis
3. Enterprise (B2B) disruption analysis
4. Key divergences and internal tensions for dual-market companies
5. Overhyped narratives vs. durable changes
6. Strategic implications for operators (clearly separated: B2C, B2B, and shared)

Constraints:
- Prioritize insights that change product, pricing, or go-to-market decisions.
- Exclude generic claims that apply equally to all software businesses.
- Aim for clarity over exhaustiveness.
""".strip()

if not Path("response_openai.txt").exists():
    response_openai = research_query_with_openai(query)
    with open("response_openai.txt", "w") as f:
        f.write(response_openai)
if not Path("response_exa.txt").exists():
    response_exa = research_query_with_exa(query)
    with open("response_exa.txt", "w") as f:
        f.write(response_exa)
if not Path("response_perplexity.txt").exists():
    response_perplexity = research_query_with_perplexity(query)
    with open("response_perplexity.txt", "w") as f:
        f.write(response_perplexity)
