import random
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import sys

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  
sys.path.insert(0, str(ROOT))  # for import modules
from functions.real_estate_functions import search_house

# Define path to house.json
DATA_DIR = ROOT / 'data'
CITY_COUNTY = DATA_DIR / 'CityCountyData.json'
OUTPUT_FILE = DATA_DIR / 'questions_answers.json'
SEARCH_LOG_FILE = DATA_DIR / "search_house_log.json"

def get_city_county() -> List[Dict[str, str]]:
    """
    Reads house data from house.json and extracts city and area information.
    """
    with CITY_COUNTY.open("r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)
    
    city_data: List[Dict[str, str]] = []

    for city in data:
        city_name: str = city["CityName"]
        for area in city["AreaList"]:
            area_name: str = area["AreaName"]
            city_data.append({
                "CityName": city_name,
                "AreaName": area_name,
            })
    return city_data

def clear_search_log():
    """
    清空 SEARCH_LOG_FILE 的內容。
    """
    with SEARCH_LOG_FILE.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
    print("SEARCH_LOG_FILE has been cleared.")

def generate_find_house_normal_questions_json(output_file: Path):
    """
    Generates random natural language questions and saves them with answers into a JSON file.

    Args:
        output_file: Path to the JSON file for storing questions and answers.

    Returns:
        None
    """

    clear_search_log()
    # Question components
    begin = {
        1: "我要找",
        2: "我想查看",
        3: "有沒有",
        4: "找",
        5: "看",
        6: "查詢",
    }

    intention = {
        1: "房子",
        2: "屋子",
        3: "不動產",
        4: "家",
        5: "屋",
        6: "房屋",
    }

    begin_loc = {
        1: "地點在",
        2: "位於",
        3: "坐落",
        4: "處在"
    }

    object_price = {
        1: "價格落在 900萬以上 2900萬以下",
        2: "900~2900",
        3: "大約900到2900之間",
        4: "9000000 ~ 29000000",
        5: "九百萬至兩千多萬之間",
        6: "九百之上 兩千之內",
    }

    city_county_data = get_city_county()

    # Validate city_county_data
    if not city_county_data:
        print("No city or district data available.")
        return

    # Prepare a dictionary to store questions and answers
    questions_answers: Dict[str, Dict[str, Any]] = {}

    # Generate questions based on the provided city and district data
    for i, location in enumerate(city_county_data, start=1):
        # Randomly choose components
        b = random.choice(list(begin.values()))
        i_ = random.choice(list(intention.values()))
        l = random.choice(list(begin_loc.values()))
        p = random.choice(list(object_price.values()))

        city = location["CityName"]
        district = location["AreaName"]

        # Construct the question
        question = f"{b}{i_}，{l}{city} {district} {p}。"

        # Call the search_house function
        ans = search_house(
            city_county=city,
            district=district,
            price_lower_limit=900,
            price_upper_limit=2900
        )

        # Add to the dictionary
        questions_answers[f"Q{i}"] = {
            "question": question,
            "answer": ans
        }

    # Save to a JSON file
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(questions_answers, f, ensure_ascii=False, indent=4)

    print(f"Questions and answers saved to {output_file}")

if __name__ == "__main__":
    generate_find_house_normal_questions_json(output_file=OUTPUT_FILE)
    