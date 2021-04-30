from cli import CLI
from communication import Communication
from consensus import Consensus
from api import API
import pickle
import os
import atexit
import signal

from blockchain import Blockchain
import yaml
import hashlib
import random


class Node:
    """
    Singleton class - Can only be one instance of the node class per node.

    Handle all node operations that don't relate to the actual blockchain data structure.
    Networking may be handled here.

    """

    single_instance = None

    def __init__(self):
        self.NODE_ID = None
        self.NODE_NAME = None
        self.NODE_TYPE = None
        self.setup_node()
        # Create the blockchain instance for this node if one doesn't exist
        if not os.path.exists("blockchain.pickle"):
            self.blockchain = Blockchain.instance(node_id=self.NODE_ID, node_name=self.NODE_NAME,
                                                  node_type=self.NODE_TYPE)
            print("First time booting! Creating genesis block...")
            self.blockchain.create_genesis()
        else:
            print("Successfully identified blockchain on this device. Loading into memory...")
            loaded_blockchain = self.load_blockchain()
            loaded_pending_transactions = self.load_pending_transactions()
            self.blockchain = Blockchain.instance(loaded_blockchain, loaded_pending_transactions, self.NODE_ID,
                                                  self.NODE_NAME, self.NODE_TYPE)
        API.instance()
        Consensus.instance(self.NODE_NAME)

        self.node_comm = Communication.instance(self.NODE_ID, self.NODE_NAME, self.blockchain, self.NODE_TYPE)
        self.blockchain.set_communication(self.node_comm)
        print(self.NODE_ID, self.NODE_NAME)
        # Send a connection request to other distributor nodes in network
        if self.NODE_TYPE == 'DISTRIBUTOR':
            self.node_comm.notify_connection('connect')

    @staticmethod
    def instance():
        if Node.single_instance == None:
            Node.single_instance = Node()
        return Node.single_instance

    # Recreate the current block so that transactions can continue to be added to it even if
    # the node has stopped midway through the block.
    def __reinstate_current_block(self, loaded_pending_transactions):
        blockchain = self.blockchain.get_blockchain()
        curr_block = blockchain[-1]
        curr_block.set_transactions(loaded_pending_transactions)
        blockchain[-1] = curr_block
        self.blockchain.set_blockchain(blockchain)

    # Save the blockchain to the blockchain.pickle file.
    def dump_blockchain(self):
        print("Saving blockchain state...")
        with open("blockchain.pickle", "wb") as f:
            pickle.dump(self.blockchain.get_blockchain(), f, pickle.HIGHEST_PROTOCOL)

    # Load the blockchain from the blockchain.pickle file.
    def load_blockchain(self):
        with open("blockchain.pickle", "rb") as f:
            return pickle.load(f)

    # Save the pending transactions to the pending_transactions.pickle file.
    def dump_pending_transactions(self):
        print("Saving pending transactions...")
        with open("pending_transactions.pickle", "wb") as f:
            pickle.dump(self.blockchain.get_pending_transactions(), f, pickle.HIGHEST_PROTOCOL)

    # Load the pending transactions from the pending_transactions.pickle file.
    def load_pending_transactions(self):
        with open("pending_transactions.pickle", "rb") as f:
            loaded_pending_transactions = pickle.load(f)
        return loaded_pending_transactions

    def disconnect(self):
        self.node_comm.notify_connection('disconnect')

    # Setup type of node and its details
    # Store in config.yaml if started first time
    # Else read it from existing config.yaml
    def setup_node(self):
        if os.path.exists("config.yaml"):
            with open("config.yaml", "r") as config:
                loaded_config = yaml.safe_load(config)
                self.NODE_ID = loaded_config["node_id"]
                self.NODE_TYPE = loaded_config["node_type"]
                if self.NODE_TYPE == "DISTRIBUTOR":
                    self.NODE_NAME = loaded_config["distributor"]
                else:
                    self.NODE_NAME = loaded_config["client"]
                config.close()
        else:
            print("No node ID found. Generating one...")
            self.NODE_ID = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            self.NODE_TYPE = input("Are you a client or distributor? (client/distributor) : ").upper()
            while not self.NODE_TYPE in ["CLIENT", "DISTRIBUTOR"]:
                self.NODE_TYPE = input("Are you a client or distributor? (client/distributor) : ").upper()
            self.NODE_NAME = "N/A"
            if self.NODE_TYPE == "DISTRIBUTOR":
                self.NODE_NAME = input(
                    "No distributor found. What distributor do you belong to? (eg: Pfizer) : ").upper()
                with open("config.yaml", "w") as config:
                    yaml.dump({"node_id": self.NODE_ID, "distributor": self.NODE_NAME, "node_type": self.NODE_TYPE},
                          config)
                config.close()

            else:
                self.NODE_NAME = input(
                    "No client found. What is the client's name? (eg: Guy's Hospital) : ").upper()
                with open("config.yaml", "w") as config:
                    yaml.dump({"node_id": self.NODE_ID, "client": self.NODE_NAME, "node_type": self.NODE_TYPE},
                              config)
                    config.close()


if __name__ == "__main__":
    print("\nNode initialising...")
    node = Node.instance()
    atexit.register(node.dump_blockchain)
    atexit.register(node.dump_pending_transactions)
    print("\nNode successfully started! Ready for input. Type 'help' to see available commands.")

    command = [""]
    while command[0] not in ["EXIT", "QUIT", "Q"]:
        command = input("\n> ").upper().split(" ")
        CLI(command[0], None or command[1:])

    node.disconnect()
    node.dump_blockchain()
    node.dump_pending_transactions()
    print("\nExiting!")
    os.kill(os.getpid(), signal.SIGTERM)
