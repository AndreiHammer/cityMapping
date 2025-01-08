# IATA City Codes Extractor

## Overview
This project is a Python-based solution for extracting IATA city codes from a PDF file and converting the data into a structured JSON format. It leverages **LangChain**, **OpenAI's GPT models**, and **PyPDFLoader** to parse and process the PDF file into a clean JSON dataset.

The IATA codes provide a standardized reference for city and airport codes used worldwide in travel and logistics. The source of the PDF used in this project is available [here](https://akhreis.wordpress.com/wp-content/uploads/2015/11/002-city-codes.pdf).

---

## Features
- **Automated Data Extraction**: Extracts city names and their corresponding IATA codes from the PDF.
- **Validation Logic**: Ensures correct key-value pairing for cities and IATA codes, detecting and correcting inversions.
- **JSON Output**: Outputs the extracted data in a user-friendly JSON format for further use in applications.

---

## Requirements
To run this project, you need the following:
- Python 3.9 or higher
- An OpenAI API Key (stored in a `.env` file)
---
### Python Libraries
Install the required dependencies with:
```bash
pip install langchain pydantic python-dotenv
```
---
## Setup Instructions

- Clone the repository

```bash
  git clone https://github.com/AndreiHammer/city_IATA_Mapping
  cd city_IATA_Mapping

```
- Open *PyCharm* or another Python IDE and choose the *Open an Existing Project* option. Navigate to the cloned repository and select it.
- Set up API Keys
    
    Create a file named `.env` in the root directory of the project and add the following keys: 

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key
```
-Run the script
```bash
  python script.py
```
- The JSON file containing the extracted data will be saved in the data directory as *city_to_iata.json*

---

## Key Components
- **LangChain**: To build a pipeline for prompt-based data extraction.
- **PyPDFLoader**: To load and parse the content of the PDF file.
- **OpenAI GPT Model**: For intelligent data extraction and formatting.
- **Pydantic**: For validating the structure of the extracted data.

---

## Future Enhancements
- Add support for extracting data from other PDF sources.
- Implement a web interface to upload PDFs and download JSON outputs.
- Enhance validation logic for more complex cases.

---

## License
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/). Feel free to use, modify, and distribute this project as per the terms of the license.
