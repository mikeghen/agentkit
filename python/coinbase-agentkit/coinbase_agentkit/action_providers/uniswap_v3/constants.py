"""Constants and ABIs for Uniswap v3 SwapRouter interactions."""

SUPPORTED_NETWORKS = ["base-mainnet", "base-sepolia", "ethereum-sepolia"]

UNISWAP_SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    }
]

# Minimal QuoterV2 ABI for quoting swaps (mirrors WOW utils usage)
UNISWAP_QUOTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct IQuoterV2.QuoteExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceX96After", "type": "uint160"},
            {"internalType": "uint32", "name": "initializedTicksCrossed", "type": "uint32"},
            {"internalType": "uint256", "name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# Minimal network addresses for Base networks; extend as needed.
# Asset addresses - Base Mainnet
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
CBETH_ADDRESS = "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22"
CBBTC_ADDRESS = "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf"
WSTETH_ADDRESS = "0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452"
AERO_ADDRESS = "0x940181a94A35A4569E4529A3CDfB74e38FD98631"

# Asset addresses - Base Sepolia
USDC_ADDRESS_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
WETH_ADDRESS_SEPOLIA = "0x4200000000000000000000000000000000000006"
CBETH_ADDRESS_SEPOLIA = "0x774eD9EDB0C5202dF9A86183804b5D9E99dC6CA3"

# Asset addresses - ETH Sepolia
USDC_ADDRESS_ETH_SEPOLIA = "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
WETH_ADDRESS_ETH_SEPOLIA = "0x2D5ee574e710219a521449679A4A7f2B43f046ad"
COMP_ADDRESS_ETH_SEPOLIA = "0xA6c8D1c55951e8AC44a0EaA959Be5Fd21cc07531"
WBTC_ADDRESS_ETH_SEPOLIA = "0xa035b9e130F2B1AedC733eEFb1C67Ba4c503491F"

# Asset mapping for easy lookup
ASSET_ADDRESSES = {
    "base-mainnet": {
        "usdc": USDC_ADDRESS,
        "weth": WETH_ADDRESS,
        "cbeth": CBETH_ADDRESS,
        "cbbtc": CBBTC_ADDRESS,
        "wsteth": WSTETH_ADDRESS,
        "aero": AERO_ADDRESS,
    },
    "base-sepolia": {
        "usdc": USDC_ADDRESS_SEPOLIA,
        "weth": WETH_ADDRESS_SEPOLIA,
        "cbeth": CBETH_ADDRESS_SEPOLIA,
    },
    "ethereum-sepolia": {
        "usdc": USDC_ADDRESS_ETH_SEPOLIA,
        "weth": WETH_ADDRESS_ETH_SEPOLIA,
        "comp": COMP_ADDRESS_ETH_SEPOLIA,
        "wbtc": WBTC_ADDRESS_ETH_SEPOLIA,
    }
}

UNISWAP_V3_ADDRESSES = {
    "base-sepolia": {
        "swap_router_02": "0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4",
        "uniswap_quoter": "0xC5290058841028F1614F3A6F0F5816cAd0df5E27",
    },
    "base-mainnet": {
        "swap_router_02": "0x2626664c2603336E57B271c5C0b26F421741e481",
        "uniswap_quoter": "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",
    },
    "ethereum-sepolia": {
        "swap_router_02": "0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E",
        "uniswap_quoter": "0xEd1f6473345F45b75F8179591dd5bA1888cf2FB3",
    }
}


