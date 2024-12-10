from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Dict
from pathlib import Path
import sys

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  
sys.path.insert(0, str(ROOT))   # for import modules 
from functions.real_estate_functions import search_house, user_reserve

# 描述字典
descriptions: Dict[str, str] = {
    "base_input": "一律採用繁體中文輸入，這個變數 city_county 是臺灣的縣/市名稱。",
    "full_name_city": "採用完整名稱作為輸入，例如：台中->臺中市、台北->臺北市、雲林->雲林縣。",
    "full_name_district": "這個變數 district 是臺灣的區域名稱，採用完整名稱作為輸入，例如：西區、中正區、大安區。",
    "font_correction": '記得 "台" 跟 "臺" 是相同意思，但一律採用 "臺" 作為標準，遇到錯字請自動修正為標準輸入。',
    "price_upper": "price_upper_limit 代表預算的金額上限，該變數的單位為萬。",
    "price_lower": "price_lower_limit 代表預算的金額下限，該變數的單位為萬。",
    "unit_example": "舉例來說：'十萬' -> 10 , '1000萬' -> 1000 , '50000000' -> 5000。"
}

# 定義模型
class RealEstateSearchInput(BaseModel): 
    city_county: str = Field(
        ...,
        description=f"{descriptions['base_input']}\n{descriptions['full_name_city']}\n{descriptions['font_correction']}"
    )
    
    district: str = Field(
        None,
        description=f"{descriptions['full_name_district']}\n{descriptions['font_correction']}"
    )
 
    price_upper_limit: Optional[int] = Field(
        None,
        description=f"{descriptions['price_upper']}\n{descriptions['unit_example']}\n如果對方有提供可以選擇放入。"
    )
    
    price_lower_limit: Optional[int] = Field(
        None,
        description=f"{descriptions['price_lower']}\n{descriptions['unit_example']}\n如果對方有提供可以選擇放入。"
    )

class RealEstateSearchTool(BaseTool):
    name: str = 'search_house'  # 確保這裡有類型註釋 
    description: str = "這是一個幫助使用者找到屬於自己想要的房屋資訊的程式。 (請不要詢問區域與價格以外的條件，台灣地區皆屬範圍內)"  # 提供類型註釋 

    args_schema: Type[BaseModel] = RealEstateSearchInput
    

    def _run(self, city_county: str, district: str = None, price_upper_limit: Optional[int] = None, price_lower_limit: Optional[int] = None):
        target = search_house(city_county, district, price_upper_limit, price_lower_limit)
        return target

    def _arun(self, city_county: str, district: str, price_upper_limit: Optional[int], price_lower_limit: Optional[int]):
        raise NotImplementedError("This tool does not support async")


class RealEstateReserveInput(BaseModel):
    date: str = Field(..., description="預約看房的日期，格式為YYYY-MM-DD-HH")
    name: str = Field(..., description="預約者的姓名")
    phone: str = Field(..., description="預約者的電話號碼")
    description: Optional[str] = Field(None, description="額外的備註或需求")

class RealEstateReserveTool(BaseTool): 
    name: str = 'reserve_house_viewing'  # 確保這裡也有類型註釋
    description: str = "這是一個幫助使用者預約看房的程式。"  # 提供類型註釋

    args_schema: Type[BaseModel] = RealEstateReserveInput

    def _run(self, date: str, name: str, phone: str, other_des: Optional[str] = None) -> str:
        return user_reserve(date, name, phone, description=other_des)

    def _arun(self, date: str, name: str, phone: str, other_des: Optional[str] = None):
        raise NotImplementedError("This tool does not support async")
