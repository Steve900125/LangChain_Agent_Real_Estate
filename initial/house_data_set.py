from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import json

# File path constants
FILE: Path = Path(__file__).resolve()
ROOT: Path = FILE.parents[1]
DATA_DIR: Path = ROOT / 'data'
HOUSE_FILE: Path = DATA_DIR / 'house.json'

# Load city and county data function
def load_city_county_to_pandas() -> pd.DataFrame:
    """Load city and county data from a JSON file into a pandas DataFrame."""
    CITY_COUNTY: Path = DATA_DIR / 'CityCountyData.json'
    
    with CITY_COUNTY.open("r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    city_data: List[Dict[str, str]] = []
    for city in data:
        city_name: str = city["CityName"]
        city_eng_name: str = city["CityEngName"]
        for area in city["AreaList"]:
            zip_code: str = area["ZipCode"]
            area_name: str = area["AreaName"]
            area_eng_name: str = area["AreaEngName"]
            city_data.append({
                "CityName": city_name,
                "CityEngName": city_eng_name,
                "ZipCode": zip_code,
                "AreaName": area_name,
                "AreaEngName": area_eng_name
            })

    df: pd.DataFrame = pd.DataFrame(city_data)
    return df

# Create house sample function
def create_house_sample():
    """Create house sample data if house.json does not already exist in the data directory."""
    # Check if house.json already exists
    if HOUSE_FILE.exists():
        print(f"{HOUSE_FILE} already exists. Skipping creation.")
        return
    
    # Load city and county data
    df = load_city_county_to_pandas()

    # Prepare sample house data
    house_data: List[Dict[str, Any]] = []
    prices = [1000, 2000, 3000]  # Prices in tens of millions
    house_id = 1  # Initialize a unique ID for each house

    for _, row in df.iterrows():
        for price in prices:
            house_data.append({
                "City": row["CityName"],
                "District": row["AreaName"],
                "Price": price,
                "CaseName": f"house_{house_id}"  # Generate unique house name with ID
            })
            house_id += 1  # Increment ID for each house

    # Save the generated data to house.json
    with HOUSE_FILE.open("w", encoding="utf-8") as f:
        json.dump(house_data, f, ensure_ascii=False, indent=4)
    
    print(f"House sample data created and saved to {HOUSE_FILE}")

# Run the function if executed as a script
if __name__ == "__main__":
    create_house_sample()
