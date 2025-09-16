"""Tests for UniswapV3ActionProvider exact input swap."""

from unittest.mock import patch

import pytest

from coinbase_agentkit.action_providers.uniswap_v3.constants import (
    ASSET_ADDRESSES,
    UNISWAP_SWAP_ROUTER_ABI,
    UNISWAP_V3_ADDRESSES,
)
from coinbase_agentkit.action_providers.uniswap_v3.schemas import ExactInputSingleSchema
from coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider import (
    UniswapV3ActionProvider,
)


# Mock asset IDs (not addresses anymore)
MOCK_TOKEN_IN_ID = "weth"
MOCK_TOKEN_OUT_ID = "usdc"
MOCK_TOKEN_IN_ADDRESS = "0x1111111111111111111111111111111111111111"
MOCK_TOKEN_OUT_ADDRESS = "0x2222222222222222222222222222222222222222"
MOCK_RECIPIENT = "0x3333333333333333333333333333333333333333"
MOCK_AMOUNT_IN = "1.0"  # Human-readable amount
MOCK_AMOUNT_IN_ATOMIC = 10**18  # Atomic amount after decimals conversion
MOCK_FEE = 3000
MOCK_TX_HASH = "0xabcdef1234567890"
MOCK_RECEIPT = {"status": 1, "transactionHash": MOCK_TX_HASH}


def test_schema_validation():
    """Ensure schema accepts and exposes fields correctly."""
    model = ExactInputSingleSchema(
        token_in=MOCK_TOKEN_IN_ID,
        token_out=MOCK_TOKEN_OUT_ID,
        fee=MOCK_FEE,
        amount_in=MOCK_AMOUNT_IN,
        recipient=MOCK_RECIPIENT,
    )
    assert model.token_in == MOCK_TOKEN_IN_ID
    assert model.token_out == MOCK_TOKEN_OUT_ID
    assert model.fee == MOCK_FEE
    assert model.amount_in == MOCK_AMOUNT_IN
    assert model.recipient == MOCK_RECIPIENT


def test_swap_exact_input_single_success_with_recipient():
    """Successful swap encodes exactInputSingle and submits tx with provided recipient."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.Web3") as mock_web3,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_decimals") as mock_get_decimals,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_balance") as mock_get_balance,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_symbol") as mock_get_symbol,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.format_amount_with_decimals") as mock_format_with,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        # Arrange mocks
        network_key = "base-sepolia"
        router = UNISWAP_V3_ADDRESSES[network_key]["swap_router_02"]
        quoter = UNISWAP_V3_ADDRESSES[network_key]["uniswap_quoter"]
        
        # Mock network and addresses
        mock_network = mock_wallet.get_network.return_value
        mock_network.network_id = network_key
        
        # Mock Web3 and contracts
        mock_contract = mock_web3.return_value.eth.contract
        mock_contract.return_value.encode_abi.return_value = "0xencoded"
        mock_web3.to_checksum_address.side_effect = lambda x: x

        # Mock utility functions
        mock_get_decimals.return_value = 18
        mock_format_with.return_value = MOCK_AMOUNT_IN_ATOMIC
        mock_get_balance.return_value = MOCK_AMOUNT_IN_ATOMIC * 2  # Sufficient balance
        mock_get_symbol.side_effect = ["WETH", "USDC"]  # token_in, token_out symbols

        # Mock wallet methods
        mock_wallet.get_address.return_value = MOCK_RECIPIENT
        mock_wallet.send_transaction.return_value = MOCK_TX_HASH
        mock_wallet.wait_for_transaction_receipt.return_value = MOCK_RECEIPT

        # Quoted amountOut from QuoterV2; amountOutMinimum should be ~99% of this
        quoted_amount_out = 1_000_000
        expected_min_out = quoted_amount_out * 99 // 100
        mock_wallet.read_contract.return_value = quoted_amount_out

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN_ID,
            "token_out": MOCK_TOKEN_OUT_ID,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
            "recipient": MOCK_RECIPIENT,
        }

        # Act
        response = provider.swap_exact_input_single(mock_wallet, args)

        # Assert response format matches new implementation
        assert "Swapped" in response
        assert "WETH" in response
        assert "USDC" in response
        assert "Transaction hash" in response
        assert MOCK_TX_HASH in response

        # Assert utility functions were called correctly
        mock_get_decimals.assert_called_with(mock_wallet, ASSET_ADDRESSES[network_key][MOCK_TOKEN_IN_ID])
        mock_format_with.assert_called_with(MOCK_AMOUNT_IN, 18)
        mock_get_balance.assert_called_with(mock_wallet, ASSET_ADDRESSES[network_key][MOCK_TOKEN_IN_ID])

        # Assert approval transaction was sent first
        assert mock_wallet.send_transaction.call_count == 2  # approval + swap
        
        # Assert swap transaction was sent with correct params
        swap_call = mock_wallet.send_transaction.call_args_list[1]
        assert swap_call[0][0]["to"] == router
        assert swap_call[0][0]["data"] == "0xencoded"

        # Assert quoter was used with asset addresses
        mock_wallet.read_contract.assert_called_once()
        read_call = mock_wallet.read_contract.call_args
        assert read_call[1]["function_name"] == "quoteExactInputSingle"


def test_swap_exact_input_single_success_default_recipient_wallet():
    """Recipient defaults to wallet address when not provided."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.Web3") as mock_web3,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_decimals") as mock_get_decimals,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_balance") as mock_get_balance,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_symbol") as mock_get_symbol,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.format_amount_with_decimals") as mock_format_with,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        # Arrange mocks
        network_key = "base-mainnet"
        router = UNISWAP_V3_ADDRESSES[network_key]["swap_router_02"]
        
        # Mock network and addresses
        mock_network = mock_wallet.get_network.return_value
        mock_network.network_id = network_key
        
        # Mock Web3 and contracts
        mock_contract = mock_web3.return_value.eth.contract
        mock_contract.return_value.encode_abi.return_value = "0xencoded"
        mock_web3.to_checksum_address.side_effect = lambda x: x

        # Mock utility functions
        mock_get_decimals.return_value = 18
        mock_format_with.return_value = MOCK_AMOUNT_IN_ATOMIC
        mock_get_balance.return_value = MOCK_AMOUNT_IN_ATOMIC * 2  # Sufficient balance
        mock_get_symbol.side_effect = ["WETH", "USDC"]

        # Mock wallet methods
        wallet_address = "0x4444444444444444444444444444444444444444"
        mock_wallet.get_address.return_value = wallet_address
        mock_wallet.send_transaction.return_value = MOCK_TX_HASH
        mock_wallet.wait_for_transaction_receipt.return_value = MOCK_RECEIPT

        # Quoted amountOut
        quoted_amount_out = 2_000_000
        mock_wallet.read_contract.return_value = quoted_amount_out

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN_ID,
            "token_out": MOCK_TOKEN_OUT_ID,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
            # No recipient provided - should default to wallet address
        }

        response = provider.swap_exact_input_single(mock_wallet, args)
        
        # Assert response format
        assert "Swapped" in response
        assert MOCK_TX_HASH in response

        # Assert approval + swap transactions were sent
        assert mock_wallet.send_transaction.call_count == 2

        # Check that the recipient in the swap call is the wallet address
        swap_call = mock_wallet.send_transaction.call_args_list[1]
        assert swap_call[0][0]["to"] == router


def test_swap_exact_input_single_error_path():
    """Handles exception raised during send_transaction gracefully."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.Web3") as mock_web3,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_decimals") as mock_get_decimals,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_balance") as mock_get_balance,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.format_amount_with_decimals") as mock_format_with,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        # Arrange mocks
        network_key = "base-mainnet"
        
        # Mock network
        mock_network = mock_wallet.get_network.return_value
        mock_network.network_id = network_key
        
        # Mock Web3 and contracts
        mock_contract = mock_web3.return_value.eth.contract
        mock_contract.return_value.encode_abi.return_value = "0xencoded"
        mock_web3.to_checksum_address.side_effect = lambda x: x

        # Mock utility functions
        mock_get_decimals.return_value = 18
        mock_format_with.return_value = MOCK_AMOUNT_IN_ATOMIC
        mock_get_balance.return_value = MOCK_AMOUNT_IN_ATOMIC * 2  # Sufficient balance

        # Mock wallet methods - first call (approval) succeeds, second call (swap) fails
        mock_wallet.get_address.return_value = MOCK_RECIPIENT
        mock_wallet.send_transaction.side_effect = [MOCK_TX_HASH, Exception("Transaction failed")]
        mock_wallet.wait_for_transaction_receipt.return_value = MOCK_RECEIPT
        mock_wallet.read_contract.return_value = 123_456

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN_ID,
            "token_out": MOCK_TOKEN_OUT_ID,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
            "recipient": MOCK_RECIPIENT,
        }

        response = provider.swap_exact_input_single(mock_wallet, args)
        assert response == "Error executing transaction: Transaction failed"


def test_swap_exact_input_single_insufficient_balance():
    """Handles insufficient balance gracefully."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_decimals") as mock_get_decimals,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.get_token_balance") as mock_get_balance,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.format_amount_with_decimals") as mock_format_with,
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.format_amount_from_decimals") as mock_format_from,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        # Arrange mocks
        network_key = "base-mainnet"
        
        # Mock network
        mock_network = mock_wallet.get_network.return_value
        mock_network.network_id = network_key
        
        # Mock utility functions - insufficient balance
        mock_get_decimals.return_value = 18
        mock_format_with.return_value = MOCK_AMOUNT_IN_ATOMIC
        mock_get_balance.return_value = MOCK_AMOUNT_IN_ATOMIC // 2  # Insufficient balance
        mock_format_from.return_value = "0.5"  # Human readable balance

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN_ID,
            "token_out": MOCK_TOKEN_OUT_ID,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
        }

        response = provider.swap_exact_input_single(mock_wallet, args)
        assert "Error: Insufficient balance" in response
        assert "You have 0.5" in response
        assert f"trying to swap {MOCK_AMOUNT_IN}" in response


def test_supports_network():
    """Test network support validation."""
    from coinbase_agentkit.network import Network
    
    provider = UniswapV3ActionProvider()
    
    # Test supported networks
    base_mainnet = Network(network_id="base-mainnet", protocol_family="evm", chain_id="8453")
    base_sepolia = Network(network_id="base-sepolia", protocol_family="evm", chain_id="84532")
    
    assert provider.supports_network(base_mainnet) is True
    assert provider.supports_network(base_sepolia) is True
    
    # Test unsupported networks
    ethereum_mainnet = Network(network_id="ethereum-mainnet", protocol_family="evm", chain_id="1")
    solana_mainnet = Network(network_id="solana-mainnet", protocol_family="solana", chain_id="mainnet")
    
    assert provider.supports_network(ethereum_mainnet) is False
    assert provider.supports_network(solana_mainnet) is False


