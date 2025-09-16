"""Tests for UniswapV3ActionProvider exact input swap."""

from unittest.mock import patch

import pytest

from coinbase_agentkit.action_providers.uniswap_v3.constants import (
    UNISWAP_SWAP_ROUTER_ABI,
    UNISWAP_V3_ADDRESSES,
)
from coinbase_agentkit.action_providers.uniswap_v3.schemas import ExactInputSingleSchema
from coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider import (
    UniswapV3ActionProvider,
)


MOCK_TOKEN_IN = "0x1111111111111111111111111111111111111111"
MOCK_TOKEN_OUT = "0x2222222222222222222222222222222222222222"
MOCK_RECIPIENT = "0x3333333333333333333333333333333333333333"
MOCK_AMOUNT_IN = 10**18
MOCK_FEE = 3000
MOCK_TX_HASH = "0xabcdef1234567890"
MOCK_RECEIPT = {"status": 1, "transactionHash": MOCK_TX_HASH}


def test_schema_validation():
    """Ensure schema accepts and exposes fields correctly."""
    model = ExactInputSingleSchema(
        token_in=MOCK_TOKEN_IN,
        token_out=MOCK_TOKEN_OUT,
        fee=MOCK_FEE,
        amount_in=MOCK_AMOUNT_IN,
        recipient=MOCK_RECIPIENT,
    )
    assert model.token_in == MOCK_TOKEN_IN
    assert model.token_out == MOCK_TOKEN_OUT
    assert model.fee == MOCK_FEE
    assert model.amount_in == MOCK_AMOUNT_IN
    assert model.recipient == MOCK_RECIPIENT


def test_swap_exact_input_single_success_with_recipient():
    """Successful swap encodes exactInputSingle and submits tx with provided recipient."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.Web3") as mock_web3,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        # Arrange mocks
        router = UNISWAP_V3_ADDRESSES["base-sepolia"]["swap_router_02"]
        mock_contract = mock_web3.return_value.eth.contract
        mock_contract.return_value.encode_abi.return_value = "0xencoded"
        mock_web3.to_checksum_address.side_effect = lambda x: x

        # Quoted amountOut from QuoterV2; amountOutMinimum should be ~99% of this
        quoted_amount_out = 1_000_000
        expected_min_out = quoted_amount_out * 99 // 100
        mock_wallet.read_contract.return_value = quoted_amount_out

        mock_wallet.get_address.return_value = MOCK_RECIPIENT
        mock_wallet.get_network.return_value.chain_id = "84532"  # not 8453, maps to base-sepolia
        mock_wallet.send_transaction.return_value = MOCK_TX_HASH
        mock_wallet.wait_for_transaction_receipt.return_value = MOCK_RECEIPT

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN,
            "token_out": MOCK_TOKEN_OUT,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
            "recipient": MOCK_RECIPIENT,
        }

        # Act
        response = provider.swap_exact_input_single(mock_wallet, args)

        # Assert response
        assert "Transaction hash" in response
        assert MOCK_TX_HASH in response

        # Assert contract build and encoding
        mock_contract.assert_called_once_with(address=router, abi=UNISWAP_SWAP_ROUTER_ABI)
        mock_contract.return_value.encode_abi.assert_called_once()
        method = mock_contract.return_value.encode_abi.call_args[0][0]
        kwargs = mock_contract.return_value.encode_abi.call_args[1]
        assert method == "exactInputSingle"
        assert "args" in kwargs and isinstance(kwargs["args"], list) and len(kwargs["args"]) == 1
        params = kwargs["args"][0]
        assert params["amountOutMinimum"] == expected_min_out

        # Assert transaction submission
        mock_wallet.send_transaction.assert_called_once_with({"to": router, "data": "0xencoded"})
        mock_wallet.wait_for_transaction_receipt.assert_called_once_with(MOCK_TX_HASH)

        # Assert quoter was used
        _, rc_kwargs = mock_wallet.read_contract.call_args
        assert rc_kwargs.get("function_name") == "quoteExactInputSingle"


def test_swap_exact_input_single_success_default_recipient_wallet():
    """Recipient defaults to wallet address when not provided."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.Web3") as mock_web3,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        router = UNISWAP_V3_ADDRESSES["base-mainnet"]["swap_router_02"]
        mock_contract = mock_web3.return_value.eth.contract
        mock_contract.return_value.encode_abi.return_value = "0xencoded"
        mock_web3.to_checksum_address.side_effect = lambda x: x

        quoted_amount_out = 2_000_000
        expected_min_out = quoted_amount_out * 99 // 100
        mock_wallet.read_contract.return_value = quoted_amount_out

        wallet_address = "0x4444444444444444444444444444444444444444"
        mock_wallet.get_address.return_value = wallet_address
        mock_wallet.get_network.return_value.chain_id = 8453  # maps to base-mainnet
        mock_wallet.send_transaction.return_value = MOCK_TX_HASH
        mock_wallet.wait_for_transaction_receipt.return_value = MOCK_RECEIPT

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN,
            "token_out": MOCK_TOKEN_OUT,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
        }

        response = provider.swap_exact_input_single(mock_wallet, args)
        assert MOCK_TX_HASH in response

        mock_contract.assert_called_once_with(address=router, abi=UNISWAP_SWAP_ROUTER_ABI)
        mock_wallet.send_transaction.assert_called_once_with({"to": router, "data": "0xencoded"})

        method = mock_contract.return_value.encode_abi.call_args[0][0]
        kwargs = mock_contract.return_value.encode_abi.call_args[1]
        assert method == "exactInputSingle"
        params = kwargs["args"][0]
        assert params["recipient"] == wallet_address
        assert params["amountOutMinimum"] == expected_min_out


def test_swap_exact_input_single_error_path():
    """Handles exception raised during send_transaction gracefully."""
    with (
        patch("coinbase_agentkit.action_providers.uniswap_v3.uniswap_v3_action_provider.Web3") as mock_web3,
        patch("coinbase_agentkit.wallet_providers.EvmWalletProvider") as mock_wallet,
    ):
        router = UNISWAP_V3_ADDRESSES["base-mainnet"]["swap_router_02"]
        mock_contract = mock_web3.return_value.eth.contract
        mock_contract.return_value.encode_abi.return_value = "0xencoded"
        mock_web3.to_checksum_address.side_effect = lambda x: x

        mock_wallet.read_contract.return_value = 123_456
        mock_wallet.get_address.return_value = MOCK_RECIPIENT
        mock_wallet.get_network.return_value.chain_id = 8453
        mock_wallet.send_transaction.side_effect = Exception("Transaction failed")

        provider = UniswapV3ActionProvider()
        args = {
            "token_in": MOCK_TOKEN_IN,
            "token_out": MOCK_TOKEN_OUT,
            "fee": MOCK_FEE,
            "amount_in": MOCK_AMOUNT_IN,
            "recipient": MOCK_RECIPIENT,
        }

        response = provider.swap_exact_input_single(mock_wallet, args)
        assert response == "Error performing exact input swap: Transaction failed"


