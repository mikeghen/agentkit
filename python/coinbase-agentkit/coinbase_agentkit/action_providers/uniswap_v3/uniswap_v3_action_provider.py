"""Uniswap v3 minimal action provider: exact input swap using SwapRouter."""

from typing import Any

from web3 import Web3

from ...network import Network
from ...wallet_providers import EvmWalletProvider
from ..action_decorator import create_action
from ..action_provider import ActionProvider
from ..erc20.constants import ERC20_ABI
from .constants import (
    ASSET_ADDRESSES,
    SUPPORTED_NETWORKS,
    UNISWAP_QUOTER_ABI,
    UNISWAP_SWAP_ROUTER_ABI,
    UNISWAP_V3_ADDRESSES,
)
from .schemas import ExactInputSingleSchema
from .utils import (
    format_amount_from_decimals,
    format_amount_with_decimals,
    get_token_balance,
    get_token_decimals,
    get_token_symbol,
)


class UniswapV3ActionProvider(ActionProvider[EvmWalletProvider]):
    """Minimal Uniswap v3 action provider supporting exactInputSingle swaps.

    Notes:
    - This provider intentionally sets amountOutMinimum to 0 to be used on private mempools only.
    - Caller must ensure prior ERC20 approval of the SwapRouter if tokenIn is not native.
    """

    def __init__(self) -> None:
        super().__init__("uniswap_v3", [])

    def _get_asset_address(self, network: Network, asset_id: str) -> str:
        """Get the asset address based on network and asset ID."""
        return ASSET_ADDRESSES[network.network_id][asset_id]

    @create_action(
        name="swap_exact_input_single",
        description="""
This tool allows swapping tokens on Uniswap v3.
It takes:
- token_in: The asset to swap from, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, or `usdc`
- token_out: The asset to swap to, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, or `usdc`
- fee: The pool fee tier (e.g., 3000 for 0.3%)
- amount_in: The amount of input tokens to swap in human-readable format
    Examples:
    - 1 WETH
    - 0.1 WETH
    - 1000 USDC
Important notes:
- Make sure to use the exact amount provided
- The tokens must be available on the network
""",
        schema=ExactInputSingleSchema,
    )
    def swap_exact_input_single(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Execute an exact input swap via Uniswap v3 SwapRouter."""
        try:
            validated_args = ExactInputSingleSchema(**args)
            network = wallet_provider.get_network()
            
            # Get token addresses from asset IDs
            # NOTE: Key errors should be handled here in case someone passes an invalid asset ID
            token_in_address = self._get_asset_address(network, validated_args.token_in)
            token_out_address = self._get_asset_address(network, validated_args.token_out)
            
            # Get token decimals and convert amount
            token_in_decimals = get_token_decimals(wallet_provider, token_in_address)
            amount_in_atomic = format_amount_with_decimals(validated_args.amount_in, token_in_decimals)

            # Check wallet balance before proceeding
            wallet_balance = get_token_balance(wallet_provider, token_in_address)
            if wallet_balance < amount_in_atomic:
                human_balance = format_amount_from_decimals(wallet_balance, token_in_decimals)
                return f"Error: Insufficient balance. You have {human_balance}, but trying to swap {validated_args.amount_in}"

            # Resolve router and quoter addresses from network
            network_key = network.network_id
            router = UNISWAP_V3_ADDRESSES[network_key]["swap_router_02"]
            quoter = UNISWAP_V3_ADDRESSES[network_key]["uniswap_quoter"]

            # Approve Uniswap router to spend tokens
            token_contract = Web3().eth.contract(address=token_in_address, abi=ERC20_ABI)
            encoded_data = token_contract.encode_abi("approve", args=[router, amount_in_atomic])
            params = {
                "to": token_in_address,
                "data": encoded_data,
            }
            try:
                approval_tx_hash = wallet_provider.send_transaction(params)
                approval_receipt = wallet_provider.wait_for_transaction_receipt(approval_tx_hash, poll_latency=2)
                print(f"Approval confirmed: {approval_tx_hash}")
            except Exception as e:
                return f"Error approving token: {e!s}"

            # Use QuoterV2 to fetch an estimated amountOut
            quoted_amount_out = wallet_provider.read_contract(
                contract_address=quoter,
                abi=UNISWAP_QUOTER_ABI,
                function_name="quoteExactInputSingle",
                args=[
                    {
                        "tokenIn": str(Web3.to_checksum_address(token_in_address)),
                        "tokenOut": str(Web3.to_checksum_address(token_out_address)),
                        "amountIn": int(amount_in_atomic),
                        "fee": int(validated_args.fee),
                        "sqrtPriceLimitX96": 0,
                    }
                ],
            )

            if isinstance(quoted_amount_out, (list, tuple)):
                quoted_amount_out = quoted_amount_out[0] if quoted_amount_out else 0
            try:
                quoted_amount_out_int = int(quoted_amount_out)
            except Exception:
                quoted_amount_out_int = 0

            # NOTE: Apply a 1% slippage tolerance.
            # NOTE: This could be something that we could make configurable.
            # for the purposes of this use case, all assets swapped should work with the 1% tolerance.
            amount_out_minimum = (quoted_amount_out_int * 99) // 100 if quoted_amount_out_int > 0 else 0

            # Execute the swap
            contract = Web3().eth.contract(address=router, abi=UNISWAP_SWAP_ROUTER_ABI)
            data = contract.encode_abi(
                "exactInputSingle",
                args=[
                    {
                        "tokenIn": Web3.to_checksum_address(token_in_address),
                        "tokenOut": Web3.to_checksum_address(token_out_address),
                        "fee": int(validated_args.fee),
                        # Only allow the wallet address to be the recipient
                        "recipient": wallet_provider.get_address(),
                        "amountIn": int(amount_in_atomic),
                        "amountOutMinimum": amount_out_minimum,
                        "sqrtPriceLimitX96": 0,
                    }
                ],
            )

            tx_params: dict[str, Any] = {
                "to": router,
                "data": data,
            }

            try:
                swap_tx_hash = wallet_provider.send_transaction(tx_params)
                swap_receipt = wallet_provider.wait_for_transaction_receipt(swap_tx_hash, poll_latency=2)
                print(f"Swap confirmed: {swap_tx_hash}")
            except Exception as e:
                return f"Error executing transaction: {e!s}"

            # Get token symbols for user-friendly output
            token_in_symbol = get_token_symbol(wallet_provider, token_in_address)
            token_out_symbol = get_token_symbol(wallet_provider, token_out_address)

            return (
                f"Swapped {validated_args.amount_in} {token_in_symbol} to {token_out_symbol} on Uniswap v3.\n"
                f"Transaction hash: {swap_tx_hash}"
            )
        except Exception as e:
            return f"Error performing swap: {e!s}"

    def supports_network(self, network: Network) -> bool:
        """Check if network is supported by Uniswap V3."""
        return network.protocol_family == "evm" and network.network_id in SUPPORTED_NETWORKS


def uniswap_v3_action_provider() -> UniswapV3ActionProvider:
    """Factory for UniswapV3ActionProvider."""
    return UniswapV3ActionProvider()


