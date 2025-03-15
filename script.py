import os
import json
import re
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class Document(BaseModel):
    city: str = Field(description="City Name")
    code: str = Field(description="IATA Code")
    country: str = Field(description="Country")


llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
parser = StrOutputParser()


def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return [page.page_content for page in pages]


# Update the prompt template to include country
prompt = PromptTemplate(
    template=(
        "You are a data extractor specialized in IATA city codes. The following text contains a table with IATA city "
        "codes."
        "The table has multiple columns with the format: Code, City Name, State, Country, repeated several times "
        "across the page."
        "Extract ALL city-code pairs in the text. For each pair, output a single line in the format: 'City Name, Country: "
        "IATA_CODE'"
        "(where IATA_CODE is the 3-letter code). "
        "Be thorough and extract EVERY single city-code-country triplet in the text, even if there are hundreds. "
        "Do not skip any entries. Ensure the city name comes first, followed by the country, then the code. "
        "Example output format:\n"
        "New York, USA: NYC\n"
        "London, UK: LON\n"
        "Paris, France: PAR\n"
        "\n{context}"
    ),
    input_variables=["context"],
)


# Function to preprocess the PDF content to make it more parseable
def preprocess_pdf_content(content):
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', content)
    return content


# Function to parse the LLM output into a dictionary
# Update the parse_llm_output function to include country
def parse_llm_output(output_text):
    results = {}
    # Look for lines in the format "City Name, Country: CODE"
    pattern = r'([^,]+),\s*([^:]+):\s*([A-Z]{3})'
    matches = re.findall(pattern, output_text)

    for city, country, code in matches:
        city = city.strip()
        country = country.strip()
        code = code.strip()
        if city and code and len(code) == 3 and code.isalpha():
            if city not in results:
                results[city] = {"code": code, "country": country}

    return results


def extract_from_raw_content(content):
    results = {}
    # Pattern to match 3-letter code, city name, and country
    pattern = r'([A-Z]{3})\s+([A-Za-z\s\-\'\.]+?)\s+([A-Z]{2})\s+([A-Za-z\s\-\'\.]+)'
    matches = re.findall(pattern, content)

    for code, city, state, country in matches:
        city = city.strip()
        country = country.strip()
        if city and code and len(code) == 3 and code.isalpha():
            if city not in results:
                results[city] = {"code": code, "country": country}

    return results


# Prepare data and process
def process_pdf_to_json(pdf_path: str, output_path: str):
    pages = load_pdf(pdf_path)  # Load the PDF pages
    all_results = {}

    # First pass: Use regex to directly extract from raw content
    print("Performing direct extraction from PDF content...")
    for page_number, page_content in enumerate(pages):
        print(f"Processing page {page_number + 1}/{len(pages)} with direct extraction")
        direct_results = extract_from_raw_content(page_content)
        all_results.update(direct_results)

    print(f"Direct extraction found {len(all_results)} entries")

    # Second pass: Use LLM to extract more entries
    print("\nPerforming LLM-based extraction...")
    for page_number, page_content in enumerate(pages):
        print(f"Processing page {page_number + 1}/{len(pages)} with LLM")

        # Preprocess the content
        processed_content = preprocess_pdf_content(page_content)

        # Split long pages into smaller chunks
        max_chunk_size = 4000  # Adjust based on token limits
        chunks = [processed_content[i:i + max_chunk_size]
                  for i in range(0, len(processed_content), max_chunk_size)]

        for chunk_idx, chunk in enumerate(chunks):
            # LangChain pipeline for each chunk
            chain = prompt | llm | parser
            try:
                # Execute the chain for the current chunk
                result_text = chain.invoke({"context": chunk})

                # Parse the text output into a dictionary
                chunk_results = parse_llm_output(result_text)

                # Add new entries to the results
                for city, code in chunk_results.items():
                    if city not in all_results:
                        all_results[city] = code

                print(f"  Chunk {chunk_idx + 1}: Found {len(chunk_results)} entries")

            except Exception as e:
                print(f"Error processing page {page_number + 1}, chunk {chunk_idx + 1}: {str(e)}")

    # Look for patterns like "AAA Anaa" in the raw text as a final pass
    pattern = r'([A-Z]{3})\s+([A-Za-z\s\-\'\.]+)'
    for page_content in pages:
        matches = re.findall(pattern, page_content)
        for code, city in matches:
            city = city.strip()
            if city and code and len(code) == 3 and code.isalpha():
                # Only add if not already in results
                if city not in all_results and not any(c.isdigit() for c in city):
                    all_results[city] = code

    print(f"\nTotal entries extracted: {len(all_results)}")

    # Combine all results into a single JSON object
    with open(output_path, "w") as json_file:
        json.dump(all_results, json_file, indent=2)

    print(f"JSON successfully saved at {output_path}")


# Run the main function
if __name__ == "__main__":
    pdf_path = "data/iata-city-codes.pdf"
    output_path = "data/city_to_iata.json"
    process_pdf_to_json(pdf_path, output_path)
