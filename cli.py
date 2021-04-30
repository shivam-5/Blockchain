from communication import Communication
from consensus import Consensus
from blockchain import Blockchain
import webbrowser
import os
from api import API


class CLI:
    def __init__(self, command, params):
        if command == "HELP":
            self.__help()
        elif command == "ADDSHIPMENT":
            self.__addshipment(params)
        elif command == "REQUESTSHIPMENT":
            self.__requestshipment(params)
        elif command == "SHOWCONSENSUS":
            self.__consensus(params)
        elif command == "SHOWPENDING":
            self.__pending_transactions(params)
        elif command == "SHOWBLOCKCHAIN":
            self.__blockchain(params)
        elif command == "GUI":
            self.__gui(params)

        elif command == "":
            pass
        elif not command in ["EXIT", "QUIT", "Q"]:
            print("Invalid input. Type 'help' to see available commands.")

    def __help(self):
        print("HELP              Displays this help menu.")
        print("ADDSHIPMENT       Enters a shipment into the network (distributor only).")
        print("REQUESTSHIPMENT   Requests a vaccine shipment (client only).")
        print("SHOWCONSENSUS     Displays the consensus power of all nodes, or a certain node if specified in the first parameter.")
        print("SHOWPENDING       Displays all transactions that are waiting to be put into a block.")
        print("SHOWBLOCKCHAIN    Displays the entire blockchain.")
        print("GUI               Open the GUI for this node.")

    def __addshipment(self, params):
        if len(params) == 0 or params[0] in ["?", "HELP"]:
            self.__show_command_help(
                usage="addshipment id srclocation destlocation qty",
                description="Enters a shipment into the network."
            )
        elif len(params) == 3:
            shipment_id = params[0]
            src = params[1]
            dest = params[2]
            qty = params[3]

            confirmation = input(
                "Are you sure you want to add this shipment to the blockchain? This action is irreversible without the agreement of all network nodes (y/n): ").upper()

            if confirmation == "Y":
                print("\nAdding to blockchain...")
                blockchain = Blockchain.instance()

                self.node_comm = Communication.instance()

                transaction = blockchain.create_distributor_transaction(shipment_id, blockchain.get_node_id(), src, dest, qty,
                                                                        blockchain.get_node_type(),
                                                                        blockchain.get_node_name())
                self.node_comm.broadcast_transaction(transaction)
                print("Shipment is now pending.\n> ", end="")

    def __requestshipment(self, params):
        if len(params) == 0 or params[0] in ["?", "HELP"]:
            self.__show_command_help(
                usage="requestshipment destlocation qty distributor",
                description="Requests a shipment of vaccines from a given distributor."
            )
        elif len(params) == 3:
            dest = params[0]
            qty = params[1]
            distributor = params[2]

            confirmation = input(
                "Are you sure you want to request this shipment? This action is irreversible without the agreement of all network nodes (y/n): ").upper()

            if confirmation == "Y":
                print("\nAdding to blockchain...")
                blockchain = Blockchain.instance()

                self.node_comm = Communication.instance()

                transaction = blockchain.create_client_transaction(blockchain.get_node_name(), dest, qty, distributor, blockchain.get_node_type())

                self.node_comm.broadcast_transaction(transaction)
                print("Request has been received and is now pending.\n> ", end="")

    def __consensus(self, params):
        if len(params) > 0 and params[0] in ["?", "HELP"]:
            self.__show_command_help(
                usage="consensus [node]",
                description="Displays the consensus power of all nodes, or a certain node if specified in the first parameter."
            )
        else:
            consensus_power = Consensus.instance().get_consensus_power()
            if len(params) > 0:
                node = params[0]
                if node in consensus_power:
                    print(node + " : " + str(consensus_power[node]))
                else:
                    print("Node " + node + " does not exist on the network. Please try again.")
            else:
                print(consensus_power)

    def __pending_transactions(self, params):
        if len(params) > 0 and params[0] in ["?", "HELP"]:
            self.__show_command_help(
                usage="showpending",
                description="Displays all transactions that are waiting to be put into a block."
            )
        else:
            for transaction in Blockchain.instance().get_pending_transactions():
                print(str(transaction))

    def __blockchain(self, params):
        if len(params) > 0 and params[0] in ["?", "HELP"]:
            self.__show_command_help(
                usage="showblockchain",
                description="Displays the entire blockchain."
            )
        else:
            print(str(Blockchain.instance()))

    # Execute the GUI.
    def __gui(self, params):
        if len(params) > 0 and params[0] in ["?", "HELP"]:
            self.__show_command_help(
                usage="gui",
                description="Open the GUI for this node."
            )
        else:
            webbrowser.open("file:///" + os.getcwd() + "/gui/index.html", new=2)
            with open("gui/js/api-port.js", "w") as f:
                f.write("window.apiPort = " + str(API.instance().get_port()) + ";")

    def __show_command_help(self, usage, description="No description available for this command."):
        print("Usage:\n  " + usage)
        print("Description:\n  " + description)
