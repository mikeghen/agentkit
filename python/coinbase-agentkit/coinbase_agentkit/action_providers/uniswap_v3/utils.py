"""Utility functions for Uniswap V3 action provider."""

from decimal import Decimal

from ...wallet_providers import EvmWalletProvider
from ..erc20.constants import ERC20_ABI


def get_token_decimals(wallet: EvmWalletProvider, token_address: str) -> int:
    """Get the number of decimals for a token using wallet.read_contract.

    Args:
        wallet: The wallet provider for reading from contracts.
        token_address: The address of the token.

    Returns:
        int: The number of decimals for the token.

    """
    result = wallet.read_contract(token_address, ERC20_ABI, "decimals")
    return result


def get_token_symbol(wallet: EvmWalletProvider, token_address: str) -> str:
    """Get a token's symbol from its contract using wallet.read_contract.

    Args:
        wallet: The wallet provider for reading from contracts.
        token_address: The address of the token contract.

    Returns:
        str: The token symbol.

    """
    return wallet.read_contract(token_address, ERC20_ABI, "symbol")


def get_token_balance(wallet: EvmWalletProvider, token_address: str) -> int:
    """Get the balance of a token for an account using wallet.read_contract.

    Args:
        wallet: The wallet provider for reading from contracts.
        token_address: The address of the token.

    Returns:
        int: The balance in atomic units.

    """
    return wallet.read_contract(
        token_address, ERC20_ABI, "balanceOf", args=[wallet.get_address()]
    )


def format_amount_with_decimals(amount: str, decimals: int) -> int:
    """Format a human-readable amount with the correct number of decimals.

    Args:
        amount: The amount as a string (e.g. "0.1").
        decimals: The number of decimals for the token.

    Returns:
        int: The amount in atomic units.

    """
    return int(Decimal(amount) * (Decimal(10) ** decimals))


def format_amount_from_decimals(amount: int, decimals: int) -> str:
    """Format an atomic amount to a human-readable string.

    Args:
        amount: The amount in atomic units.
        decimals: The number of decimals for the token.

    Returns:
        str: The amount as a human-readable string.

    """
    return str(Decimal(amount) / (Decimal(10) ** decimals))
