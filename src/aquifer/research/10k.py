import requests
import requests_cache
from pathlib import Path
from pydantic import BaseModel, Field
from functools import cached_property
from markdownify import markdownify as md
from rich.console import Console
from rich.markdown import Markdown
from conduit.sync import Model, Prompt, Conduit, Response, Verbosity, ConduitCache

# Configs
requests_cache.install_cache(".sec_cache")
console = Console()
cache = ConduitCache(name="research")
Model.conduit_cache = cache
Model.console = console

# Constants
PREFERRED_MODEL = "sonar"

# Prompt strings
cik_prompt_str = """
Given the company name, return the Central Index Key (CIK) used by the U.S. Securities and Exchange Commission (SEC) to identify the company. Only return the CIK number without any additional text.

If the company is not publicly traded or does not have a CIK, respond with "N/A".

<company_name>
{{company_name}}
</company_name>
""".strip()


# Functions
def is_valid_cik(cik: str) -> bool:
    return cik.isdigit() and len(cik) <= 10


def normalize_cik(x) -> str:
    if len(x.splitlines()) > 1:
        x = x.splitlines()[0]
    return str(x).strip().strip('"').strip("'")


def get_cik(company_name: str) -> str:
    """
    Given a company name, return its Central Index Key (CIK) from the SEC.
    """
    prompt = Prompt(cik_prompt_str)
    model = Model(PREFERRED_MODEL)
    conduit = Conduit(model=model, prompt=prompt)
    response = conduit.run(
        input_variables={"company_name": company_name}, verbose=Verbosity.SILENT
    )
    assert isinstance(response, Response), f"Expected Response, got {type(response)}"
    cik = normalize_cik(str(response.content))
    if is_valid_cik(cik):
        return cik
    raise ValueError(
        f"Invalid CIK returned for {company_name}: {cik}. Are you sure this company is publicly traded?"
    )


# Dataclasses
class SECFiling(BaseModel):
    url: str = Field(..., description="The URL of the SEC filing")
    date: str = Field(..., description="The filing date of the SEC filing")

    @cached_property
    def content(self):
        headers = {"User-Agent": "Your Name your.email@example.com"}
        r = requests.get(self.url, headers=headers)
        return r.text

    def print(self):
        md_content = md(self.content)
        markdown = Markdown(md_content)
        console.print(markdown)


class Company(BaseModel):
    name: str = Field(..., description="The name of the company")
    cik: str = Field(..., description="The Central Index Key (CIK) of the company")

    @cached_property
    def filings(self) -> list[SECFiling]:
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        headers = {"User-Agent": "Your Name your.email@example.com"}

        r = requests.get(url, headers=headers)
        data = r.json()

        # Zip the parallel lists into structured records
        records = zip(
            data["filings"]["recent"]["accessionNumber"],
            data["filings"]["recent"]["form"],
            data["filings"]["recent"]["filingDate"],
            data["filings"]["recent"]["primaryDocument"],
        )

        # Filter and view only 10-K/20-F filings
        filings = []
        for acc, form, date, doc in records:
            if form == "10-K" or form == "20-F":
                url = f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{acc.replace('-', '')}/{doc}"
                filings.append(SECFiling(url=url, date=date))
        if not filings:
            print(f"No 10-K or 20-F filings found for CIK {self.cik}")
        return filings


class Companies(BaseModel):
    companies: list[Company] = Field(
        ..., description="A list of companies with their CIKs"
    )

    @classmethod
    def from_markdown(cls, filepath: str | Path) -> "Companies":
        lines = Path(filepath).read_text().splitlines()
        companies = [line.split(",") for line in lines]
        company_objs = [Company(name=c[0], cik=c[1]) for c in companies]
        return cls(companies=company_objs)


def get_company_filings(company_name: str) -> list[SECFiling]:
    cik = get_cik(company_name)
    company = Company(name=company_name, cik=cik)
    return company.filings


def get_company_filing(company_name: str) -> SECFiling:
    filings = get_company_filings(company_name)
    if filings:
        return filings[0]
    else:
        raise ValueError(f"No filings found for company {company_name}")


if __name__ == "__main__":
    # filing = get_company_filing(company)
    # print(f"Latest filing for {company} ({filing.date}):")
    # print(filing.content)
    # companies = Companies.from_markdown(Path(__file__).parent / "10k_companies.md")
    # companies.companies[-1].filings[0].print()

    # Get last two filings for Duolingo
    company = "Duolingo"
    filings = get_company_filings(company)
    print("<filing1>")
    filings[0].print()
    print("</filing1>\n<filing2>")
    filings[1].print()
    print("</filing2>")
