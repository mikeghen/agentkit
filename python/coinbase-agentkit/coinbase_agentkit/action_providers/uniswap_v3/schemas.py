"""Schemas for Uniswap v3 swap actions."""

from pydantic import BaseModel, Field


class ExactInputSingleSchema(BaseModel):
    """Input schema for performing an exact input swap on Uniswap v3."""

    token_in: str = Field(description="Address of the token to swap from")
    token_out: str = Field(description="Address of the token to swap to")
    fee: int = Field(description="Uniswap v3 pool fee in hundredths of a bip, e.g., 3000")
    amount_in: int = Field(description="Amount of token_in to swap (in wei)")
    recipient: str | None = Field(
        default=None, description="Recipient address; defaults to the wallet address if not set"
    )


