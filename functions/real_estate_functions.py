from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  
SAVE_SEARCH_LOG_FILE = True

# Define path to house.json
DATA_DIR = ROOT / 'data'
HOUSE_FILE = DATA_DIR / 'house.json'
SEARCH_LOG_FILE = DATA_DIR / "search_house_log.json"

# Define the directory path for reservations
RESERVATION_DIR = Path('./data/reservation')

from typing import List, Dict, Any
import json
from pathlib import Path


def log_search_results(results: List[Dict[str, Any]]) -> None:
    """
    Appends a list of search results to the search_house_log.json file.
    
    Args:
        results: A list of dictionaries containing house search results.
    """
    # Load existing log data or initialize a new list
    if SEARCH_LOG_FILE.exists():
        with SEARCH_LOG_FILE.open("r", encoding="utf-8") as f:
            log_data = json.load(f)
    else:
        log_data = []

    # Append the new results directly
    log_data.append(results)

    # Save the updated log data back to the file
    with SEARCH_LOG_FILE.open("w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=4)


def search_house(
    city_county: str, 
    district: str,
    price_upper_limit: Optional[int] = None,
    price_lower_limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Search houses based on city, district, and price range."""

    # Read house data from house.json
    with HOUSE_FILE.open("r", encoding="utf-8") as f:
        house_data = json.load(f)

    # Set default values if limits are not provided
    if price_lower_limit is None:
        price_lower_limit = 0
    if price_upper_limit is None:
        price_upper_limit = 999999

    # Filter houses based on provided criteria
    results = [
        house for house in house_data
        if house["City"] == city_county
        and house["District"] == district
        and price_lower_limit <= house["Price"] <= price_upper_limit
    ]

    if SAVE_SEARCH_LOG_FILE is True:
        log_search_results(results)

    return results


def user_reserve(
    date: str, 
    name: str, 
    phone: str, 
    description: Optional[str] = None
) -> str:
    """Create a reservation entry in a JSON file with the current timestamp and name as the filename."""

    # Check for required fields
    if not date or not name or not phone:
        raise ValueError("Date, name, and phone are required fields.")

    # Ensure the reservation directory exists
    RESERVATION_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare reservation data
    reservation_data: Dict[str, Any] = {
        "date": date,
        "name": name,
        "phone": phone,
        "description": description or ""  # Use an empty string if no description is provided
    }

    # Generate a unique file name using current time and name
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = name.replace(" ", "_")  # Replace spaces with underscores in the name
    file_path = RESERVATION_DIR / f"{current_time}_{safe_name}.json"

    # Save the reservation data to the JSON file
    with file_path.open("w", encoding="utf-8") as f:
        json.dump([reservation_data], f, ensure_ascii=False, indent=4)
    
    # Check if the file was successfully created
    if file_path.exists():
        print(f"Reservation saved successfully for {date} in file: {file_path.name}")
        return '預約成功'
    else:
        return '預約失敗，請稍後再試'


# Example usage
if __name__ == "__main__":
    # Example search criteria
    search_results = search_house(
        city_county="臺北市",
        district="中正區",
        price_upper_limit=3000,
        price_lower_limit=1000
    )
    print(search_results)

    # Sample reservation with dynamic file naming
    user_reserve(
        date="2023-10-25",
        name="Jane Doe",
        phone="987654321",
        description="This is a sample reservation."
    )
    