import json

def get_country_name(country_code):
    try:
        # Try to get the country from the 2-letter code
        country = pycountry.countries.get(alpha_2=country_code)
        if country:
            return country.name

        # If not found, try with 3-letter code
        country = pycountry.countries.get(alpha_3=country_code)
        if country:
            return country.name
        
        # Handle special cases or codes not in pycountry
        special_cases = {
            "UK": "United Kingdom",
            "US": "United States",
            "UAE": "United Arab Emirates",
            "PF": "French Polynesia",
            "TL": "Timor-Leste",
            "XK": "Kosovo",
            # Add more special cases as needed
        }
        
        if country_code in special_cases:
            return special_cases[country_code]
        
        # If all else fails, return the code itself
        return country_code
    
    except Exception as e:
        print(f"Error processing country code {country_code}: {e}")
        return country_code

def convert_country_codes(input_file, output_file):
    try:
        # Load the JSON file
        print(f"Loading JSON from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Found {len(data)} entries in the JSON file")
        
        # Process each entry
        converted_count = 0
        for city, info in data.items():
            if "country" in info and isinstance(info["country"], str):
                country_code = info["country"]
                # Only convert if it looks like a country code (2 or 3 letters)
                if len(country_code) in [2, 3] and country_code.isalpha():
                    country_name = get_country_name(country_code)
                    if country_name != country_code:
                        info["country"] = country_name
                        converted_count += 1
        
        print(f"Converted {converted_count} country codes to full names")
        
        # Save the updated JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Updated JSON saved to {output_file}")
    
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    input_file = "data/city_to_iata2.json"
    output_file = "data/city_to_iata_full_countries.json"
    
    # Check if pycountry is installed
    try:
        import pycountry
    except ImportError:
        print("The pycountry package is not installed. Installing it now...")
        import subprocess
        subprocess.check_call(["pip", "install", "pycountry"])
        import pycountry
    
    convert_country_codes(input_file, output_file) 