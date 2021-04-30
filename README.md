# 7CCSMDLC Coursework – A Vaccine Supply Chain Distribution Blockchain

## How to run?

The entry point is node.py and therefore that's the file you want to run. It's probably best to execute it using cmd/terminal.

## What am I looking at?

Once you run the node you'll see a JSON dump. That's the blockcahin. I chose JSON because it's the easiest to work with in python - especially for a small blockchain like this.

The blockchain network consists of nodes, which house blocks, which contain transactions.

### Each block has

* An ID.
* A timestamp.
* A set of transactions.
* The hash of the previous block (previous_digest). In the case of the genesis (initial, id=0) block, this can be arbitrarily set and hence the choice to include a headline as Bitcoin did here.

### Each transaction has

* A shipment ID, automatically calculated in the format: BlockID-TransactionNumInBlock/DistributorInitials.
* An origin node - the first node which entered the transaction into the network.
* A source location - where the vaccines came from.
* A destination location - where the vaccines are going.
* A quantity.
* A distributor.
* A timestamp.

## Next Steps

Now that we have the base code for the blockchain there's serveral things you need to do.

* First, ***please*** branch the repo. We don't want to all be working off main.
* You need to figure out how we're actually going to make the blockchain persist (that is, how do we save the data). A flat JSON file is an option. We need to read this in every time the node starts.
* How are the nodes going to communicate? You will likely have to write some kind of protocol to do this. Remember, we discussed that all nodes are going to be aware of each other on our network so you don't really need to worry about picking "neighbours".
* The consensus model - how are nodes going to submit their blocks for evaluation by other nodes? We'll need to find a way to aggregate the number of vaccines in circulation and keep track of this (ie: our proof of stake mechanism). Remember the qty value in transactions - this will be helpful. This will be used to calculate a nodes "voting" power.
* Block interval. By time, or number of transactions? Have a play about.
* How are we going to handle if a shipment goes from Japan -> London (one transaction) and then from London -> Paris? Two options: a. Start a new transaction with a new ID, or b. Persist the shipment ID somehow.



Update on branch "Shivam"
- Changes on top of "Added help for implemented commands and fixed double instantiation of consensus" commit of "therring-working" branch
- Requires to install two programs:
-   https://www.rabbitmq.com/download.html
-   https://www.erlang.org/downloads
- And this installation from pip:
-   python -m pip install pika --upgrade

- Run each node in separate command prompt and change name of each node before running for better visibility
