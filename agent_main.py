from typing import Optional, List
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Tools
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from tools.real_estate_tools import RealEstateReserveTool, RealEstateSearchTool
from tools.feng_shui_tools import FengShuiRecommendationTool

#  SQL database
from functions.postgresql_functions import save_data , get_user_messages

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

def run_agent(history: Optional[List[BaseMessage]] = None):
    agent = create_agent()
    print('Agent is now running')

    # Configuration for session ID
    config = {"configurable": {"thread_id": 'tester'}}

    # 如果有提供歷史消息，將它們更新到代理的內存中
    if history:
        agent.update_state(config, {"messages": history})
    
    sys_prompt = '你是一位房地產輔助機器人負責協助使用者'
    SystemMessage(content=sys_prompt)
    agent.update_state(config, {"messages": sys_prompt})

    while True:
        question = input("Please enter your question (or 'Q' to quit): ")
        if question.upper() == "Q":
            break

        # Invoke the agent with the provided session ID
        response = agent.invoke({"messages": [HumanMessage(content=question)]}, config)
        if response["messages"][-1].tool_calls:
            print(response["messages"][-1].tool_calls)
        print(response["messages"][-1].content)  # Print the agent's response


def run_line_agent(user_id: str, question: str, timestamp: int):

    # Initialize agent
    agent = create_agent()
    config = {"configurable": {"thread_id": user_id}}
    
    # Load chat history from the database
    initial_history = []
    chat_history = get_user_messages(user_id)
    # chat_history maximum numbers is 5 (can be adjust in get_user_messages() sql lang)
    if chat_history is not None :
        for row_data in chat_history:
            initial_history.append(HumanMessage(content=row_data[0]))
            initial_history.append(AIMessage(content=row_data[1]))
    else:
        print("No sufficient history messages from this user")

    # Update agent state with initial chat history if available
    if initial_history:
        agent.update_state(config, {"messages": initial_history})
    else:
        agent.update_state(config, {"messages": []})

    # Load system prompt and add it to the chat history
    sys_prompt = '你是一位房地產輔助機器人負責協助使用者，不要使用 Markdown 語法'
    initial_history.append(SystemMessage(content=sys_prompt))
    agent.update_state(config, {"messages": initial_history})

    # Process user question
    response = agent.invoke({"messages": [HumanMessage(content=question)]}, config)
    agent_answer = response["messages"][-1].content

    # Save user message and agent response to the database
    user_message = {
        'user_message': question,
        'user_id': user_id,
        'timestamp': timestamp
    }
    agent_message = {
        'agent_message': agent_answer
    }
    save_data(user=user_message, agent=agent_message)

    return agent_answer

def test_line_agent():
    user_id = 'Baka!>///<'

    while True:
        question = input("Please enter your question (or 'Q' to quit): ")
        current_dt = datetime.now()
        timestamp = int(round(current_dt.timestamp()))

        if question.upper() == "Q":
            break

        answer = run_line_agent(user_id=user_id, question=question, timestamp=timestamp)
        print(f"Agent: {answer}")



if __name__ == '__main__':
    run_agent()

    
