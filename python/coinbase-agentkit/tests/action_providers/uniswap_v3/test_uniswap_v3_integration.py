"""Integration test for Uniswap v3 WETH->USDC swap on Base Mainnet.

This test mirrors the style shown in other provider READMEs: it uses a real
EthAccount wallet, wraps ETH to WETH, approves the Uniswap router, and performs
an exactInputSingle swap from WETH to USDC.

Requires PRIVATE_KEY env var configured for EthAccount wallet provider.
"""

import os
import time
from decimal import Decimal

import pytest
from eth_account import Account
from web3 import Web3

from coinbase_agentkit.action_providers.uniswap_v3.constants import (
    UNISWAP_SWAP_ROUTER_ABI,
    UNISWAP_V3_ADDRESSES,
    UNISWAP_QUOTER_ABI,
)
from coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider import (
    UniswapV3ActionProvider,
)
from coinbase_agentkit.action_providers.weth.weth_action_provider import WethActionProvider
from coinbase_agentkit.action_providers.morpho.utils import approve as erc20_approve
from coinbase_agentkit.action_providers.compound.constants import (
    USDC_ADDRESS,
    WETH_ADDRESS,
)
from coinbase_agentkit.wallet_providers import EthAccountWalletProvider
from coinbase_agentkit.wallet_providers.eth_account_wallet_provider import (
    EthAccountWalletProviderConfig,
)

WAIT_TIME = 15
SWAP_FEE = 500

@pytest.fixture
def wallet() -> EthAccountWalletProvider:
    """Create an EthAccount wallet provider on base-mainnet (chainId 8453)."""
    private_key = os.environ.get("PRIVATE_KEY")
    assert private_key is not None, "You must set PRIVATE_KEY environment variable"
    assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"

    account = Account.from_key(private_key)
    print("account address", account.address)

    return EthAccountWalletProvider(
        config=EthAccountWalletProviderConfig(
            account=account,
            chain_id="8453",
        )
    )


@pytest.fixture
def weth_provider() -> WethActionProvider:
    return WethActionProvider()


@pytest.fixture
def uniswap_provider() -> UniswapV3ActionProvider:
    return UniswapV3ActionProvider()


@pytest.mark.integration
def test_uniswap_v3_swap_weth_to_usdc(wallet, weth_provider, uniswap_provider):
    """End-to-end swap WETH->USDC on base-mainnet.

    Steps:
    1) Wrap a small amount of ETH to WETH
    2) Approve SwapRouter to spend WETH
    3) Quote WETH -> USDC via QuoterV2 and swap using ~99% of quote as amountOutMinimum
    """

    # Step 0: Check account balance
    balance = wallet.get_balance()
    print("account balance", balance, "ETH")

    # Step 1: Wrap ETH to WETH
    wrap_amount_wei = str(Web3.to_wei(Decimal("0.00005"), "ether"))
    # print("wrap_amount_wei", wrap_amount_wei)
    # wrap_result = weth_provider.wrap_eth(wallet, {"amount_to_wrap": wrap_amount_wei})
    # assert "Wrapped" in wrap_result
    # time.sleep(WAIT_TIME)

    # Step 2: Approve Uniswap router to spend WETH
    # router = UNISWAP_V3_ADDRESSES["base-mainnet"]["swap_router_02"]
    approve_amount = int(wrap_amount_wei)
    # approve_receipt = erc20_approve(wallet, WETH_ADDRESS, router, approve_amount)
    # assert approve_receipt.get("status") == 1
    # time.sleep(WAIT_TIME)

    # Step 3: Get a quote using QuoterV2 (provider will apply ~1% buffer to set amountOutMinimum)
    quoter = UNISWAP_V3_ADDRESSES["base-mainnet"]["uniswap_quoter"]
    quote = wallet.read_contract(
        contract_address=quoter,
        abi=UNISWAP_QUOTER_ABI,
        function_name="quoteExactInputSingle",
        args=[
            {
                "tokenIn": Web3.to_checksum_address(WETH_ADDRESS),
                "tokenOut": Web3.to_checksum_address(USDC_ADDRESS),
                "amountIn": int(approve_amount),
                "fee": int(SWAP_FEE),
                "sqrtPriceLimitX96": 0,
            }
        ],
    )
    if isinstance(quote, (list, tuple)):
        quote = quote[0] if quote else 0
    print("quoted amountOut", quote)

    # Step 4: Swap WETH -> USDC, provider uses quoter to set amountOutMinimum
    args = {
        "token_in": WETH_ADDRESS,
        "token_out": USDC_ADDRESS,
        "fee": SWAP_FEE,
        "amount_in": approve_amount,
    }
    swap_response = uniswap_provider.swap_exact_input_single(wallet, args)
    print(swap_response)
    assert "Transaction hash" in swap_response


