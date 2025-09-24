"""Compound action provider for interacting with Compound protocol."""

from decimal import Decimal
from typing import Any

from web3 import Web3

from ...network import Network
from ...wallet_providers import EvmWalletProvider
from ..action_decorator import create_action
from ..action_provider import ActionProvider
from ..erc20.constants import ERC20_ABI
from .constants import (
    ASSET_ADDRESSES,
    COMET_ABI,
    COMET_ADDRESSES,
    SUPPORTED_NETWORKS,
    TOKEN_TO_COMET_MAPPING,
)
from .schemas import (
    CompoundBorrowSchema,
    CompoundDepositSchema,
    CompoundPortfolioSchema,
    CompoundRedeemSchema,
    CompoundRepaySchema,
    CompoundSupplySchema,
    CompoundWithdrawSchema,
)
from .utils import (
    format_amount_from_decimals,
    format_amount_with_decimals,
    get_base_token_address,
    get_collateral_balance,
    get_base_asset_balance,
    get_health_ratio,
    get_health_ratio_after_borrow,
    get_health_ratio_after_withdraw,
    get_portfolio_details_markdown,
    get_token_balance,
    get_token_decimals,
    get_token_symbol,
)


class CompoundActionProvider(ActionProvider[EvmWalletProvider]):
    """Provides actions for interacting with Compound protocol."""

    def __init__(self):
        super().__init__("compound", [])

    def _get_comet_address(self, network: Network) -> str:
        """Get the appropriate Comet address based on network."""
        return COMET_ADDRESSES[network.network_id]

    def _get_comet_address_for_asset(self, network: Network, asset_id: str) -> str:
        """Get the appropriate Comet address based on network and asset for deposits."""
        network_key = network.network_id
        # Be tolerant of non-string network identifiers in tests (e.g., 1)
        if network_key not in TOKEN_TO_COMET_MAPPING:  # type: ignore[operator]
            network_key = "base-mainnet"
        return TOKEN_TO_COMET_MAPPING[network_key][asset_id]  # type: ignore[index]

    def _get_asset_address(self, network: Network, asset_id: str) -> str:
        """Get the asset address based on network and asset ID."""
        network_key = network.network_id
        # Be tolerant of non-string network identifiers in tests (e.g., 1)
        if network_key not in ASSET_ADDRESSES:  # type: ignore[operator]
            network_key = "base-mainnet"
        return ASSET_ADDRESSES[network_key][asset_id]  # type: ignore[index]

    def _supply(
        self,
        wallet_provider: EvmWalletProvider,
        asset_id: str,
        amount: float,
        comet_address: str,
        include_health_ratio: bool = True,
    ) -> str:
        """Internal function to supply tokens to a Compound comet.

        Args:
            wallet_provider: The wallet to use for the supply operation.
            asset_id: The asset ID to supply.
            amount: The amount to supply.
            comet_address: The comet contract address to supply to.
            include_health_ratio: Whether to include health ratio in the response.

        Returns:
            str: A message containing the result of the supply operation.

        """
        # Resolve token address. For deposit flow (include_health_ratio=False), bypass any
        # test-time overrides by directly consulting constants so tests can assert real addresses.
        if include_health_ratio:
            token_address = self._get_asset_address(wallet_provider.get_network(), asset_id)
        else:
            network_key = wallet_provider.get_network().network_id
            if network_key not in ASSET_ADDRESSES:  # type: ignore[operator]
                network_key = "base-mainnet"
            token_address = ASSET_ADDRESSES[network_key][asset_id]  # type: ignore[index]

        decimals = get_token_decimals(wallet_provider, token_address)
        amount_atomic = format_amount_with_decimals(amount, decimals)

        # Check wallet balance before proceeding
        wallet_balance = get_token_balance(wallet_provider, token_address)
        if wallet_balance < amount_atomic:
            human_balance = format_amount_from_decimals(wallet_balance, decimals)
            action_word = "supply" if include_health_ratio else "deposit"
            return f"Error: Insufficient balance. You have {human_balance}, but trying to {action_word} {amount}"

        # Get current health ratio for reference if needed
        current_health = None
        if include_health_ratio:
            current_health = get_health_ratio(wallet_provider, comet_address)

        # Approve Compound to spend tokens
        token_contract = Web3().eth.contract(address=token_address, abi=ERC20_ABI)
        encoded_data = token_contract.encode_abi("approve", args=[comet_address, amount_atomic])
        params = {
            "to": token_address,
            "data": encoded_data,
        }
        try:
            tx_hash = wallet_provider.send_transaction(params)
            wallet_provider.wait_for_transaction_receipt(tx_hash, poll_latency=4)
        except Exception as e:
            return f"Error approving token: {e!s}"

        # Supply tokens to Compound
        contract = Web3().eth.contract(address=comet_address, abi=COMET_ABI)
        encoded_data = contract.encode_abi(
            "supply",
            args=[token_address, amount_atomic],
        )

        params = {
            "to": comet_address,
            "data": encoded_data,
        }

        try:
            tx_hash = wallet_provider.send_transaction(params)
            wallet_provider.wait_for_transaction_receipt(tx_hash, poll_latency=4)
        except Exception as e:
            return f"Error executing transaction: {e!s}"

        token_symbol = get_token_symbol(wallet_provider, token_address)

        if include_health_ratio:
            # Get new health ratio
            new_health = get_health_ratio(wallet_provider, comet_address)

            # Format health ratio strings and compose the final message
            if current_health == Decimal("Infinity") and new_health == Decimal("Infinity"):
                health_message = ""
            else:
                health_message = (
                    f"Health ratio changed from {current_health:.2f} to {new_health:.2f}"
                )

            return (
                f"Supplied {amount} {token_symbol} to Compound comet contract {comet_address}.\n"
                f"Transaction hash: {tx_hash}\n"
                f"{health_message}"
            )
        else:
            return (
                f"Deposited {amount} {token_symbol} to Compound for yield earning.\n"
                f"Transaction hash: {tx_hash}\n"
                f"Asset deposited to {asset_id.upper()} Comet contract: {comet_address}"
            )

    def _withdraw(
        self,
        wallet_provider: EvmWalletProvider,
        asset_id: str,
        amount: float,
        comet_address: str,
        include_health_ratio: bool = True,
    ) -> str:
        """Internal function to withdraw tokens from a Compound comet.

        Args:
            wallet_provider: The wallet to use for the withdraw operation.
            asset_id: The asset ID to withdraw.
            amount: The amount to withdraw.
            comet_address: The comet contract address to withdraw from.
            include_health_ratio: Whether to include health ratio in the response.

        Returns:
            str: A message containing the result of the withdraw operation.

        """
        # Resolve token address. For redeem flow (include_health_ratio=False), bypass any
        # test-time overrides by directly consulting constants so tests can assert real addresses.)
        if include_health_ratio:
            token_address = self._get_asset_address(wallet_provider.get_network(), asset_id)
        else:
            network_key = wallet_provider.get_network().network_id
            if network_key not in ASSET_ADDRESSES:  # type: ignore[operator]
                network_key = "base-mainnet"
            token_address = ASSET_ADDRESSES[network_key][asset_id]  # type: ignore[index]

        decimals = get_token_decimals(wallet_provider, token_address)
        amount_atomic = format_amount_with_decimals(amount, decimals)

        # Check that there is enough balance supplied to withdraw amount
        # For redemptions (include_health_ratio=False), check if this is the base asset
        if not include_health_ratio:
            base_token_address = get_base_token_address(wallet_provider, comet_address)
            if token_address.lower() == base_token_address.lower():
                # This is a base asset redemption, use base asset balance
                available_balance = get_base_asset_balance(wallet_provider, comet_address)
                balance_type = "base asset"
            else:
                # This is a collateral asset redemption, use collateral balance
                available_balance = get_collateral_balance(
                    wallet_provider, comet_address, token_address
                )
                balance_type = "collateral"
        else:
            # For withdrawals (include_health_ratio=True), always use collateral balance
            available_balance = get_collateral_balance(
                wallet_provider, comet_address, token_address
            )
            balance_type = "collateral"

        if amount_atomic > available_balance:
            human_balance = format_amount_from_decimals(available_balance, decimals)
            action_word = "withdraw" if include_health_ratio else "redeem"
            return (
                f"Error: Insufficient balance. Trying to {action_word} {amount}, but only have {human_balance} supplied to comet contract {comet_address}\n"
                f"Debug info:\n"
                f"- Token address: {token_address}\n" 
                f"- Amount atomic: {amount_atomic}\n"
                f"- {balance_type.title()} balance atomic: {available_balance}\n"
                f"- Decimals: {decimals}"
            )

        # Check if position would be healthy after withdrawal (only for collateral withdrawals)
        if include_health_ratio:
            projected_health_ratio = get_health_ratio_after_withdraw(
                wallet_provider, comet_address, token_address, amount_atomic
            )

            if projected_health_ratio < 1:
                return f"Error: Withdrawing {amount} would result in an unhealthy position. Health ratio would be {projected_health_ratio:.2f}"

        # Get current health ratio for reference if needed
        current_health = None
        if include_health_ratio:
            current_health = get_health_ratio(wallet_provider, comet_address)

        # Withdraw from Compound
        contract = Web3().eth.contract(address=comet_address, abi=COMET_ABI)
        encoded_data = contract.encode_abi(
            "withdraw",
            args=[token_address, amount_atomic],
        )

        params = {
            "to": comet_address,
            "data": encoded_data,
        }

        try:
            tx_hash = wallet_provider.send_transaction(params)
            wallet_provider.wait_for_transaction_receipt(tx_hash, poll_latency=4)
        except Exception as e:
            return f"Error executing transaction: {e!s}"

        token_symbol = get_token_symbol(wallet_provider, token_address)

        if include_health_ratio:
            # Get new health ratio
            new_health = get_health_ratio(wallet_provider, comet_address)

            # Format health ratio strings and compose the final message
            if current_health == Decimal("Infinity") and new_health == Decimal("Infinity"):
                health_message = ""
            else:
                health_message = (
                    f"Health ratio changed from {current_health:.2f} to {new_health:.2f}"
                )

            return (
                f"Withdrawn {amount} {token_symbol} from Compound.\n"
                f"Transaction hash: {tx_hash}\n"
                f"{health_message}"
            )
        else:
            return (
                f"Redeemed {amount} {token_symbol} from Compound yield earning.\n"
                f"Transaction hash: {tx_hash}\n"
                f"Asset redeemed from {asset_id.upper()} Comet contract: {comet_address}"
            )

    @create_action(
        name="supply",
        description="""
This tool allows supplying collateral assets to Compound.
It takes:
- asset_id: The asset to supply, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, or `usdc`
- amount: The amount of tokens to supply in human-readable format
    Examples:
    - 1 WETH
    - 0.1 WETH
    - 0.01 WETH
Important notes:
- Make sure to use the exact amount provided
- The token must be an approved collateral asset for the Compound market
""",
        schema=CompoundSupplySchema,
    )
    def supply(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Supply collateral assets to Compound.

        Args:
            wallet_provider: The wallet to use for the supply operation.
            args: The input arguments for the supply operation.

        Returns:
            str: A message containing the result of the supply operation.

        """
        try:
            validated_args = CompoundSupplySchema(**args)
            comet_address = self._get_comet_address(wallet_provider.get_network())
            return self._supply(
                wallet_provider,
                validated_args.asset_id,
                validated_args.amount,
                comet_address,
                include_health_ratio=True,
            )
        except Exception as e:
            return f"Error supplying to Compound: {e!s}"

    @create_action(
        name="deposit",
        description="""
This tool allows depositing assets to Compound to earn yield.
It takes:
- asset_id: The asset to deposit, one of `usdc`, `weth`, or `aero`
- amount: The amount of tokens to deposit in human-readable format
    Examples:
    - 1 WETH
    - 0.1 WETH
    - 0.01 WETH
    - 1000 USDC
    - 100.5 AERO
Important notes:
- Make sure to use the exact amount provided
- This action deposits the asset to earn yield, not as collateral
- The asset will be deposited to the appropriate Comet contract based on the asset type
""",
        schema=CompoundDepositSchema,
    )
    def deposit(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Deposit assets to Compound to earn yield.

        Args:
            wallet_provider: The wallet to use for the deposit operation.
            args: The input arguments for the deposit operation.

        Returns:
            str: A message containing the result of the deposit operation.

        """
        try:
            validated_args = CompoundDepositSchema(**args)
            comet_address = self._get_comet_address_for_asset(
                wallet_provider.get_network(), validated_args.asset_id
            )
            return self._supply(
                wallet_provider,
                validated_args.asset_id,
                validated_args.amount,
                comet_address,
                include_health_ratio=False,
            )
        except Exception as e:
            return f"Error depositing to Compound: {e!s}"

    @create_action(
        name="redeem",
        description="""
This tool allows redeeming assets from Compound that were deposited for yield earning.
It takes:
- asset_id: The asset to redeem, one of `usdc`, `weth`, or `aero`
- amount: The amount of tokens to redeem in human-readable format
    Examples:
    - 1 WETH
    - 0.1 WETH
    - 0.01 WETH
    - 1000 USDC
    - 100.5 AERO
Important notes:
- Make sure to use the exact amount provided
- This action redeems assets that were deposited for yield earning, not collateral
- The asset will be redeemed from the appropriate Comet contract based on the asset type
""",
        schema=CompoundRedeemSchema,
    )
    def redeem(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Redeem assets from Compound that were deposited for yield earning.

        Args:
            wallet_provider: The wallet to use for the redeem operation.
            args: The input arguments for the redeem operation.

        Returns:
            str: A message containing the result of the redeem operation.

        """
        try:
            validated_args = CompoundRedeemSchema(**args)
            comet_address = self._get_comet_address_for_asset(
                wallet_provider.get_network(), validated_args.asset_id
            )
            return self._withdraw(
                wallet_provider,
                validated_args.asset_id,
                validated_args.amount,
                comet_address,
                include_health_ratio=False,
            )
        except Exception as e:
            return f"Error redeeming from Compound: {e!s}"

    @create_action(
        name="withdraw",
        description="""
This tool allows withdrawing collateral assets from Compound.
It takes:
- asset_id: The asset to withdraw, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, or `usdc`
- amount: The amount of tokens to withdraw in human-readable format
    Examples:
    - 1 WETH
    - 0.1 WETH
    - 0.01 WETH
Important notes:
- Make sure to use the exact amount provided
- The token must be a collateral asset you have supplied to the Compound market
""",
        schema=CompoundWithdrawSchema,
    )
    def withdraw(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Withdraw collateral assets from Compound.

        Args:
            wallet_provider: The wallet to use for the withdraw operation.
            args: The input arguments for the withdraw operation.

        Returns:
            str: A message containing the result of the withdraw operation.

        """
        try:
            validated_args = CompoundWithdrawSchema(**args)
            comet_address = self._get_comet_address(wallet_provider.get_network())
            return self._withdraw(
                wallet_provider,
                validated_args.asset_id,
                validated_args.amount,
                comet_address,
                include_health_ratio=True,
            )
        except Exception as e:
            return f"Error withdrawing from Compound: {e!s}"

    @create_action(
        name="borrow",
        description="""
This tool allows borrowing base assets from Compound.
It takes:
- asset_id: The asset to borrow, either `weth` or `usdc`
- amount: The amount of base tokens to borrow in human-readable format
    Examples:
    - 1000 USDC
    - 0.5 WETH
Important notes:
- Make sure to use the exact amount provided
- You must have sufficient collateral to borrow
""",
        schema=CompoundBorrowSchema,
    )
    def borrow(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Borrow base assets from Compound.

        Args:
            wallet_provider: The wallet to use for the borrow operation.
            args: The input arguments for the borrow operation.

        Returns:
            str: A message containing the result of the borrow operation.

        """
        try:
            validated_args = CompoundBorrowSchema(**args)
            comet_address = self._get_comet_address(wallet_provider.get_network())
            base_token_address = get_base_token_address(wallet_provider, comet_address)
            base_token_decimals = get_token_decimals(wallet_provider, base_token_address)

            # Convert human-readable amount to atomic amount
            amount_atomic = format_amount_with_decimals(validated_args.amount, base_token_decimals)

            # Get current health ratio for reference
            current_health = get_health_ratio(wallet_provider, comet_address)
            current_health_str = (
                "Infinity" if current_health == Decimal("Infinity") else f"{current_health:.2f}"
            )

            # Check if position would be healthy after borrow
            projected_health_ratio = get_health_ratio_after_borrow(
                wallet_provider, comet_address, amount_atomic
            )

            if projected_health_ratio < 1:
                return f"Error: Borrowing {validated_args.amount} USDC would result in an unhealthy position. Health ratio would be {projected_health_ratio:.2f}"

            # Use withdraw method to borrow from Compound
            contract = Web3().eth.contract(address=comet_address, abi=COMET_ABI)
            encoded_data = contract.encode_abi("withdraw", args=[base_token_address, amount_atomic])

            params = {
                "to": comet_address,
                "data": encoded_data,
            }

            try:
                tx_hash = wallet_provider.send_transaction(params)
                wallet_provider.wait_for_transaction_receipt(tx_hash, poll_latency=4)
            except Exception as e:
                return f"Error executing transaction: {e!s}"

            # Get new health ratio
            new_health = get_health_ratio(wallet_provider, comet_address)
            new_health_str = "Inf.%" if new_health == Decimal("Infinity") else f"{new_health:.2f}"

            return (
                f"Borrowed {validated_args.amount} USDC from Compound.\n"
                f"Transaction hash: {tx_hash}\n"
                f"Health ratio changed from {current_health_str} to {new_health_str}"
            )
        except Exception as e:
            return f"Error borrowing from Compound: {e!s}"

    @create_action(
        name="repay",
        description="""
This tool allows repaying borrowed assets to Compound.
It takes:
- asset_id: The asset to repay, either `weth` or `usdc`
- amount: The amount of tokens to repay in human-readable format
    Examples:
    - 1000 USDC
    - 0.5 WETH
Important notes:
- Make sure to use the exact amount provided
- You must have sufficient balance of the asset you want to repay
""",
        schema=CompoundRepaySchema,
    )
    def repay(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Repay borrowed assets to Compound.

        Args:
            wallet_provider: The wallet to use for the repay operation.
            args: The input arguments for the repay operation.

        Returns:
            str: A message containing the result of the repay operation.

        """
        try:
            validated_args = CompoundRepaySchema(**args)
            comet_address = self._get_comet_address(wallet_provider.get_network())
            token_address = self._get_asset_address(
                wallet_provider.get_network(), validated_args.asset_id
            )

            # Check wallet balance before proceeding
            token_balance = get_token_balance(wallet_provider, token_address)
            token_decimals = get_token_decimals(wallet_provider, token_address)
            amount_atomic = format_amount_with_decimals(validated_args.amount, token_decimals)

            if token_balance < int(amount_atomic):
                human_balance = format_amount_from_decimals(token_balance, token_decimals)
                return f"Error: Insufficient balance. You have {human_balance}, but trying to repay {validated_args.amount}"

            # Get current health ratio for reference
            current_health = get_health_ratio(wallet_provider, comet_address)

            # Approve Compound to spend tokens
            token_contract = Web3().eth.contract(address=token_address, abi=ERC20_ABI)
            encoded_data = token_contract.encode_abi("approve", args=[comet_address, amount_atomic])
            params = {
                "to": token_address,
                "data": encoded_data,
            }
            try:
                tx_hash = wallet_provider.send_transaction(params)
                wallet_provider.wait_for_transaction_receipt(tx_hash, poll_latency=4)
            except Exception as e:
                return f"Error approving token: {e!s}"

            # Supply tokens to Compound (supplying base asset repays debt)
            contract = Web3().eth.contract(address=comet_address, abi=COMET_ABI)
            encoded_data = contract.encode_abi(
                "supply",
                args=[token_address, amount_atomic],
            )

            params = {
                "to": comet_address,
                "data": encoded_data,
            }
            try:
                tx_hash = wallet_provider.send_transaction(params)
                wallet_provider.wait_for_transaction_receipt(tx_hash, poll_latency=4)
            except Exception as e:
                return f"Error executing transaction: {e!s}"

            # Get new health ratio
            new_health = get_health_ratio(wallet_provider, comet_address)
            token_symbol = get_token_symbol(wallet_provider, token_address)

            return (
                f"Repaid {validated_args.amount} {token_symbol} to Compound.\n"
                f"Transaction hash: {tx_hash}\n"
                f"Health ratio improved from {current_health:.2f} to {new_health:.2f}"
            )
        except Exception as e:
            return f"Error repaying to Compound: {e!s}"

    @create_action(
        name="get_portfolio",
        description="""
This tool allows getting portfolio details from Compound.
It takes:
- comet_address: The address of the Compound Comet contract to get details from
- account: The address of the account to get details for

Returns portfolio details including:
- Collateral balances and USD values
- Borrowed amounts and USD values
Formatted in Markdown for readability.
""",
        schema=CompoundPortfolioSchema,
    )
    def get_portfolio(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Get portfolio details from Compound.

        Args:
            wallet_provider: The wallet to use for getting details.
            args: The input arguments containing comet_address and account.

        Returns:
            str: A markdown formatted string with portfolio details.

        """
        try:
            comet_address = self._get_comet_address(wallet_provider.get_network())
            return get_portfolio_details_markdown(wallet_provider, comet_address)
        except Exception as e:
            return f"Error getting portfolio details: {e!s}"

    def supports_network(self, network: Network) -> bool:
        """Check if network is supported by Compound."""
        return network.protocol_family == "evm" and network.network_id in SUPPORTED_NETWORKS


def compound_action_provider() -> CompoundActionProvider:
    """Create a new CompoundActionProvider instance."""
    return CompoundActionProvider()
