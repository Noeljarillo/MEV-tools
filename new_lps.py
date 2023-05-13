import time
import sys
import threading
from web3 import Web3, exceptions
from tkinter import *
import webbrowser

INFURA_URL = "https://weathered-hardworking-glade.ethereum-goerli.discover.quiknode.pro/bf19c675a3260c97ed6d8691171a45a4e49bc2a1/"
UNISWAP_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
PAIR_CREATED_EVENT_SIGNATURE = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"
DEXTOOLS_BASE_URL = "https://www.dextools.io/app/es/ether/pair-explorer/"
ETHERSCAN_BASE_URL = "https://goerli.etherscan.io/tx/"
BLOCK_TIME = 15
SECONDS_IN_4_HOURS = 4 * 60 * 60
BLOCKS_IN_4_HOURS = SECONDS_IN_4_HOURS // BLOCK_TIME

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

def open_link(url):
    webbrowser.open(url)

def process_event(event):
    event_signature = event['topics'][0].hex()
    tx_hash = event['transactionHash'].hex()

    if event_signature == PAIR_CREATED_EVENT_SIGNATURE:
        token0, token1 = event['topics'][1].hex()[24:], event['topics'][2].hex()[24:]

        etherscan_link = f"{ETHERSCAN_BASE_URL}{tx_hash}"
        dextools_link = f"{DEXTOOLS_BASE_URL}{token0}-{token1}"

        
        output.insert(END, f"Block Number: {event['blockNumber']}\n")
        output.insert(END, f"Transaction Hash: {tx_hash}\n")
        output.insert(END, f"Token Pair: {token0} and {token1}\n")
        output.insert(END, "\n\n")

        output.insert(END, etherscan_link, ("link",))
        output.insert(END, "\n")
        output.insert(END, "\n\n")

        output.insert(END, dextools_link, ("link",))
        output.insert(END, "\n\n")
        output.yview(END)

def main():
    latest_block = w3.eth.block_number
    starting_block = max(latest_block - BLOCKS_IN_4_HOURS, 0)

    while True:
        try:
            new_block = w3.eth.block_number

            if new_block > latest_block:
                output.insert(END, f"New block detected: {new_block}\n")
                for event in w3.eth.get_logs({'fromBlock': starting_block, 'toBlock': new_block, 'address': UNISWAP_FACTORY_ADDRESS}):
                    process_event(event)

                latest_block = new_block
                starting_block = latest_block

            time.sleep(5)

        except exceptions.ConnectionError:
            output.insert(END, "Connection error, retrying...\n")
            time.sleep(10)

script_thread = threading.Thread(target=main)
script_thread.start()

root = Tk()
root.title("Uniswap Event Listener")
root.geometry("900x600")

output = Text(root, wrap='word', width=110, height=30, bg="#f0f0f0")
output.pack(padx=10, pady=10)

output.tag_configure("link", foreground="blue", underline=True)
output.tag_bind("link", "<Button-1>", lambda event: open_link(event.widget.get('insert linestart', 'insert lineend')))

output.config(state=NORMAL)

root.mainloop()
