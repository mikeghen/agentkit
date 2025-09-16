"""Uniswap v3 minimal action provider: exact input swap using SwapRouter."""

from typing import Any

from web3 import Web3

from ...network import Network
from ...wallet_providers import EvmWalletProvider
from ..action_decorator import create_action
from ..action_provider import ActionProvider
from .constants import UNISWAP_QUOTER_ABI, UNISWAP_SWAP_ROUTER_ABI, UNISWAP_V3_ADDRESSES
from .schemas import ExactInputSingleSchema


class UniswapV3ActionProvider(ActionProvider[EvmWalletProvider]):
    """Minimal Uniswap v3 action provider supporting exactInputSingle swaps.

    Notes:
    - This provider intentionally sets amountOutMinimum to 0 to be used on private mempools only.
    - Caller must ensure prior ERC20 approval of the SwapRouter if tokenIn is not native.
    """

    def __init__(self) -> None:
        super().__init__("uniswap_v3", [])

    @create_action(
        name="swap_exact_input_single",
        description=(
            "Perform an exact input swap on Uniswap v3 using SwapRouter.exactInputSingle.\n"
            "Inputs: token_in, token_out, fee, amount_in, recipient (optional).\n"
            "Uses QuoterV2 to estimate output and sets amountOutMinimum to ~99% of quote."
        ),
        schema=ExactInputSingleSchema,
    )
    def swap_exact_input_single(self, wallet_provider: EvmWalletProvider, args: dict[str, Any]) -> str:
        """Execute an exact input swap via Uniswap v3 SwapRouter."""
        try:
            validated = ExactInputSingleSchema(**args)

            # Resolve router and quoter addresses from local Uniswap v3 addresses mapping by network
            chain_id = wallet_provider.get_network().chain_id
            try:
                numeric_chain_id = int(chain_id)  # handle both str and int inputs
            except Exception:
                numeric_chain_id = -1
            network_key = "base-mainnet" if numeric_chain_id == 8453 else "base-sepolia"
            router = UNISWAP_V3_ADDRESSES[network_key]["swap_router_02"]
            quoter = UNISWAP_V3_ADDRESSES[network_key]["uniswap_quoter"]

            recipient = (
                Web3.to_checksum_address(validated.recipient)
                if validated.recipient
                else wallet_provider.get_address()
            )

            # Use QuoterV2 to fetch an estimated amountOut
            quoted_amount_out = wallet_provider.read_contract(
                contract_address=quoter,
                abi=UNISWAP_QUOTER_ABI,
                function_name="quoteExactInputSingle",
                args=[
                    {
                        "tokenIn": str(Web3.to_checksum_address(validated.token_in)),
                        "tokenOut": str(Web3.to_checksum_address(validated.token_out)),
                        "amountIn": int(validated.amount_in),
                        "fee": int(validated.fee),
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

            # Apply a conservative 1% buffer similar to WOW provider usage
            amount_out_minimum = (quoted_amount_out_int * 99) // 100 if quoted_amount_out_int > 0 else 0

            # Encode call to exactInputSingle with computed amountOutMinimum and sqrtPriceLimitX96 = 0
            contract = Web3().eth.contract(address=router, abi=UNISWAP_SWAP_ROUTER_ABI)

            data = contract.encode_abi(
                "exactInputSingle",
                args=[
                    {
                        "tokenIn": Web3.to_checksum_address(validated.token_in),
                        "tokenOut": Web3.to_checksum_address(validated.token_out),
                        "fee": int(validated.fee),
                        "recipient": recipient,
                        "amountIn": int(validated.amount_in),
                        "amountOutMinimum": amount_out_minimum,
                        "sqrtPriceLimitX96": 0,
                    }
                ],
            )

            tx_params: dict[str, Any] = {
                "to": router,
                "data": data,
            }

            # If tokenIn is the chain native (WETH address not used), user would be providing ETH.
            # For simplicity, we do not auto-detect. Caller should set approval for ERC20s or wrap ETH beforehand.
            # If the swap requires msg.value (e.g., swapping ETH->token via WETH path internally),
            # that is out of scope for this minimal provider.

            tx_hash = wallet_provider.send_transaction(tx_params)
            receipt = wallet_provider.wait_for_transaction_receipt(tx_hash)

            return (
                f"Submitted Uniswap v3 exactInputSingle swap.\n"
                f"Transaction hash: {tx_hash}\n"
                f"Receipt: {receipt}"
            )
        except Exception as e:
            return f"Error performing exact input swap: {e!s}"

    def supports_network(self, network: Network) -> bool:
        return network.protocol_family == "evm"


def uniswap_v3_action_provider() -> UniswapV3ActionProvider:
    """Factory for UniswapV3ActionProvider."""
    return UniswapV3ActionProvider()


