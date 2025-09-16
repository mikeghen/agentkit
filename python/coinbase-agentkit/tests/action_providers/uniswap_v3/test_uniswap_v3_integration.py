# """Integration test for Uniswap v3 multi-token swap chain on Base Mainnet.

# This test performs a complete swap chain using the new asset ID pattern:
# WETH → USDC → cbBTC → cbETH → WETH

# Features demonstrated:
# - Uses asset IDs ("weth", "usdc", "cbbtc", "cbeth") instead of token addresses
# - Uses human-readable amounts instead of wei
# - Automatic approval handling by the provider
# - Balance checking with user-friendly error messages
# - Always swaps maximum available balance for each step
# - Detailed logging of balances and swap amounts

# The test assumes existing WETH balance and performs the complete swap chain,
# showing how the new simplified interface works across multiple token types.

# Requires PRIVATE_KEY env var configured for EthAccount wallet provider.
# """

# import os
# import time
# from decimal import Decimal

# import pytest
# from eth_account import Account
# from web3 import Web3

# from coinbase_agentkit.action_providers.uniswap_v3.constants import (
#     ASSET_ADDRESSES,
#     UNISWAP_SWAP_ROUTER_ABI,
#     UNISWAP_V3_ADDRESSES,
#     UNISWAP_QUOTER_ABI,
# )
# from coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider import (
#     UniswapV3ActionProvider,
# )
# from coinbase_agentkit.wallet_providers import EthAccountWalletProvider
# from coinbase_agentkit.wallet_providers.eth_account_wallet_provider import (
#     EthAccountWalletProviderConfig,
# )

# WAIT_TIME = 20  # Increased wait time to ensure transactions are fully confirmed

# # Asset IDs for the swap chain
# WETH_ASSET_ID = "weth"
# USDC_ASSET_ID = "usdc"
# CBBTC_ASSET_ID = "cbbtc"
# CBETH_ASSET_ID = "cbeth"
# NETWORK_ID = "base-mainnet"

# # Common fee tiers for different pairs
# WETH_USDC_FEE = 500     # 0.05%
# USDC_CBBTC_FEE = 3000   # 0.30%
# CBBTC_CBETH_FEE = 3000  # 0.30%
# CBETH_WETH_FEE = 500    # 0.05%


# def get_token_balance_human(wallet, asset_id: str) -> str:
#     """Get human-readable token balance for an asset ID."""
#     from coinbase_agentkit.action_providers.uniswap_v3.utils import (
#         get_token_balance,
#         get_token_decimals,
#         format_amount_from_decimals,
#     )
    
#     token_address = ASSET_ADDRESSES[NETWORK_ID][asset_id]
#     balance_atomic = get_token_balance(wallet, token_address)
#     decimals = get_token_decimals(wallet, token_address)
#     return format_amount_from_decimals(balance_atomic, decimals)

# @pytest.fixture
# def wallet() -> EthAccountWalletProvider:
#     """Create an EthAccount wallet provider on base-mainnet (chainId 8453)."""
#     private_key = os.environ.get("PRIVATE_KEY")
#     assert private_key is not None, "You must set PRIVATE_KEY environment variable"
#     assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"

#     account = Account.from_key(private_key)
#     print("account address", account.address)

#     return EthAccountWalletProvider(
#         config=EthAccountWalletProviderConfig(
#             account=account,
#             chain_id="8453",
#         )
#     )


# @pytest.fixture
# def uniswap_provider() -> UniswapV3ActionProvider:
#     return UniswapV3ActionProvider()


# @pytest.mark.integration
# def test_uniswap_v3_swap_chain(wallet, uniswap_provider):
#     """End-to-end swap chain: WETH→USDC→cbBTC→cbETH→WETH using asset ID pattern.

#     Performs a complete swap chain always using maximum available balance:
#     1) Check existing WETH balance (assumes WETH is already available)
#     2) Swap all WETH → USDC 
#     3) Swap all USDC → cbBTC
#     4) Swap all cbBTC → cbETH
#     5) Swap all cbETH → WETH
#     """

#     print("="*80)
#     print("STARTING UNISWAP V3 SWAP CHAIN TEST")
#     print("="*80)

#     # Step 0: Check initial account balance
#     eth_balance = wallet.get_balance()
#     print(f"Initial ETH balance: {eth_balance}")

#     # Step 1: Check existing WETH balance (assume we already have WETH)
#     initial_weth_balance = get_token_balance_human(wallet, WETH_ASSET_ID)
#     print(f"\n1. CHECKING EXISTING WETH BALANCE")
#     print(f"Available WETH balance: {initial_weth_balance}")
    
#     # Verify we have some WETH to start with
#     assert float(initial_weth_balance) > 0, f"Need existing WETH balance to run swap chain test. Current balance: {initial_weth_balance}"

#     # Step 2: WETH → USDC (swap all WETH)
#     print(f"\n2. SWAPPING ALL WETH → USDC")
#     weth_balance = get_token_balance_human(wallet, WETH_ASSET_ID)
#     print(f"WETH balance before swap: {weth_balance}")
    
#     swap1_result = uniswap_provider.swap_exact_input_single(wallet, {
#         "token_in": WETH_ASSET_ID,
#         "token_out": USDC_ASSET_ID,
#         "fee": WETH_USDC_FEE,
#         "amount_in": weth_balance,
#     })
#     print(f"WETH→USDC result: {swap1_result}")
#     assert "Swapped" in swap1_result
    
#     # Wait longer and confirm transaction is fully settled
#     print(f"Waiting {WAIT_TIME} seconds for transaction to settle...")
#     time.sleep(WAIT_TIME)
    
#     usdc_balance = get_token_balance_human(wallet, USDC_ASSET_ID)
#     print(f"USDC balance after swap: {usdc_balance}")
#     assert float(usdc_balance) > 0, "Should have USDC balance after swap"

#     # Step 3: USDC → cbBTC (swap all USDC)
#     print(f"\n3. SWAPPING ALL USDC → cbBTC")
#     print(f"USDC balance before swap: {usdc_balance}")
    
#     swap2_result = uniswap_provider.swap_exact_input_single(wallet, {
#         "token_in": USDC_ASSET_ID,
#         "token_out": CBBTC_ASSET_ID,
#         "fee": USDC_CBBTC_FEE,
#         "amount_in": usdc_balance,
#     })
#     print(f"USDC→cbBTC result: {swap2_result}")
#     assert "Swapped" in swap2_result
    
#     print(f"Waiting {WAIT_TIME} seconds for transaction to settle...")
#     time.sleep(WAIT_TIME)
    
#     cbbtc_balance = get_token_balance_human(wallet, CBBTC_ASSET_ID)
#     print(f"cbBTC balance after swap: {cbbtc_balance}")
#     assert float(cbbtc_balance) > 0, "Should have cbBTC balance after swap"

#     # Step 4: cbBTC → cbETH (swap all cbBTC)
#     print(f"\n4. SWAPPING ALL cbBTC → cbETH")
#     print(f"cbBTC balance before swap: {cbbtc_balance}")
    
#     swap3_result = uniswap_provider.swap_exact_input_single(wallet, {
#         "token_in": CBBTC_ASSET_ID,
#         "token_out": CBETH_ASSET_ID,
#         "fee": CBBTC_CBETH_FEE,
#         "amount_in": cbbtc_balance,
#     })
#     print(f"cbBTC→cbETH result: {swap3_result}")
#     assert "Swapped" in swap3_result
    
#     print(f"Waiting {WAIT_TIME} seconds for transaction to settle...")
#     time.sleep(WAIT_TIME)
    
#     cbeth_balance = get_token_balance_human(wallet, CBETH_ASSET_ID)
#     print(f"cbETH balance after swap: {cbeth_balance}")
#     assert float(cbeth_balance) > 0, "Should have cbETH balance after swap"

#     # Step 5: cbETH → WETH (swap all cbETH, completing the circle)
#     print(f"\n5. SWAPPING ALL cbETH → WETH (completing the circle)")
#     print(f"cbETH balance before swap: {cbeth_balance}")
    
#     swap4_result = uniswap_provider.swap_exact_input_single(wallet, {
#         "token_in": CBETH_ASSET_ID,
#         "token_out": WETH_ASSET_ID,
#         "fee": CBETH_WETH_FEE,
#         "amount_in": cbeth_balance,
#     })
#     print(f"cbETH→WETH result: {swap4_result}")
#     assert "Swapped" in swap4_result
    
#     print(f"Waiting {WAIT_TIME} seconds for final transaction to settle...")
#     time.sleep(WAIT_TIME)
    
#     final_weth_balance = get_token_balance_human(wallet, WETH_ASSET_ID)
#     print(f"Final WETH balance: {final_weth_balance}")

#     # Summary
#     print(f"\n" + "="*80)
#     print("SWAP CHAIN COMPLETE - SUMMARY")
#     print("="*80)
#     print(f"Started with:     {initial_weth_balance} WETH")
#     print(f"Ended with:       {final_weth_balance} WETH")
#     print(f"Swap path:        WETH → USDC → cbBTC → cbETH → WETH")
#     print(f"Total transactions: 4 swaps (assuming existing WETH balance)")
#     print("="*80)
    
#     # Verify we have some WETH at the end (accounting for fees)
#     assert float(final_weth_balance) > 0, "Should have some WETH remaining after swap chain"


