# CDP Agentkit LangChain Extension Examples - Financial Advisor Python

This example demonstrates an agent setup as a terminal style chatbot with access to act as a financial advisor. The advisor has a conservative investment style that guides the user through managing investments on Compound and safely borrowing small amounts for daily spending.

## Ask the chatbot to help you invest!
- "Show me my portfolio"
- "Supply 0.0001 WETH to Compound, wrap ETH if needed"
- "Can I borrow 1 USDC?"
- "What is my collateral ratio?"

## Requirements
- Python 3.10+
- Poetry for package management and tooling
  - [Poetry Installation Instructions](https://python-poetry.org/docs/#installation)
- [CDP API Key](https://portal.cdp.coinbase.com/access/api)
- [OpenAI API Key](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)

### Checking Python Version
Before using the example, ensure that you have the correct version of Python installed. The example requires Python 3.10 or higher. You can check your Python version by running:

```bash
python --version
poetry --version
```

## Installation
```bash
poetry install
```

## Run the Chatbot

### Set ENV Vars
- Ensure the following ENV Vars are set:
  - "CDP_API_KEY_NAME"
  - "CDP_API_KEY_PRIVATE_KEY"
  - "OPENAI_API_KEY"
  - "NETWORK_ID" (Defaults to `base-sepolia`)

```bash
poetry run python chatbot.py
``` 

# Example Conversation with Financial Advisor Agent

> **User**: Check my wallet balance.

```text
Agent:
Your wallet balance is approximately 0.0158 ETH.

Native balance at address 0xB6f31b8b0D7BA9Dc4737dc341d6D5645CD0028Ae: 15782958277838
```

> **User**: Supply 0.0001 WETH to Compound, wrap ETH if needed.

```text
Agent:
I successfully supplied 0.0001 WETH to Compound. However, there was an error wrapping ETH due to insufficient funds. Your health ratio in Compound improved to 431.18.

Error wrapping ETH: {'code': -32000, 'message': 'insufficient funds for transfer'}
```

> **User**: Show me my portfolio.

```text
Agent:
Here are your portfolio details:

- You have supplied 0.0008 WETH, valued at approximately $2.78.
- You have borrowed 0.005 USDC, which has no current value.
- Your overall health ratio is 431.18.

# Portfolio Details

## Supply Details

### WETH
- **Supply Amount:** 0.000800000000000000
- **Price:** $3477.28
- **Collateral Factor:** 0.78
- **Asset Value:** $2.78

### Total Supply Value: $2.78

## Borrow Details

### USDC
- **Borrow Amount:** 0.005000
- **Price:** $1.00
- **Borrow Value:** $0.00

## Overall Health

- **Health Ratio:** 431.18
```

> **User**: Can I borrow 0.001 USDC?

```text
Agent:
Your current health ratio is 431.18, which is healthy. You can borrow 0.001 USDC. I will proceed with the borrowing now.
```

> **User**: Can I borrow 1 USDC?

```text
Agent:
You can only borrow amounts that maintain a healthy collateral ratio. Since your current borrow amount is 0.005 USDC, borrowing 1 USDC would lower your health ratio below 2. Therefore, I can only proceed with the borrowing of 0.001 USDC, as previously mentioned.
```

> **User**: Is it safe to borrow more USDC?

```text
Agent:
No, it's not safe to borrow more USDC at this time. Borrowing additional funds would lower your health ratio below the safe threshold of 2. It's best to maintain your current borrow level to ensure your collateral stays healthy.
```

> **User**: What is my collateral ratio?

```text
Agent:
Your current collateral ratio is 431.18, which indicates a healthy position. This means your collateral is significantly higher than your borrowed amount.
```