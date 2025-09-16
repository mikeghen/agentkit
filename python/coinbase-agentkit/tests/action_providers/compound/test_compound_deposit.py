from decimal import Decimal
from unittest.mock import MagicMock, call, patch


def test_deposit_action_success_usdc(compound_wallet, compound_provider):
    """Test that the deposit action in CompoundActionProvider successfully deposits USDC tokens."""
    provider = compound_provider
    input_args = {
        "asset_id": "usdc",
        "amount": 1000.0,
    }

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_balance"
        ) as mock_get_token_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
    ):
        # Setup mocks for utility functions
        mock_get_token_decimals.return_value = 6  # USDC has 6 decimals
        atomic_amount = int(Decimal("1000.0") * Decimal(10**6))
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_token_balance.return_value = atomic_amount * 2  # Sufficient balance
        mock_get_token_symbol.return_value = "USDC"

        fake_comet_contract = MagicMock()
        fake_comet_contract.encode_abi.return_value = "encoded_supply_data"
        fake_token_contract = MagicMock()
        fake_token_contract.encode_abi.return_value = "encoded_approve_data"

        def get_contract(address, abi):
            if "0xb125E6687d4313864e53df431d5425969c15Eb2F" in address:  # USDC comet
                return fake_comet_contract
            return fake_token_contract

        fake_eth = MagicMock()
        fake_eth.contract.side_effect = get_contract
        mock_web3.return_value.eth = fake_eth

        # Act
        result = provider.deposit(compound_wallet, input_args)

        # Assert that the deposit action returned the expected success message
        assert "Deposited 1000.0 USDC to Compound for yield earning" in result
        assert "Transaction hash: 0xTxHash" in result
        assert "Asset deposited to USDC Comet contract" in result
        assert "0xb125E6687d4313864e53df431d5425969c15Eb2F" in result

        fake_token_contract.encode_abi.assert_called_once_with(
            "approve", args=["0xb125E6687d4313864e53df431d5425969c15Eb2F", atomic_amount]
        )
        fake_comet_contract.encode_abi.assert_called_once_with(
            "supply", args=["0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", atomic_amount]
        )

        assert compound_wallet.send_transaction.call_count == 2


def test_deposit_action_success_weth(compound_wallet, compound_provider):
    """Test that the deposit action in CompoundActionProvider successfully deposits WETH tokens."""
    provider = compound_provider
    input_args = {
        "asset_id": "weth",
        "amount": 1.0,
    }

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_balance"
        ) as mock_get_token_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
    ):
        # Setup mocks for utility functions
        mock_get_token_decimals.return_value = 18  # WETH has 18 decimals
        atomic_amount = int(Decimal("1.0") * Decimal(10**18))
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_token_balance.return_value = atomic_amount * 2  # Sufficient balance
        mock_get_token_symbol.return_value = "WETH"

        fake_comet_contract = MagicMock()
        fake_comet_contract.encode_abi.return_value = "encoded_supply_data"
        fake_token_contract = MagicMock()
        fake_token_contract.encode_abi.return_value = "encoded_approve_data"

        def get_contract(address, abi):
            if "0x46e6b214b524310239732D51387075E0e70970bf" in address:  # WETH comet
                return fake_comet_contract
            return fake_token_contract

        fake_eth = MagicMock()
        fake_eth.contract.side_effect = get_contract
        mock_web3.return_value.eth = fake_eth

        # Act
        result = provider.deposit(compound_wallet, input_args)

        # Assert that the deposit action returned the expected success message
        assert "Deposited 1.0 WETH to Compound for yield earning" in result
        assert "Transaction hash: 0xTxHash" in result
        assert "Asset deposited to WETH Comet contract" in result
        assert "0x46e6b214b524310239732D51387075E0e70970bf" in result

        fake_token_contract.encode_abi.assert_called_once_with(
            "approve", args=["0x46e6b214b524310239732D51387075E0e70970bf", atomic_amount]
        )
        fake_comet_contract.encode_abi.assert_called_once_with(
            "supply", args=["0x4200000000000000000000000000000000000006", atomic_amount]
        )

        assert compound_wallet.send_transaction.call_count == 2


def test_deposit_action_success_aero(compound_wallet, compound_provider):
    """Test that the deposit action in CompoundActionProvider successfully deposits AERO tokens."""
    provider = compound_provider
    input_args = {
        "asset_id": "aero",
        "amount": 100.5,
    }

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_symbol"
        ) as mock_get_token_symbol,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_balance"
        ) as mock_get_token_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
    ):
        # Setup mocks for utility functions
        mock_get_token_decimals.return_value = 18  # AERO has 18 decimals
        atomic_amount = int(Decimal("100.5") * Decimal(10**18))
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_token_balance.return_value = atomic_amount * 2  # Sufficient balance
        mock_get_token_symbol.return_value = "AERO"

        fake_comet_contract = MagicMock()
        fake_comet_contract.encode_abi.return_value = "encoded_supply_data"
        fake_token_contract = MagicMock()
        fake_token_contract.encode_abi.return_value = "encoded_approve_data"

        def get_contract(address, abi):
            if "0x784efeB622244d2348d4F2522f8860B96fbEcE89" in address:  # AERO comet
                return fake_comet_contract
            return fake_token_contract

        fake_eth = MagicMock()
        fake_eth.contract.side_effect = get_contract
        mock_web3.return_value.eth = fake_eth

        # Act
        result = provider.deposit(compound_wallet, input_args)

        # Assert that the deposit action returned the expected success message
        assert "Deposited 100.5 AERO to Compound for yield earning" in result
        assert "Transaction hash: 0xTxHash" in result
        assert "Asset deposited to AERO Comet contract" in result
        assert "0x784efeB622244d2348d4F2522f8860B96fbEcE89" in result

        fake_token_contract.encode_abi.assert_called_once_with(
            "approve", args=["0x784efeB622244d2348d4F2522f8860B96fbEcE89", atomic_amount]
        )
        fake_comet_contract.encode_abi.assert_called_once_with(
            "supply", args=["0x940181a94A35A4569E4529A3CDfB74e38FD98631", atomic_amount]
        )

        assert compound_wallet.send_transaction.call_count == 2


def test_deposit_insufficient_balance(compound_wallet, compound_provider):
    """Test deposit action when wallet has insufficient balance."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": 2000.0}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_balance"
        ) as mock_get_token_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_from_decimals"
        ) as mock_format_from_decimals,
    ):
        mock_get_token_decimals.return_value = 6
        deposit_amount = int(Decimal("2000.0") * Decimal(10**6))
        wallet_balance = int(Decimal("1000.0") * Decimal(10**6))
        mock_format_amount_with_decimals.return_value = deposit_amount
        mock_get_token_balance.return_value = wallet_balance
        mock_format_from_decimals.return_value = "1000"

        result = provider.deposit(compound_wallet, input_args)

        assert "Error: Insufficient balance" in result
        assert "You have 1000, but trying to deposit 2000" in result


def test_deposit_approval_failure(compound_wallet, compound_provider):
    """Test deposit action when token approval fails."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": 1000.0}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_balance"
        ) as mock_get_token_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        mock_get_token_decimals.return_value = 6
        atomic_amount = int(Decimal("1000.0") * Decimal(10**6))
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_token_balance.return_value = atomic_amount * 2

        fake_contract = MagicMock()
        fake_contract.encode_abi.return_value = "encoded_approve_data"
        fake_eth = MagicMock()
        fake_eth.contract.return_value = fake_contract
        mock_web3.return_value.eth = fake_eth

        compound_wallet.send_transaction.side_effect = Exception("Approval failed")
        result = provider.deposit(compound_wallet, input_args)

        assert "Error approving token: Approval failed" in result


def test_deposit_transaction_failure(compound_wallet, compound_provider):
    """Test deposit action when the deposit transaction fails."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": 1000.0}

    with (
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
        ) as mock_get_token_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.format_amount_with_decimals"
        ) as mock_format_amount_with_decimals,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_balance"
        ) as mock_get_token_balance,
        patch(
            "coinbase_agentkit.action_providers.compound.compound_action_provider.Web3"
        ) as mock_web3,
    ):
        mock_get_token_decimals.return_value = 6
        atomic_amount = int(Decimal("1000.0") * Decimal(10**6))
        mock_format_amount_with_decimals.return_value = atomic_amount
        mock_get_token_balance.return_value = atomic_amount * 2

        fake_comet_contract = MagicMock()
        fake_comet_contract.encode_abi.return_value = "encoded_supply_data"
        fake_token_contract = MagicMock()
        fake_token_contract.encode_abi.return_value = "encoded_approve_data"

        def get_contract(address, abi):
            if "0xb125E6687d4313864e53df431d5425969c15Eb2F" in address:
                return fake_comet_contract
            return fake_token_contract

        fake_eth = MagicMock()
        fake_eth.contract.side_effect = get_contract
        mock_web3.return_value.eth = fake_eth

        def mock_send_transaction(params):
            if params["data"] == "encoded_approve_data":
                return "0xApprovalHash"
            raise Exception("Deposit transaction failed")

        compound_wallet.send_transaction.side_effect = mock_send_transaction
        result = provider.deposit(compound_wallet, input_args)

        assert "Error executing transaction: Deposit transaction failed" in result


def test_deposit_general_error(compound_wallet, compound_provider):
    """Test deposit action when an unexpected error occurs."""
    provider = compound_provider
    input_args = {"asset_id": "usdc", "amount": 1000.0}

    with patch(
        "coinbase_agentkit.action_providers.compound.compound_action_provider.get_token_decimals"
    ) as mock_get_token_decimals:
        mock_get_token_decimals.side_effect = Exception("Unexpected error occurred")

        result = provider.deposit(compound_wallet, input_args)

        assert "Error depositing to Compound: Unexpected error occurred" in result
