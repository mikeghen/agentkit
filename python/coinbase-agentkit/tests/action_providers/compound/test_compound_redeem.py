from unittest.mock import MagicMock, patch


def test_redeem_action_success_usdc(compound_wallet, compound_provider):
    """Test that the redeem action in CompoundActionProvider successfully redeems USDC tokens."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": "1000"}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_collateral_balance"
        ) as mock_get_collateral_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_from_decimals"
        ) as mock_format_amount_from_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        token_decimals = 6
        atomic_amount = 1000000000
        mock_get_token_decimals.return_value = token_decimals
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_collateral_balance.return_value = atomic_amount
        mock_format_amount_from_decimals.return_value = "1000"
        mock_get_token_symbol.return_value = "USDC"

        fake_contract = MagicMock()
        fake_contract.encode_abi.return_value = "encoded_withdraw_data"
        fake_eth = MagicMock()
        fake_eth.contract.return_value = fake_contract
        mock_web3.return_value.eth = fake_eth

        result = provider.redeem(compound_wallet, input_args)

        assert "Redeemed 1000.0 USDC from Compound yield earning" in result
        assert "Transaction hash: 0xTxHash" in result
        assert "Asset redeemed from USDC Comet contract" in result
        assert "0xb125E6687d4313864e53df431d5425969c15Eb2F" in result  # USDC comet address

        fake_contract.encode_abi.assert_called_once_with(
            "withdraw", args=["0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", atomic_amount]
        )

        compound_wallet.send_transaction.assert_called_once_with(
            {"to": "0xb125E6687d4313864e53df431d5425969c15Eb2F", "data": "encoded_withdraw_data"}
        )


def test_redeem_action_success_weth(compound_wallet, compound_provider):
    """Test that the redeem action in CompoundActionProvider successfully redeems WETH tokens."""
    provider = compound_provider
    input_args = {"asset_id": "weth", "amount": "1.5"}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_collateral_balance"
        ) as mock_get_collateral_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_from_decimals"
        ) as mock_format_amount_from_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        token_decimals = 18
        atomic_amount = 1500000000000000000  # 1.5 WETH in wei
        mock_get_token_decimals.return_value = token_decimals
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_collateral_balance.return_value = atomic_amount
        mock_format_amount_from_decimals.return_value = "1.5"
        mock_get_token_symbol.return_value = "WETH"

        fake_contract = MagicMock()
        fake_contract.encode_abi.return_value = "encoded_withdraw_data"
        fake_eth = MagicMock()
        fake_eth.contract.return_value = fake_contract
        mock_web3.return_value.eth = fake_eth

        result = provider.redeem(compound_wallet, input_args)

        assert "Redeemed 1.5 WETH from Compound yield earning" in result
        assert "Transaction hash: 0xTxHash" in result
        assert "Asset redeemed from WETH Comet contract" in result
        assert "0x46e6b214b524310239732D51387075E0e70970bf" in result  # WETH comet address

        fake_contract.encode_abi.assert_called_once_with(
            "withdraw", args=["0x4200000000000000000000000000000000000006", atomic_amount]
        )

        compound_wallet.send_transaction.assert_called_once_with(
            {"to": "0x46e6b214b524310239732D51387075E0e70970bf", "data": "encoded_withdraw_data"}
        )


def test_redeem_action_success_aero(compound_wallet, compound_provider):
    """Test that the redeem action in CompoundActionProvider successfully redeems AERO tokens."""
    provider = compound_provider
    input_args = {"asset_id": "aero", "amount": "100.5"}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_collateral_balance"
        ) as mock_get_collateral_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_from_decimals"
        ) as mock_format_amount_from_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        token_decimals = 18
        atomic_amount = 100500000000000000000  # 100.5 AERO in wei
        mock_get_token_decimals.return_value = token_decimals
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_collateral_balance.return_value = atomic_amount
        mock_format_amount_from_decimals.return_value = "100.5"
        mock_get_token_symbol.return_value = "AERO"

        fake_contract = MagicMock()
        fake_contract.encode_abi.return_value = "encoded_withdraw_data"
        fake_eth = MagicMock()
        fake_eth.contract.return_value = fake_contract
        mock_web3.return_value.eth = fake_eth

        result = provider.redeem(compound_wallet, input_args)

        assert "Redeemed 100.5 AERO from Compound yield earning" in result
        assert "Transaction hash: 0xTxHash" in result
        assert "Asset redeemed from AERO Comet contract" in result
        assert "0x784efeB622244d2348d4F2522f8860B96fbEcE89" in result  # AERO comet address

        fake_contract.encode_abi.assert_called_once_with(
            "withdraw", args=["0x940181a94A35A4569E4529A3CDfB74e38FD98631", atomic_amount]
        )

        compound_wallet.send_transaction.assert_called_once_with(
            {"to": "0x784efeB622244d2348d4F2522f8860B96fbEcE89", "data": "encoded_withdraw_data"}
        )


def test_redeem_insufficient_balance(compound_wallet, compound_provider):
    """Test redeem action when there is insufficient balance to redeem."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": "1000"}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_collateral_balance"
        ) as mock_get_collateral_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_from_decimals"
        ) as mock_format_amount_from_decimals,
    ):
        token_decimals = 6
        redeem_amount = 1000000000  # 1000 USDC
        balance = 500000000  # Only 500 USDC available

        mock_get_token_decimals.return_value = token_decimals
        mock_format_amount_with_decimals.return_value = redeem_amount
        mock_get_collateral_balance.return_value = balance
        mock_format_amount_from_decimals.return_value = "500.0"

        result = provider.redeem(compound_wallet, input_args)

        assert "Error: Insufficient balance" in result
        assert "Trying to redeem 1000.0, but only have 500.0 supplied" in result


def test_redeem_transaction_failure(compound_wallet, compound_provider):
    """Test redeem action when the transaction fails."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": "1000"}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_collateral_balance"
        ) as mock_get_collateral_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        token_decimals = 6
        atomic_amount = 1000000000
        mock_get_token_decimals.return_value = token_decimals
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_collateral_balance.return_value = atomic_amount * 2

        fake_contract = MagicMock()
        fake_contract.encode_abi.return_value = "encoded_withdraw_data"
        fake_eth = MagicMock()
        fake_eth.contract.return_value = fake_contract
        mock_web3.return_value.eth = fake_eth

        compound_wallet.send_transaction.side_effect = Exception("Transaction failed")
        result = provider.redeem(compound_wallet, input_args)

        assert "Error executing transaction: Transaction failed" in result


def test_redeem_general_error(compound_wallet, compound_provider):
    """Test redeem action when an unexpected error occurs."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": "1000"}

    with patch(
        "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
    ) as mock_get_token_decimals:
        mock_get_token_decimals.side_effect = Exception("Unexpected error occurred")

        result = provider.redeem(compound_wallet, input_args)

        assert "Error redeeming from Compound: Unexpected error occurred" in result


def test_redeem_no_health_ratio_checks(compound_wallet, compound_provider):
    """Test that redeem action does not perform health ratio checks unlike withdraw."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": "1000"}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_collateral_balance"
        ) as mock_get_collateral_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_health_ratio_after_withdraw"
        ) as mock_get_health_ratio_after_withdraw,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_health_ratio"
        ) as mock_get_health_ratio,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        token_decimals = 6
        atomic_amount = 1000000000
        mock_get_token_decimals.return_value = token_decimals
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_collateral_balance.return_value = atomic_amount
        mock_get_token_symbol.return_value = "USDC"

        fake_contract = MagicMock()
        fake_contract.encode_abi.return_value = "encoded_withdraw_data"
        fake_eth = MagicMock()
        fake_eth.contract.return_value = fake_contract
        mock_web3.return_value.eth = fake_eth

        result = provider.redeem(compound_wallet, input_args)

        # Verify that health ratio functions are NOT called for redeem
        mock_get_health_ratio_after_withdraw.assert_not_called()
        mock_get_health_ratio.assert_not_called()

        assert "Redeemed 1000.0 USDC from Compound yield earning" in result
