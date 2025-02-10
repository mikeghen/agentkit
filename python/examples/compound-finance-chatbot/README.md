# Compound Finance AI Agent Chatbot 

This example demonstrates an AI agent that can interact with Compound Finance protocols through a terminal-style chatbot interface. The agent can perform various DeFi operations including supplying assets, borrowing, managing collateral, and more. The agent is powered by the Coinbase Developer Platform AgentKit and the CDP SDK. This example is built with LangChain and uses OpenAI for the LLM.

## Example DeFi Operations with Compound Finance
Try asking the chatbot to:
- Supply ETH or WETH as collateral to Compound
- Borrow USDC against your supplied collateral
- Check your health ratio and portfolio details
- Repay borrowed assets
- Withdraw your supplied collateral


## Requirements
- Python 3.10+
- Poetry for package management and tooling
  - [Poetry Installation Instructions](https://python-poetry.org/docs/#installation)
- [CDP API Key](https://portal.cdp.coinbase.com/access/api)
- [OpenAI API Key](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)

### Checking Python Version
Before using the example, ensure that you have the correct version of Python installed. The example requires Python 3.10 or higher. You can check your Python version by running the following code:

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
make run
```


## Demonstration of Compound Finance AgentKit Actions

### Wraps ETH to WETH
```
Prompt: Use the default wallet to wrap 0.0001 ETH to WETH, then show me my WETH balance for the default wallet address.
-------------------
Wrapped 0.0001 ETH with transaction hash: 0x6bf7c912653faa3003dfeff76c0ca3b090507f5437b4d0f5447f22722f7a0ca2
-------------------
I have successfully wrapped **0.0001 ETH** to WETH. You can view the transaction details [here](https://sepolia.basescan.org/tx/0x6bf7c912653faa3003dfeff76c0ca3b090507f5437b4d0f5447f22722f7a0ca2).
-------------------
```

### Supplies WETH to Compound
```
Prompt: Next, supply the 0.0001 WETH to compound finance.  
-------------------
Supplied 0.0001 WETH to Compound V3.
Transaction hash: 0xbe800f1eb3c7e4d7067addb016a7d78c341f879d9aee22c12be02f4cea5d13ef
Transaction link: https://sepolia.basescan.org/tx/0xbe800f1eb3c7e4d7067addb016a7d78c341f879d9aee22c12be02f4cea5d13ef
-------------------
I have successfully supplied **0.0001 WETH** to Compound Finance. You can view the transaction details [here](https://sepolia.basescan.org/tx/0xbe800f1eb3c7e4d7067addb016a7d78c341f879d9aee22c12be02f4cea5d13ef). 

If you have any more requests or questions, just let me know!
-------------------
```

### Borrows USDC from Compound
```
Prompt: Next, borrow 0.01 USDC from compound
-------------------
Borrowed 0.01 USDC from Compound V3.
Transaction hash: 0x1d2c8e7f18d8dd9fa5410f4e6444751fa95b6c4ccfa4a4d4be1c594dba0ca215
Transaction link: https://sepolia.basescan.org/tx/0x1d2c8e7f18d8dd9fa5410f4e6444751fa95b6c4ccfa4a4d4be1c594dba0ca215
-------------------
I have successfully borrowed **0.01 USDC** from Compound. You can view the transaction details [here](https://sepolia.basescan.org/tx/0x1d2c8e7f18d8dd9fa5410f4e6444751fa95b6c4ccfa4a4d4be1c594dba0ca215).

If you have any further requests or questions, feel free to ask!
-------------------
```

### Gets Its Compound Portfolio Details
```
Prompt: What is my health ratio on Compound?
-------------------
# Portfolio Details

## Supply Details

### WETH
- **Supply Amount:** 0.000100000000000000
- **Price:** $3477.28
- **Collateral Factor:** 0.78
- **Asset Value:** $0.35

### Total Supply Value: $0.35

## Borrow Details

### 0x036CbD53842c5426634e7929541eC2318f3dCF7e
- **Borrow Amount:** 0.010000
- **Price:** $1.00
- **Borrow Value:** $0.01

## Overall Health

- **Health Ratio:** 26.95

-------------------
Your health ratio on Compound is **26.95**. 

If you need any further assistance or have more questions, feel free to ask!
-------------------
```
### Repays USDC to Compound
```
Prompt: Repay 0.01 USDC to Compound
-------------------
Repaid 0.01 USDC to Compound V3.
Transaction hash: 0x0de530f9b7dd0045b9581e0768547f538407b9e01312e44aee904a8215833b4f
Transaction link: https://sepolia.basescan.org/tx/0x0de530f9b7dd0045b9581e0768547f538407b9e01312e44aee904a8215833b4f
-------------------
I have successfully repaid **0.01 USDC** to Compound. You can view the transaction details [here](https://sepolia.basescan.org/tx/0x0de530f9b7dd0045b9581e0768547f538407b9e01312e44aee904a8215833b4f).

If you have any more requests or questions, just let me know!
-------------------
```

### Withdraws USDC from Compound
```
Prompt: Withdraw half of the WETH we have in Compound
-------------------
Withdrew 0.00005 WETH from Compound V3.
Transaction hash: 0x1d55b5d75468877cfe96d2ccf878fb264744fb76af0e754fc4fea6aed8cf8977
Transaction link: https://sepolia.basescan.org/tx/0x1d55b5d75468877cfe96d2ccf878fb264744fb76af0e754fc4fea6aed8cf8977
-------------------
I have successfully withdrawn **0.00005 WETH** from Compound. You can view the transaction details [here](https://sepolia.basescan.org/tx/0x1d55b5d75468877cfe96d2ccf878fb264744fb76af0e754fc4fea6aed8cf8977).

If you have any more requests or questions, feel free to ask!
-------------------
```

### Unwraps WETH to ETH
```
Prompt: Unwrap 0.0001 WETH to ETH
-------------------
Unwrapped 0.0001 WETH with transaction hash: 0x48ec8a391bf9ddd91829b1ba3467944865cefdeafc51548b2c0d4df30d29f135
-------------------
I have successfully unwrapped **0.0001 WETH** to ETH. You can view the transaction details [here](https://sepolia.basescan.org/tx/0x48ec8a391bf9ddd91829b1ba3467944865cefdeafc51548b2c0d4df30d29f135).

If you have any more requests or questions, feel free to ask!
-------------------
```