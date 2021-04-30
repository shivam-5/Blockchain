from communication import Communication
import pickle
import threading
import time
from queue import Queue, Empty

from block import Block
import uuid

from transactions.client_transaction import ClientTransaction
from transactions.distributor_transaction import DistributorTransaction


class Blockchain:
    """ 
    Singleton class - Can only be one instance of the blockchain per node.
    Get the instance via the static instance() method.

    """

    single_instance = None

    comm = None
    node_id = None

    max_pending_transactions = 5
    max_block_wait_time = 60

    candidate_blocks = Queue()
    temp_blocks = dict()
    consensus_results = dict()

    thread_wait = None

    def __init__(self, blockchain, pending_transactions, node_id, node_name, node_type):
        self.blockchain = blockchain
        self.pending_transactions = pending_transactions
        self.node_id = node_id
        self.node_type = node_type
        self.node_name = node_name
        self.start_block_wait_timer()

    def get_node_id(self):
        return self.node_id

    def get_node_name(self):
        return self.node_name

    def get_node_type(self):
        return self.node_type

    def start_block_wait_timer(self):
        self.thread_wait = threading.Thread(target=self.new_block_timer, daemon=True)
        self.thread_wait.start()

    # Display the blockchain nicely when printed.
    def __str__(self):
        blockchain_string = "[\n"
        for b in self.blockchain:
            blockchain_string += str(b)
        blockchain_string += "\n]"
        return blockchain_string

    # STATIC - Fetch and return the single instance of the blockchain, or if it doesn't already exist, instantiate it.
    @staticmethod
    def instance(blockchain=[], pending_transactions=[], node_id=None, node_name=None, node_type=None):
        if Blockchain.single_instance is None:
            Blockchain.single_instance = Blockchain(blockchain, pending_transactions, node_id, node_name, node_type)
        return Blockchain.single_instance

    # Set instance to communicate with network
    def set_communication(self, comm):
        self.comm = comm

    # Fetch the entire blockchain data structure.
    def get_blockchain(self):
        return self.blockchain

    # Set the blockchain data structure.
    def set_blockchain(self, blockchain):
        self.blockchain = blockchain

    # Fetch and return the pending transactions for the current block.
    def get_pending_transactions(self):
        return self.pending_transactions

    # Create the first block in the blockchain.
    def create_genesis(self):
        genesis = Block(
            uuid.uuid4(),  # Block ID
            0,  # block number in blockchain
            "",  # Transactions for this block.
            time.time(),  # Block timestamp.
            "Evening Standard 02/03/2021 Hunt for mutant carrier continues amid row over face masks in schools."
        )
        self.blockchain.append(genesis)
        return genesis

    # Initialise and add a new block to the blockchain.
    def create_block(self):
        print(len(self.pending_transactions))
        block = Block(
            id=str(uuid.uuid4()),  # Block ID.
            block_number=len(self.blockchain),  # Block number
            transactions=self.pending_transactions,  # Transactions for this block.
            timestamp=time.time(),  # Block timestamp.
            previous_digest=Block.get_digest(self.blockchain[-1])  # Get the hash digest of the last block.
        )
        self.pending_transactions = []  # Clears pending transactions
        self.temp_blocks[block.id] = block  # Add newly created block to temporary blocks
        self.consensus_results[block.id] = []   # Stores consensus results for this block's validation
        self.comm.broadcast_block(block)    # Broadcast this block over the network for validation
        return block

    # If block is validated based on consensus, add it to blockchain
    def block_validated(self, blockId):
        if blockId not in self.temp_blocks:
            return
        print("\nBlock validated through consensus. Adding", blockId, "to blockchain.\n> ", end="")
        block = self.temp_blocks[blockId]   # Retrieve block from temporary blocks
        self.blockchain.append(block)   # Append block to blockchain
        self.temp_blocks.pop(blockId)   # Remove from temporary blocks
        self.consensus_results.pop(blockId)     # Clear this block's consensus results
        print("\n", str(self), "\n> ", end="")

    # Create a transaction (shipment) and returns it
    def create_distributor_transaction(self, shipment_id, origin_node, src_location, dest_location, qty, type,
                                       distributor):
        transaction = DistributorTransaction(
            shipment_id,
            # self.__generate_shipment_id(distributor),
            origin_node,
            src_location,
            dest_location,
            qty,
            distributor,
            type,
            time.time()
        )
        return transaction

    # Create a transaction (request) and returns it
    def create_client_transaction(self, client, dest_location, qty, distributor, type):
        transaction = ClientTransaction(
            # self.__generate_shipment_id(client),
            client,
            dest_location,
            qty,
            distributor,
            type,
            time.time()
        )
        return transaction

    # PRIVATE - Generate a shipment identifier in the format: BlockNum-TransactionInBlockNum/DistributorInitials
    def __generate_distributor_transaction_id(self, distributor):
        block_id = str(len(self.blockchain) - 1)
        transaction_id = str(len(self.pending_transactions))
        distributor_id = "".join([i[0] for i in distributor.split(" ")])

        return block_id + "-" + transaction_id + "/" + distributor_id

    # PRIVATE - Generate a shipment identifier in the format: BlockNum-TransactionInBlockNum/ClientInitials
    def __generate_client_transaction_id(self, client):
        block_id = str(len(self.blockchain) - 1)
        transaction_id = str(len(self.pending_transactions))
        client_id = "".join([i[0] for i in client.split(" ")])

        return block_id + "-" + transaction_id + "/" + client_id

    # Timer thread that creates block with pending transactions on timeout
    def new_block_timer(self):
        while True:
            count = 0
            while count < self.max_block_wait_time and self.thread_wait.is_alive():
                time.sleep(5)
                count += 5
            if len(self.pending_transactions) != 0 and self.thread_wait.is_alive():
                print("\nBlock Timer Expired. Creating block!\n> ", end="")
                self.create_block()
            if self.thread_wait.is_alive() is False:
                self.start_block_wait_timer()
