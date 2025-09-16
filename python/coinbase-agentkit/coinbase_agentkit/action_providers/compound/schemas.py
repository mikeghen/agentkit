"""Schemas for Compound action provider."""

from typing import Literal

from pydantic import BaseModel, Field


class CompoundSupplySchema(BaseModel):
    """Input schema for supplying assets to Compound."""

    asset_id: Literal["weth", "cbeth", "cbbtc", "wsteth", "usdc"] = Field(
        ...,
        description="The asset ID to supply to the Compound market, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, or `usdc`",
    )
    amount: float = Field(
        ...,
        description="The amount of the asset to supply to the Compound market, e.g. `0.125` weth; `19.99` usdc",
    )


class CompoundWithdrawSchema(BaseModel):
    """Input schema for withdrawing assets from Compound."""

    asset_id: Literal["weth", "cbeth", "cbbtc", "wsteth", "usdc"] = Field(
        ...,
        description="The asset ID to withdraw from the Compound market, one of `weth`, `cbeth`, `cbbtc`, `wsteth`, or `usdc`",
    )
    amount: float = Field(
        ...,
        description="The amount of the asset to withdraw from the Compound market, e.g. `0.125` weth; `19.99` usdc",
    )


class CompoundBorrowSchema(BaseModel):
    """Input schema for borrowing assets from Compound."""

    asset_id: Literal["weth", "usdc"] = Field(
        ...,
        description="The asset ID to borrow from the Compound market, either `weth` or `usdc`",
    )
    amount: float = Field(
        ...,
        description="The amount of the asset to borrow from the Compound market, e.g. `0.125` weth; `19.99` usdc",
    )


class CompoundRepaySchema(BaseModel):
    """Input schema for repaying borrowed assets to Compound."""

    asset_id: Literal["weth", "usdc"] = Field(
        ...,
        description="The asset ID to repay to the Compound market, either `weth` or `usdc`",
    )
    amount: float = Field(
        ...,
        description="The amount of the asset to repay to the Compound market, e.g. `0.125` weth; `19.99` usdc",
    )


class CompoundDepositSchema(BaseModel):
    """Input schema for depositing assets to Compound for yield earning."""

    asset_id: Literal["usdc", "weth", "aero"] = Field(
        ...,
        description="The asset ID to deposit to the Compound market for yield earning, one of `usdc`, `weth`, or `aero`",
    )
    amount: float = Field(
        ...,
        description="The amount of the asset to deposit to the Compound market for yield earning, e.g. `0.125` weth; `19.99` usdc; `100.5` aero",
    )


class CompoundPortfolioSchema(BaseModel):
    """Input schema for getting portfolio details from Compound."""

    pass  # No inputs required
