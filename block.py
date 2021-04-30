import hashlib
import json


class Block:
    """
    Manage the structure of blocks in the blockchain.

    """

    def __init__(self, id, block_number, transactions, timestamp, previous_digest=None):
        self.id = id
        self.block_number = block_number
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_digest = previous_digest

    # Display the block nicely when printed.
    def __str__(self):
        transactions_string = ""

        transactions_string = "["
        for t in self.transactions:
            transactions_string += str(t)
        transactions_string += "\n            ]"

        block_string = f"""
        {{
            "id": "{self.id}",
            "block_number": "{self.block_number}",
            "timestamp": "{self.timestamp}",
            "transactions": {transactions_string},
            "previous_digest": "{self.previous_digest}"
        }},\n"""
        return block_string

    def get_transactions(self):
        return self.transactions

    def set_transactions(self, transactions):
        self.transactions = transactions

    # STATIC - Get the hash of a given block.
    @staticmethod
    def get_digest(block):
        block_as_json = json.dumps(str(block)).encode()
        digest = hashlib.sha256(block_as_json).hexdigest()
        return digest
