import threading
import time
from collections import Set

import jsonpickle
import pika


# Handles the communication between nodes in the blockchain network
class Communication():
    connected_nodes = set()     # Set of connected nodes in the network
    single_instance = None

    my_Lock = threading.Lock()

    def __init__(self, id, node_name, blockchain, node_type):
        self.id = id
        self.node_name = node_name
        self.blockchain = blockchain
        if node_type == 'DISTRIBUTOR':      # Register to listeners only for distributor nodes
            thread_validation = threading.Thread(target=self.register_listeners, args=(), daemon=True)
            thread_validation.start()

    @staticmethod
    def instance(id=None, node_name=None, blockchain=None, node_type=None):
        if Communication.single_instance == None:
            Communication.single_instance = Communication(id, node_name, blockchain, node_type)
        return Communication.single_instance

    # Broadcast all nodes in network
    # status = connect/disconnect
    def notify_connection(self, status):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(status, exchange_type='fanout')
        channel.basic_publish(exchange=status, routing_key='', body=self.id)
        connection.close()

    # Broadcast all nodes in network a block for validation
    def broadcast_block(self, block):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare('block_validation_request', exchange_type='fanout')
        channel.basic_publish(exchange='block_validation_request', routing_key='',
                              body=jsonpickle.encode(block, unpicklable=True))
        connection.close()

    # Broadcast all nodes in network a transaction for validation
    def broadcast_transaction(self, transction):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare('transaction', exchange_type='fanout')
        channel.basic_publish(exchange='transaction', routing_key='',
                              body=jsonpickle.encode(transction, unpicklable=True))
        connection.close()

    # Broadcast all nodes in network whether a block is validated or not
    def broadcast_block_validation_result(self, result):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare('block_validation_result', exchange_type='fanout')
        channel.basic_publish(exchange='block_validation_result', routing_key='', body=result)
        connection.close()

    # Register for various listeners over the network
    def register_listeners(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        # Setup listener for node connection
        channel.exchange_declare('connect', exchange_type='fanout')
        connectionQueue = channel.queue_declare(queue='').method.queue
        channel.queue_bind(connectionQueue, 'connect')
        channel.basic_consume(queue=connectionQueue, on_message_callback=self.node_connected, auto_ack=True)

        # Setup listener for node disconnection
        channel.exchange_declare('disconnect', exchange_type='fanout')
        disconenctionQueue = channel.queue_declare(queue='').method.queue
        channel.queue_bind(disconenctionQueue, 'disconnect')
        channel.basic_consume(queue=disconenctionQueue, on_message_callback=self.node_disconnected, auto_ack=True)

        # Setup listener for block validation approval
        channel.exchange_declare('block_validation_result', exchange_type='fanout')
        validationResultQueue = channel.queue_declare(queue='').method.queue
        channel.queue_bind(validationResultQueue, 'block_validation_result')
        channel.basic_consume(queue=validationResultQueue, on_message_callback=self.block_validation_result,
                              auto_ack=True)

        # Setup listener for new transaction in the network
        channel.exchange_declare('transaction', exchange_type='fanout')
        validationResultQueue = channel.queue_declare(queue='').method.queue
        channel.queue_bind(validationResultQueue, 'transaction')
        channel.basic_consume(queue=validationResultQueue, on_message_callback=self.new_transaction,
                              auto_ack=True)

        # Setup listener for block validation request
        channel.exchange_declare('block_validation_request', exchange_type='fanout')
        validationRequestQueue = channel.queue_declare(queue='').method.queue
        channel.queue_bind(validationRequestQueue, 'block_validation_request')
        channel.basic_consume(queue=validationRequestQueue, on_message_callback=self.block_validation_request,
                              auto_ack=True)

        channel.start_consuming()

    # Callback when a new node is connected over network
    def node_connected(self, ch, method, properties, body):
        remoteId = str(body).split("'")[1]
        if remoteId != self.id and remoteId not in self.connected_nodes:
            print("\nNode connected: ", remoteId, "\n> ", end="")
            self.connected_nodes.add(remoteId)
            self.notify_connection('connect')

    # Callback when a node is disconnected from network
    def node_disconnected(self, ch, method, properties, body):
        remoteId = str(body).split("'")[1]
        if remoteId != self.id and remoteId in self.connected_nodes:
            print("\nNode disconnected: ", remoteId, "\n> ", end="")
            self.connected_nodes.remove(remoteId)

    # Callback when a new pending transaction is received over network
    def new_transaction(self, ch, method, properties, body):
        transaction = jsonpickle.decode(body)
        if transaction not in self.blockchain.pending_transactions:
            if transaction.get_transaction_type() == 'CLIENT':
                if transaction.get_requested_distributor().upper() != self.node_name.upper():
                    return
            print("\nNew request received!\n> ", end="")
            self.blockchain.pending_transactions.append(transaction)

    # Callback on receiving a validation from another node for a block
    def block_validation_result(self, ch, method, properties, body):
        result = str(body).split("'")[1].split(" ")
        node_id = result[0]
        block_id = result[1]
        validationResult = result[2]
        print("\nResult:", result, "\n> ", end="")

        with self.my_Lock:
            if block_id in self.blockchain.temp_blocks:
                block = self.blockchain.temp_blocks[block_id]
                if block.block_number <= self.blockchain.blockchain[-1].block_number:
                    # Discard block since it was late in reaching/requesting consensus
                    # and another block is already added to blockchain
                    # Maybe send approval failure?
                    return
            if validationResult == 'success':
                # Increase consensus count for this block and check if 50% reached
                if block_id in self.blockchain.consensus_results.keys():
                    consensus_results = self.blockchain.consensus_results[block_id]
                    if node_id not in consensus_results:
                        consensus_results.append(node_id)

                    # Reach more than 50% consensus
                    # Change the measure to stake value rather than node count?
                    if len(consensus_results) > ((len(self.connected_nodes) + 1) / 2):
                        # Add approved block to blockchain
                        self.blockchain.block_validated(block_id)
                    else:
                        self.blockchain.consensus_results[block_id] = consensus_results
                else:
                    # Received this block first time. Add to consensus list and wait for 50% approval
                    self.blockchain.consensus_results[block_id] = [node_id]

    # Callback on receiving a validation request for a new block over the network
    def block_validation_request(self, ch, method, properties, body):
        block = jsonpickle.decode(body)

        with self.my_Lock:
            if block.block_number <= self.blockchain.blockchain[-1].block_number:
                # Discard block since it was late in reaching/requesting consensus
                # and another block is already added there
                # Maybe send approval failure?
                return

            print("\nValidate block: ", block, "\n> ", end="")
            time.sleep(10)
            # Received a new block, add it to temp list and wait for 50% consensus
            self.blockchain.temp_blocks[block.id] = block
            if block.id not in self.blockchain.consensus_results.keys():
                self.blockchain.consensus_results[block.id] = []
            self.blockchain.consensus_results[block.id].append(self.id)

        # If block is validated, broadcast it to all nodes
        # Message contains current node's id, block id, approval result
        return self.broadcast_block_validation_result(str(self.id) + " " + str(block.id) + " " + "success")
