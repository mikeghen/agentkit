import os
import sys
import json
import time
import yaml

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    compound_action_provider,
    erc20_action_provider,
    wallet_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools

# Configure a file to persist the agent's CDP API Wallet Data.
wallet_data_file = "wallet_data.txt"

load_dotenv()


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Initialize CDP Wallet Provider
    wallet_data = None
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    cdp_config = None
    if wallet_data is not None:
        cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)

    wallet_provider = CdpWalletProvider(cdp_config)

    agentkit = AgentKit(AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            cdp_api_action_provider(),
            cdp_wallet_action_provider(),
            compound_action_provider(),
            erc20_action_provider(),
            wallet_action_provider(),
            weth_action_provider(),
        ]
    ))

    wallet_data_json = json.dumps(wallet_provider.export_wallet().to_dict())

    with open(wallet_data_file, "w") as f:
        f.write(wallet_data_json)

    # Load financial advisor prompt from YAML
    # Construct the YAML file path relative to the current file.
    config_path = os.path.join(os.path.dirname(__file__), "config", "financial_advisor_agent.yaml")
    with open(config_path, "r") as yaml_file:
        fa_config = yaml.safe_load(yaml_file)
    advisor = fa_config.get("financial_advisor", {})
    state_prompt = (
        f"Role: {advisor.get('role', '')}\n\n"
        f"Goal: {advisor.get('goal', '')}\n\n"
        f"Financial Plan: {advisor.get('financial_plan', '')}"
    )

    # Use langchain tools from Agentkit.
    tools = get_langchain_tools(agentkit)

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    # Pass the state_prompt read from YAML as a tuple element.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(state_prompt,),
    ), config


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            # Provide instructions autonomously
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            # Run agent in autonomous mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            # Wait before the next action
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Chat Mode
def run_scripted_chat(agent_executor, config):
    """Run the agent with predefined prompts."""
    prompts = [
        "Get ETH",
        "Wrap 0.0001 ETH to WETH",
        "Supply 0.0001 WETH to Compound",
        "Borrow 0.001 USDC from Compound",
        "Get my Compound portfolio details",
        "Repay 0.001 USDC from Compound",
        "Withdraw 0.0001 WETH from Compound"
    ]

    print("Running scripted prompts...")
    for prompt in prompts:
        print(f"\nExecuting: {prompt}")
        print("-------------------")
        
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=prompt)]}, config
        ):
            if "agent" in chunk:
                print(chunk["agent"]["messages"][0].content)
            elif "tools" in chunk:
                print(chunk["tools"]["messages"][0].content)
            print("-------------------")
        
        # Add a small delay between prompts to avoid rate limiting
        time.sleep(1)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()
    run_scripted_chat(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
