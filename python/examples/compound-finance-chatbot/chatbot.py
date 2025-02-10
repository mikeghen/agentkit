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
            "You are a DeFi assistant specialized in Compound Finance operations. You can help users interact "
            "with Compound protocols through various operations like supplying assets, borrowing, managing "
            "collateral, and checking portfolio details. Before executing any operation, always check the "
            "wallet details to determine the network you're on. If you're on 'base-sepolia', you can request "
            "funds from the faucet. Otherwise, provide wallet details to the user for funding.\n\n"
            "You can help users with:\n"
            "- Supplying ETH/WETH as collateral\n"
            "- Borrowing USDC against supplied collateral\n"
            "- Checking health ratio and getting portfolio details\n"
            "- Repaying borrowed assets\n"
            "- Withdrawing supplied collateral\n\n"
            "You may encounter errors when using these tools. If you do, try to understand the error and resolve it.\n"
            "Be concise and action-oriented in your responses.\n"
        ),
    ), config

# Chat Mode
def run_agent(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\ncompound-finance-chatbot> ")
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
