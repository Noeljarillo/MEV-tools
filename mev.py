import time
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
ETH_NODE_URL = ""
MY_ADDRESS = ""
MY_PRIVATE_KEY = ""
SANDWICH_ATTACKER_ADDRESS = ""
SANDWICH_ATTACKER_ABI =   # 

w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if not w3.isConnected():
    raise ValueError("Failed to connect to Ethereum node")

def monitor_mempool():
    while True:
        try:
            pending_transactions = w3.eth.getBlock("pending")["transactions"]

            for tx_hash in pending_transactions:
                transaction = w3.eth.getTransaction(tx_hash)
                is_target_tx = (
                    transaction["to"] == SANDWICH_ATTACKER_ADDRESS
                    and transaction["input"].startswith("0x18cbafe5")  # UniswapV2Router02.swapExactTokensForTokens
                )

                if is_target_tx and identify_target_transactions(transaction):
                    gas_price = w3.eth.gasPrice
                    optimized_gas_price = calculate_gas_price(gas_price, transaction)
                    try:
                        execute_sandwich_attack(
                            tx_hash,
                            amountIn,
                            amountOutMin,
                            path,
                            to,
                            deadline,
                            optimized_gas_price
                        )
                    except Exception as e:
                        logging.error(f"Error executing sandwich attack: {e}")

        except Exception as e:
            logging.error(f"Error monitoring mempool: {e}")
            time.sleep(60)  # Wait for a minute before retrying

def identify_target_transactions(tx):
    if tx["to"] != UNISWAP_ROUTER_ADDRESS:
        return False

    if not tx["input"].startswith("0x18cbafe5"):  # UniswapV2Router02.swapExactTokensForTokens
        return False

    decoded_input = uniswap_router.decode_function_input(tx["input"])
    path = decoded_input[0]
    token_in = path[0]
    token_out = path[-1]

    if token_in not in LOW_CAP_TOKENS or token_out not in LOW_CAP_TOKENS:
        return False

    try:
        trade_details = get_trade_details(tx)
        if trade_details["amount_in"] == 0 or trade_details["amount_out"] == 0:
            return False  # Invalid trade

        # Check if the price impact is within the acceptable range
        price_impact = (trade_details["amount_out"] - trade_details["amount_in"]) / trade_details["amount_in"]
        if abs(price_impact) > MAX_PRICE_IMPACT:
            return False

        # Check if the expected profit is greater than the minimum profit
        expected_profit = calculate_expected_profit(trade_details["amount_in"], trade_details["amount_out"])
        if expected_profit < MIN_PROFIT:
            return False

        return True

    except Exception as e:
        logging.error(f"Error identifying target transaction: {e}")
        return False


def calculate_gas_price(base_gas_price, target_tx):
    gas_price_multiplier = 1.1
    return int(base_gas_price * gas_price_multiplier)

def execute_sandwich_attack(tx_hash, amountIn, amountOutMin, path, to, deadline, gas_price):
    sandwich_attacker_contract = w3.eth.contract(
        address=SANDWICH_ATTACKER_ADDRESS,
        abi=SANDWICH_ATTACKER_ABI
    )

    estimated_gas = sandwich_attacker_contract.functions.attack(
        amountIn,
        amountOutMin,
        path,
        to,
        deadline
    ).estimateGas()

    txn = sandwich_attacker_contract.functions.attack(
        amountIn,
        amountOutMin,
        path,
        to,
        deadline
    ).buildTransaction({
        'from': MY_ADDRESS,
        'value': w3.toWei(0.1, 'ether'),
        'gas': estimated_gas,
        'gasPrice': gas_price,
        'nonce': w3.eth.getTransactionCount(MY_ADDRESS),
    })

    signed_txn = w3.eth.account.signTransaction(txn, MY_PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    logging.info(f"Front-running transaction sent: {signed_txn.hash.hex()}")

    while True:
        try:
            receipt = w3.eth.getTransactionReceipt(tx_hash)
            if receipt is not None:
                break
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error monitoring target transaction: {e}")

    # Execute the backrunning transaction
    backrun_txn = sandwich_attacker_contract.functions.backrun(
        amountIn,
        amountOutMin,
        path,
        to,
        deadline
    ).buildTransaction({
        'from': MY_ADDRESS,
        'value': w3.toWei(0.1, 'ether'),
        'gas': estimated_gas,
        'gasPrice': gas_price,
        'nonce': w3.eth.getTransactionCount(MY_ADDRESS),
    })

    signed_backrun_txn = w3.eth.account.signTransaction(backrun_txn, MY_PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_backrun_txn.rawTransaction)

    logging.info(f"Backrunning transaction sent: {signed_backrun_txn.hash.hex()}")

    # Calculate profit/loss
    # This is a simplified example; you should implement a more accurate calculation based on the actual token prices
    profit = int(amountIn) * int(amountOutMin) - int(amountIn)
    logging.info(f"Profit from sandwich attack: {profit}")

if __name__ == "__main__":
    monitor_mempool()
