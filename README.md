
# Real Estate Agent Chatbot

This project implements a chatbot agent designed to assist users with real estate inquiries. The agent utilizes various tools, including real estate and Feng Shui recommendation tools, and integrates with a PostgreSQL database to retrieve and save chat history. It also uses the `LangChain` library to manage agent interactions, including handling user sessions and maintaining chat histories.

## Project Structure

- **`data`**: Contains data-related files, including reservation records.
- **`functions`**: Contains functions for interacting with PostgreSQL and other backend functionalities.
- **`initial`**: initial setting can be found in here.
- **`tools`**: Contains custom tools used by the agent, including real estate and Feng Shui tools.
- **`agent_main.py`**: Main entry point for running the agent in CLI mode.
- **`requirements.txt`**: Lists dependencies required for this project.
- **`.env`**: Stores environment variables, such as database credentials.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd LANGCHAIN_NEW
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Full install (api key database url)
   ```bash
   python initial\initial_all.py
   ```

3. Configure environment variables:
   - Create a `.env` file in the root directory and add the necessary environment variables (e.g., for database access).

## Usage

### Running the Agent

The agent can be run in two main modes:

1. **Interactive Mode (`test_line_agent`)**
   - This mode runs an interactive session where you can continuously ask questions.
   - Run the following command:
     ```bash
     python agent_main.py
     ```
   - Enter questions to interact with the agent. Type `Q` to exit.

2. **Function Call (`run_line_agent`)**
   - This function can be used to invoke the agent for specific user inquiries, typically when integrating with another system (e.g., a web service).
   - It takes `user_id`, `question`, and `timestamp` as inputs.

### Functions Overview

- **`create_agent`**: Initializes and returns an agent with memory, tools, and model configurations.
- **`run_agent`**: Runs the agent in a loop to answer user questions continuously.
- **`run_line_agent`**: Processes a single user query, retrieves chat history from the database, invokes the agent, and saves the conversation to the database.
- **`test_line_agent`**: Entry point for CLI testing, allowing interactive input.

### Key Tools and Integrations

- **RealEstateReserveTool** and **RealEstateSearchTool**: Handle reservation and search tasks related to real estate.
- **FengShuiRecommendationTool**: Provides Feng Shui recommendations based on the user's query.
- **TavilySearchAPIWrapper**: Integrates a third-party search API.
- **MemorySaver**: Saves agent’s memory with session IDs to retain context.
- **PostgreSQL Database**:
  - **`save_data`**: Saves user and agent messages to the database.
  - **`get_user_messages`**: Retrieves previous messages from the database.

### Example Code Snippets

To create and run the agent directly:
```python
from agent_main import run_line_agent

user_id = 'user123'
question = "What are the best property deals nearby?"
timestamp = int(datetime.now().timestamp())

response = run_line_agent(user_id=user_id, question=question, timestamp=timestamp)
print(response)
```

## Configuration

- **Session Configuration**: The agent maintains session memory by associating user conversations with a unique `thread_id`. This is handled by setting `thread_id` as `user_id`.
- **History Management**: The agent loads up to 5 previous messages from the database to retain context in each session. Adjust this limit in the `get_user_messages` function if needed.

