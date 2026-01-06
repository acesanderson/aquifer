import time
from google import genai
import logging
import diskcache

logger = logging.getLogger(__name__)

client = genai.Client()  # Assumes API key in environment
cache = diskcache.Cache("./deep_research_cache")


@cache.memoize(expire=86400)  # Cache results for 1 day
def deep_research(input: str) -> str:
    logger.info("Starting deep research interaction")
    start_time = time.time()
    interaction = client.interactions.create(
        input=input,
        agent="deep-research-pro-preview-12-2025",
        background=True,
    )

    while True:
        logger.info(
            f"Checking status of interaction {interaction.id}: {time.time() - start_time:.2f}s elapsed"
        )
        interaction = client.interactions.get(interaction.id)
        if interaction.status == "completed":
            return interaction.outputs[-1].text
        elif interaction.status == "failed":
            raise Exception(f"Research failed: {interaction.error}")
        time.sleep(10)


if __name__ == "__main__":
    query = "What is the competitive threat to LinkedIn Learning posed from the Coursera acquisition of Udemy on 2025-12-16?"
    result = deep_research(query)
    print("Research Result:")
    print(result)
