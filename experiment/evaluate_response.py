from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import json

# Tools
from pathlib import Path
import sys
from typing import Any

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  
sys.path.insert(0, str(ROOT))  # for import modules

DATA_DIR = ROOT / 'data'
EVALUATE_DATA = DATA_DIR / 'questions_answers.json'
EVALUATE_RESULT= DATA_DIR / 'evaluate_result.json'
SEARCH_LOG_FILE = DATA_DIR / "search_house_log.json"


from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from tools.real_estate_tools import RealEstateReserveTool, RealEstateSearchTool
from tools.feng_shui_tools import FengShuiRecommendationTool

def ensure_file_exists(file_path: Path, default_data: Any):
    """
    確保文件存在。如果文件不存在，創建並寫入默認數據。
    
    Args:
        file_path: 要檢查的文件路徑。
        default_data: 文件不存在時寫入的默認數據。
    """
    if not file_path.exists():
        print(f"File {file_path} does not exist. Creating it with default data.")
        file_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)

def evaluate_and_log_results():
    """
    比較 EVALUATE_DATA 和 SEARCH_LOG_FILE 的答案，計算總分與正確率，
    並將結果記錄到 evaluate_result.json。
    """
    # 確保文件存在
    ensure_file_exists(EVALUATE_DATA, {})
    ensure_file_exists(SEARCH_LOG_FILE, [])

    # 讀取 EVALUATE_DATA
    with EVALUATE_DATA.open("r", encoding="utf-8") as f:
        evaluate_data = json.load(f)

    # 讀取 SEARCH_LOG_FILE
    with SEARCH_LOG_FILE.open("r", encoding="utf-8") as f:
        search_log = json.load(f)

    # 確保 SEARCH_LOG_FILE 是列表結構
    if not isinstance(search_log, list):
        print("SEARCH_LOG_FILE is not in the expected list format.")
        return

    # 初始化結果記錄
    correct_questions = {}
    incorrect_questions = {}
    total_questions = len(evaluate_data)
    correct_count = 0

    # 遍歷 EVALUATE_DATA 和 SEARCH_LOG_FILE，逐一比較答案
    for idx, (qid, query_data) in enumerate(evaluate_data.items(), start=1):
        evaluate_answers = query_data["answer"]  # 獲取 EVALUATE_DATA 的答案

        # 確認 SEARCH_LOG_FILE 是否有對應索引
        if idx > len(search_log):
            print(f"SEARCH_LOG_FILE is missing data for {qid}.")
            incorrect_questions[qid] = {
                "question": query_data["question"],
                "expected": evaluate_answers,
                "actual": None
            }
            continue

        search_answers = search_log[idx - 1]  # 獲取 SEARCH_LOG_FILE 的答案

        # 比較兩者是否相同
        if evaluate_answers == search_answers:
            correct_questions[qid] = query_data
            correct_count += 1
        else:
            incorrect_questions[qid] = {
                "question": query_data["question"],
                "expected": evaluate_answers,
                "actual": search_answers
            }

    # 計算總分與正確率
    score = correct_count
    accuracy = correct_count / total_questions if total_questions > 0 else 0

    # 構造結果
    evaluate_result = {
        "total_questions": total_questions,
        "correct_count": correct_count,
        "incorrect_count": total_questions - correct_count,
        "accuracy": round(accuracy * 100, 2),
        "correct_questions": correct_questions,
        "incorrect_questions": incorrect_questions
    }

    # 將結果記錄到 evaluate_result.json
    with EVALUATE_RESULT.open("w", encoding="utf-8") as f:
        json.dump(evaluate_result, f, ensure_ascii=False, indent=4)

    print(f"Evaluation completed. Results saved to {EVALUATE_RESULT}")

def create_agent():
    # Memory with session ID
    memory = MemorySaver()
    # Load model (gpt-4o)
    model = ChatOpenAI(model="gpt-4o",verbose = True)
    # Load tools
    search = TavilySearchAPIWrapper()
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=2)
    tools = [RealEstateReserveTool(), RealEstateSearchTool(), FengShuiRecommendationTool(),tavily_tool]
    agent_executor = create_react_agent(model, tools, checkpointer=memory)
    
    return agent_executor

def one_time_agent(question: str):
    agent = create_agent()
    print('Agent is now running')

    # Configuration for session ID
    config = {"configurable": {"thread_id": 'tester'}}

    sys_prompt = '你是一位房地產輔助機器人負責協助使用者'
    SystemMessage(content=sys_prompt)
    agent.update_state(config, {"messages": sys_prompt})

    # Invoke the agent with the provided session ID
    response = agent.invoke({"messages": [HumanMessage(content=question)]}, config)

    if response["messages"][-1].tool_calls:
        print(response["messages"][-1].tool_calls)

    print(response["messages"][-1].content)  # Print the agent's response

def get_search_log_len():
    # 讀取 SEARCH_LOG_FILE
    with SEARCH_LOG_FILE.open("r", encoding="utf-8") as f:
        search_log = json.load(f)
    return len(search_log)

def clear_search_log():
    """
    清空 SEARCH_LOG_FILE 的內容。
    """
    with SEARCH_LOG_FILE.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
    print("SEARCH_LOG_FILE has been cleared.")

def clear_evaluate_log():
   
    with EVALUATE_RESULT.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
    print("EVALUATE_RESULT has been cleared.")

def append_null_in_search_log():
    """
    在 SEARCH_LOG_FILE 中加入一個空結果 []。
    """
    # 確保文件存在，並初始化為空列表（如文件不存在）
    if not SEARCH_LOG_FILE.exists():
        with SEARCH_LOG_FILE.open("w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    # 讀取 SEARCH_LOG_FILE
    with SEARCH_LOG_FILE.open("r", encoding="utf-8") as f:
        search_log = json.load(f)

    # 確保文件是列表結構
    if not isinstance(search_log, list):
        raise ValueError("SEARCH_LOG_FILE is not a list. Please check the file format.")

    # 添加一個空結果
    search_log.append([])

    # 將更新後的數據寫回 SEARCH_LOG_FILE
    with SEARCH_LOG_FILE.open("w", encoding="utf-8") as f:
        json.dump(search_log, f, ensure_ascii=False, indent=4)

    print(f"Appended an empty entry to SEARCH_LOG_FILE. Current length: {len(search_log)}")

def evaluate_questions():

    if not EVALUATE_DATA.exists():
        print(f"File {EVALUATE_DATA} does not exist.")
        return 
    
    with EVALUATE_DATA.open("r", encoding="utf-8") as f:
        data = json.load(f)

    clear_search_log()
    clear_evaluate_log()

    question_count = 0
    for _, query_data in data.items():
        question_count += 1
        question = query_data["question"]
        one_time_agent(question)
        if get_search_log_len() < question_count:
            append_null_in_search_log()

if __name__=="__main__":
   evaluate_questions()
   evaluate_and_log_results()