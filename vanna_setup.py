"""
Vanna 2.0 Agent Initialization
Sets up the AI agent with all required components for NL2SQL
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Vanna 2.0 components
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.google import GeminiLlmService


def get_agent():
    """
    Initialize and return configured Vanna 2.0 Agent
    """
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    
    # Get database path
    db_path = Path(__file__).parent / "clinic.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}.")
    
    # 1. Create LLM Service (Updated to a valid model name)
    llm = GeminiLlmService(api_key=api_key, model="gemini-1.5-flash")
    
    # 2. Create Agent Memory
    agent_memory = DemoAgentMemory()
    
    # 3. Create SQLite Runner
    sql_runner = SqliteRunner(str(db_path))
    
    # 4. Create ToolRegistry and register required tools
    registry = ToolRegistry()
    
    # CRITICAL: Registering 'run_sql' so main.py can find it
    registry.register(RunSqlTool(sql_runner=sql_runner))
    
    # Register memory tools
    registry.register(SaveQuestionToolArgsTool(agent_memory=agent_memory))
    registry.register(SearchSavedCorrectToolUsesTool(agent_memory=agent_memory))
    
    # 5. Create UserResolver
    class DefaultUserResolver(UserResolver):
        def resolve_user(self, context: RequestContext) -> User:
            return User(user_id="default_user")
    
    user_resolver = DefaultUserResolver()
    
    # 6. Create Agent
    agent = Agent(
        llm_service=llm,
        tool_registry=registry,
        user_resolver=user_resolver,
        agent_memory=agent_memory
    )
    
    return agent


if __name__ == "__main__":
    # Test initialization
    try:
        agent = get_agent()
        print("✓ Vanna 2.0 Agent initialized successfully")
        # Fixed attribute names for Vanna 2.0
        print(f"Agent LLM: {agent.llm_service.__class__.__name__}")
        print(f"Agent Memory Items: {len(agent.agent_memory.get_all_mappings())}")
    except Exception as e:
        print(f"✗ Error initializing agent: {e}")