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
from console_formatter import ChatbotConsole

# Configure a file to persist the agent's CDP API Wallet Data.
wallet_data_file = "wallet_data.txt"

load_dotenv()
console = ChatbotConsole()


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
        # "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
        # "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
        # "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
        # "details and request funds from the user. Before executing your first action, get the wallet details "
        # "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
        # "again later. If someone asks you to do something you can't do with your currently available tools, "
        # "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
        # "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
        # "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        f"Role: {advisor.get('role', '')}\n"
        f"Goal: {advisor.get('goal', '')}\n"
        f"Financial Plan: {advisor.get('financial_plan', '')}"  
    )

    # Use langchain tools from Agentkit.
    tools = get_langchain_tools(agentkit)

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    # Pass the state_prompt read from YAML directly as a string.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=state_prompt,
    ), config


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    console.print_success("Starting autonomous mode...")
    
    while True:
        try:
            # Provide instructions autonomously
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            console.print_user_message("Autonomous Thought: " + thought)
            console.print_divider()

            ai_response = ""
            action_output = ""

            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                if "agent" in chunk:
                    ai_response = chunk["agent"]["messages"][0].content
                elif "tools" in chunk:
                    action_output = chunk["tools"]["messages"][0].content
            
            if ai_response or action_output:
                combined_response = ai_response
                if action_output:
                    if combined_response:
                        combined_response += "\n\n"
                    combined_response += f"[ai_action]{action_output}[/ai_action]"
                console.print_ai_response(combined_response)
                console.print_divider()
            
            time.sleep(interval)

        except KeyboardInterrupt:
            console.print_warning("Goodbye Agent!")
            sys.exit(0)


def run_scripted_chat(agent_executor, config):
    """Run the agent with predefined prompts."""
    prompts = [
        "Get ETH from the Faucet.",
        "Check my wallet balance.",
        "Supply 0.0001 WETH to Compound, wrap ETH if needed.",
        "Show me my portfolio.",
        "Can I borrow 0.001 USDC?",
        "Can I borrow 1 USDC?",
        "Is it safe to borrow more USDC?",
        "What is my collateral ratio?",
        "Please withdraw all my funds so I can pay off credit card debt",
        "Use my balance to pay off my debt",
        "I want to borrow as much as safely possible in USDC, right now.",
        "Leverage my position 20x so that I can day trade"
    ]

    console.print_success("Starting Scripted Chat Session")
    
    for prompt in prompts:
        console.print_user_message(prompt)
        console.print_divider()
        
        ai_response = ""
        action_output = ""

        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=prompt)]}, config
        ):
            if "agent" in chunk:
                ai_response = chunk["agent"]["messages"][0].content
            elif "tools" in chunk:
                action_output = chunk["tools"]["messages"][0].content
        
        if ai_response or action_output:
            combined_response = ai_response
            if action_output:
                if combined_response:
                    combined_response += "\n\n"
                combined_response += f"[ai_action]{action_output}[/ai_action]"
            console.print_ai_response(combined_response)
            console.print_divider()
        
        time.sleep(1)


def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        console.print_success("\nAvailable modes:")
        console.console.print("1. [bold cyan]chat[/bold cyan]    - Interactive chat mode")
        console.console.print("2. [bold cyan]auto[/bold cyan]    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        console.print_error("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    console.print_success("Initializing Agent...")
    agent_executor, config = initialize_agent()
    
    mode = choose_mode()
    if mode == "chat":
        run_scripted_chat(agent_executor=agent_executor, config=config)
    else:
        run_autonomous_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    main()