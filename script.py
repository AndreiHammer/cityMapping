import os
import json
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


# Define the data model
class Document(BaseModel):
    city: str = Field(description="City Name")
    code: str = Field(description="IATA Code")


# Configure LLM
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
parser = JsonOutputParser()


# Function to load and extract text from the PDF
def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return [page.page_content for page in pages]


# Prompt for the LLM
prompt = PromptTemplate(
    template=(
        "You are a data extractor. Extract the information in JSON format, where the key is the city name and "
        "the value is its corresponding IATA code. Each entry must follow this structure: "
        "'City Name': 'IATA Code'. Ensure no inversions occur. Validate the output carefully before returning. "
        "Example: {{ 'Napoli': 'NAP', 'Bucharest': 'BUH' }}. \n{format_instructions}\n{context}"
    ),
    input_variables=["context"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


# Prepare data and process
def process_pdf_to_json(pdf_path: str, output_path: str):
    pages = load_pdf(pdf_path)  # Load the PDF pages
    results = {}

    for page_content in pages:
        # LangChain pipeline for each page
        chain = prompt | llm | parser
        try:
            # Execute the chain for the current page
            result = chain.invoke({"context": page_content})

            # Check if the result is a dictionary
            if isinstance(result, dict):
                # Iterate over the dictionary and validate keys/values
                for key, value in result.items():
                    # Ensure the key is a city name and value is a code
                    if len(key) == 3 and key.isalpha() and len(value) > 2:  # Likely inverted, fix it
                        key, value = value, key

                    document = Document(city=key, code=value)
                    results[document.city] = document.code
            else:
                print(f"Unexpected result format: {result}")

        except Exception as e:
            print(f"Error processing page: {e}")

    # Combine all results into a single JSON object
    with open(output_path, "w") as json_file:
        json.dump(results, json_file, indent=2)

    print(f"JSON successfully saved at {output_path}")


# Run the main function
if __name__ == "__main__":
    pdf_path = "data/iata-city-codes.pdf"
    output_path = "data/city_to_iata.json"
    process_pdf_to_json(pdf_path, output_path)
