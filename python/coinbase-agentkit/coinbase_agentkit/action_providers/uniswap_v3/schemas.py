"""Schemas for Uniswap v3 swap actions."""

from typing import Literal
from pydantic import BaseModel, Field


class ExactInputSingleSchema(BaseModel):
    """Input schema for performing an exact input swap on Uniswap v3."""

    token_in: Literal["weth", "cbeth", "cbbtc", "wsteth", "usdc", "aero"] = Field(
        ...,
        description="The asset ID to swap from, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, `usdc`, or `aero`",
    )
    token_out: Literal["weth", "cbeth", "cbbtc", "wsteth", "usdc", "aero"] = Field(
        ...,
        description="The asset ID to swap to, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, `usdc`, or `aero`",
    )
    fee: int = Field(description="Uniswap v3 pool fee in hundredths of a bip, e.g., 3000")
    amount_in: str = Field(
        ...,
        description="The amount of the input token to swap, e.g. `0.125` weth; `19.99` usdc",
    )
    recipient: str | None = Field(
        default=None, description="Recipient address; defaults to the wallet address if not set"
    )


