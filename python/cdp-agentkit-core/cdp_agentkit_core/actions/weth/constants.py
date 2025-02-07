# Constants related to WETH actions

WETH_ADDRESS = "0x4200000000000000000000000000000000000006"

WETH_ABI = [
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "name": "account",
                "type": "address",
            },
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "type": "uint256",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "name": "wad",
                "type": "uint256",
            },
        ],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]
