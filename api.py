from communication import Communication
from blockchain import Blockchain
from flask import Flask, request, jsonify
from threading import Thread
from flask_cors import CORS, cross_origin
import os
import socket
import webbrowser
import logging
from waitress import serve


class API:
    """ 
    Singleton class - Can only be one instance of the API per node.
    Get the instance via the static instance() method.

    """

    app = Flask(__name__)

    single_instance = None

    def __init__(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        cors = CORS(API.app)
        API.app.config['CORS_HEADERS'] = 'Content-Type'
        Thread(target=self.start_server).start()

    @staticmethod
    def instance():
        if API.single_instance == None:
            API.single_instance = API()
        return API.single_instance

    def start_server(self):
        self.port = 5000
        while self.is_port_in_use(self.port):
            self.port += 1
        with open("gui/js/api-port.js", "w") as f:
            f.write("window.apiPort = " + str(self.port) + ";")
            f.close()

        print("\nAPI online on port", str(self.port), "and listening for connections from the GUI!\n> ", end="")
        try:
            webbrowser.open("file:///" + os.getcwd() + "/gui/index.html", new=2)
            serve(app=API.app, port=self.port)
        except:
            print("An error occurred when starting the REST API server. Please restart the node and try again. Otherwise, simply use the CLI.")

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def get_port(self):
        if API.single_instance:
            return self.port
        return None

    @app.route("/add-shipment", methods=["POST"])
    @cross_origin()
    def add_shipment():
        response = jsonify(success=False, status_code=500)
        if request.method == "POST":
            shipment_id = request.form["shipment-id"]
            src = request.form["src-location"]
            dest = request.form["dest-location"]
            qty = request.form["qty"]

            print("\nAdding to blockchain...")

            blockchain = Blockchain.instance()
            node_comm = Communication.instance()
            transaction = blockchain.create_distributor_transaction(shipment_id, blockchain.get_node_id(), src, dest, qty,
                                                                    blockchain.get_node_type(),
                                                                    blockchain.get_node_name())
            node_comm.broadcast_transaction(transaction)
            print("Shipment is now pending.\n> ", end="")

            response = jsonify(success=True, status_code=200)
        return response

    @app.route("/request-shipment", methods=["POST"])
    @cross_origin()
    def request_shipment():
        response = jsonify(success=False, status_code=500)
        if request.method == "POST":
            dest = request.form["dest-location"]
            qty = request.form["qty"]
            distributor = request.form["distributor"]

            print("\nAdding to blockchain...")

            blockchain = Blockchain.instance()
            node_comm = Communication.instance()
            transaction = blockchain.create_client_transaction(blockchain.get_node_name(), dest, qty, distributor, blockchain.get_node_type())
            node_comm.broadcast_transaction(transaction)

            print("Request has been received and is now pending.\n> ", end="")
            response = jsonify(success=True, status_code=200)
        return response

    @app.route("/get-node-info", methods=["GET"])
    @cross_origin()
    def get_distributor():
        blockchain = Blockchain.instance()
        response = jsonify(success=True, status_code=200, distributor_client=blockchain.get_node_name(), node_id=blockchain.get_node_id(), node_type=blockchain.get_node_type())
        return response

    @app.route("/get-pending-transactions", methods=["GET"])
    @cross_origin()
    def get_pending_transactions():
        blockchain = Blockchain.instance()
        pending_transactions = blockchain.get_pending_transactions()
        response = jsonify(success=True, status_code=200, pending_transactions=[str(transaction).strip()[:-1] for transaction in pending_transactions])
        return response

    @app.route("/get-block", methods=["GET"])
    @cross_origin()
    def get_block():
        blockchain = Blockchain.instance().get_blockchain()
        block_index = request.args.get("blockIndex", default=0, type=int)
        if abs(block_index) < len(blockchain):
            block = str(blockchain[block_index - 1]).strip()
            response = jsonify(success=True, status_code=200, block=block[:-1])
        else:
            response = jsonify(success=True, status_code=404)
        return response
