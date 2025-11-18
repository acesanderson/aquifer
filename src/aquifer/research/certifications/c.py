from conduit.batch import (
    ModelAsync,
    AsyncConduit,
    Prompt,
    Response,
    Verbosity,
    ConduitCache,
)
from asyncio import Semaphore

ModelAsync.conduit_cache = ConduitCache()
sem = Semaphore(5)


questions = """
What is the current (2024-2025) global market size of the professional certification industry in US dollars?
What is the projected Compound Annual Growth Rate (CAGR) for the professional certification market from 2025 through 2030?
What are the key market drivers, restraints, and opportunities cited in recent industry reports (e.g., from Grand View Research, Technavio, or similar market research firms)?
What is the market size breakdown by major industry segment (e.g., IT, Healthcare, Finance, Project Management)?
What are the formal industry definitions distinguishing a "certification" (e.g., high-stakes, proctored) from a "certificate" (e.g., completion-based)?
What are the primary types of exam proctoring used by major certification bodies (e.g., in-person, live online proctoring, AI-assisted proctoring)?
List the top 5 vendor-neutral certification bodies by estimated market share or revenue.
List the top 5 vendor-specific certification programs by the number of active credential holders.
When did the first major IT certification programs (e.g., Novell CNE, Microsoft MCSE) emerge, and what market need did they fill?
What are the founding dates and original missions of CompTIA and PMI (Project Management Institute)?
How did the "trust" and "brand authority" of certifications like the (ISC)² CISSP or PMI PMP develop over time?
What is the current non-member exam fee for the PMP certification in the US?
What is the current member exam fee for the PMP certification in the US?
What is the current annual PMI membership fee?
What are the "Professional Development Unit" (PDU) requirements to maintain a PMP certification, and how are PDUs typically earned?
What are the requirements and costs for a company to become a PMI "Authorized Training Partner (ATP)"?
What specific "Enterprise Solutions" or bulk purchasing programs does PMI offer directly to corporations?
What is PMI's latest reported total annual revenue and total membership count?
What are the current US retail prices for the CompTIA A+, Network+, and Security+ exam vouchers?
What are the product offerings and price points for CompTIA's "CertMaster" official exam preparation suite?
What are the requirements for a university to join the "CompTIA Academic Partner Program"?
What are the requirements for a training company to join the "CompTIA Commercial Partner Program"?
What are the renewal fees and continuing education (CE) requirements for CompTIA certifications?
What was the reported deal value and strategic rationale for the 2024 acquisition of CompTIA by Thoma Bravo and H.I.G. Capital?
What is the B2B partnership structure of the "AWS Partner Network"?
What are the specific certification requirements (e.g., number of certified staff) for a company to achieve "Select," "Advanced," and "Premier" tiers in the AWS Partner Network?
What is the US retail price for the "AWS Certified Cloud Practitioner" exam and the "AWS Certified Solutions Architect - Professional" exam?
What is the B2B partnership structure of the "Google Cloud Partner Advantage" program?
What are the certification requirements for a company to earn a Google Cloud "Partner" or "Premier" designation?
What is the US retail price for the "Cloud Digital Leader" exam and the "Professional Cloud Architect" exam?
What is the B2B partnership structure of the "Microsoft Cloud Partner Program"?
What are the certification requirements for a company to earn a "Solutions Partner" designation (e.g., for Azure)?
How does Microsoft's "Enterprise Skills Initiative (ESI)" program work for B2B customers?
What is the current US pricing for a "Coursera Plus" monthly and annual subscription?
How does Coursera's "freemium" funnel work for professional certificates (e.g., what is free vs. what requires payment)?
What is Udemy's primary B2C model (e.g., à la carte course purchases vs. "Personal Plan" subscription)?
What is the pricing model for "Coursera for Business" and "Coursera for Government"?
What is the pricing model for "Udemy Business," and how many courses are included?
What is the typical revenue-sharing model between Coursera and its university or industry partners (e.g., Google, IBM)?
What is the revenue-sharing model for individual instructors on the Udemy marketplace?
What recent statistics (2024-2025) quantify the increase in AI-generated resumes or job applications?
What are the key findings from industry analysts (e.g., Gartner, Forrester) on the impact of AI on resume screening and talent acquisition?
What statistical evidence or research exists on the "Skills-First" hiring trend?
Which major corporations (e.g., IBM, Google, Walmart) have publicly announced moves to drop 4-year-degree requirements for certain roles, and what do they cite as a replacement signal?
What are the most commonly cited "high-demand" or "hard" skills gaps in the 2025 US labor market?
Quantify the number of open, unfilled jobs in cybersecurity and AI/Data Science in the US (latest available data).
What performance have leading AI models (e.g., GPT-4, Claude 3) demonstrated on professional exams like the Bar, USMLE, or PMP?
What are the leading AI-powered exam proctoring services (e.g., ProctorU, Honorlock), and what specific anti-cheating technologies do they advertise?
List the major AI-focused certifications launched in 2024-2025 by "Big Tech" (Google, Microsoft, AWS).
What AI certifications, if any, have been launched by "AI-Native" companies (e.g., OpenAI, Anthropic)?
What is the product description, target audience, and price for the "PMI Certified Professional in Managing AI (PMI-CPMAI)"?
What is the product description, target audience, and price for the "CompTIA AI Essentials" certification?
What is Coursera's reported Customer Acquisition Cost (CAC) and Lifetime Value (LTV) according to their latest investor reports?
What is Coursera's reported free-to-paid conversion rate for its certificate programs?
What is the business model of "Credly" (by Pearson), and how does it generate revenue from digital badges?
What statistical data does Coursera publish in its "Learner Outcome" reports regarding salary increases or job placement rates for its Professional Certificate graduates?
What are the key findings from "Udemy's Workplace Learning Trends" or similar reports regarding the B2C value of skill acquisition?
""".strip().splitlines()

prompt_stub = """
Act as an expert research assistant. I am building a knowledge base to develop a "bizdev POV" on the professional certification and EdTech industry.

For the following query, your task is to retrieve high-quality, factual information, data, and specific examples.

Prioritize surfacing:

- Verifiable Data: (e.g., market size, company revenue, pricing models, dates, statistics).
- Key Entities & Products: (e.g., specific companies, organizations, programs, and their features).
- Source-based Facts: (e.g., information attributable to industry reports, financial filings, or official company statements).
- Business Mechanics: (Factual descriptions of how a business model, partnership, or process works).

Do not provide your own analysis, opinions, or summaries. Focus on finding and presenting the raw data and factual information needed to answer the query.

Here is the question:
<question>
{{question}}
</question>
""".strip()


def research(questions: list[str]) -> list[Response]:
    prompt = Prompt(prompt_stub)
    input_variables_list = [{"question": q} for q in questions]
    model = ModelAsync("sonar-pro")
    conduit = AsyncConduit(model=model, prompt=prompt)
    responses = conduit.run(
        input_variables_list=input_variables_list,
        verbose=Verbosity.PROGRESS,
        semaphore=sem,
    )
    assert all(isinstance(r, Response) for r in responses), (
        "All responses should be of type Response"
    )
    return responses


if __name__ == "__main__":
    results = research(questions)
    research_output = ""
    # zip questions and results
    for question, response in zip(questions, results):
        research_output += "--------------------------------------\n\n"
        research_output += f"# {question}\n\n{response.content}\n\n"
    print(research_output)
