import os
import sys
import time

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Add the Actions the Compound Finance Agent will need. 
from cdp_agentkit_core.actions.compound.supply import CompoundSupplyAction
from cdp_agentkit_core.actions.compound.repay import CompoundRepayAction
from cdp_agentkit_core.actions.compound.withdraw import CompoundWithdrawAction
from cdp_agentkit_core.actions.compound.borrow import CompoundBorrowAction
from cdp_agentkit_core.actions.compound.portfolio_details import CompoundPortfolioDetailsAction
from cdp_agentkit_core.actions.weth.wrap_eth import WrapEthAction
from cdp_agentkit_core.actions.weth.unwrap_eth import UnwrapWethAction

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"

load_dotenv()

def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini")

    wallet_data = None

    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    # Configure CDP Agentkit Langchain Extension.
    values = {}
    if wallet_data is not None:
        # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
        values = {"cdp_wallet_data": wallet_data}

    print(os.getenv("CDP_API_KEY_NAME"))
    print(os.getenv("CDP_API_KEY_PRIVATE_KEY"))
    agentkit = CdpAgentkitWrapper(
        cdp_api_key_name=os.getenv("CDP_API_KEY_NAME"),
        cdp_api_key_private_key=os.getenv("CDP_API_KEY_PRIVATE_KEY"),
        **values
    )

    # Persist the agent's CDP MPC Wallet Data.
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get compound-specific tools.
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    all_tools = cdp_toolkit.get_tools()
    
    # Filter tools to include only those that the Compound Finance Agent will need.
    tools = [
        tool for tool in all_tools
        if isinstance(tool, (
            CompoundSupplyAction,
            CompoundRepayAction,
            CompoundWithdrawAction,
            CompoundBorrowAction,
            CompoundPortfolioDetailsAction,
            WrapEthAction,
            UnwrapWethAction,
        ))
    ]

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and filtered compound tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        ),
    ), config

# Chat Mode
def run_agent(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()
    run_agent(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
