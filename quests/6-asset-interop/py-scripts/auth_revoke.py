from stellar_sdk import Keypair, Network, Server, TransactionBuilder, AuthorizationFlag
from stellar_sdk.exceptions import BaseHorizonError

# Configure Stellar SDK to talk to the horizon instance hosted by Stellar.org
# To use the live network, set the hostname to 'https://horizon.stellar.org'
secret = "PRIVATE_KEY" # TODO fill out 
# Use the test network, if you want to use the live network, please set it to `Network.PUBLIC_NETWORK_PASSPHRASE`
server = Server(horizon_url="https://horizon-testnet.stellar.org")
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

# Keys for accounts to issue and receive the new asset
issuing_keypair = Keypair.from_secret(secret)
issuing_public = issuing_keypair.public_key

# Transactions require a valid sequence number that is specific to this account.
# We can fetch the current sequence number for the source account from Horizon.
issuing_account = server.load_account(issuing_public)

transaction = (
    TransactionBuilder(
        source_account=issuing_account,
        network_passphrase=network_passphrase,
        base_fee=100,
    )
    .append_set_options_op(
        set_flags=AuthorizationFlag.AUTHORIZATION_REVOCABLE
    )
    .build()
)
transaction.sign(issuing_keypair)
try:
    transaction_resp = server.submit_transaction(transaction)
    print(f"Transaction Resp:\n{transaction_resp}")
except BaseHorizonError as e:
    print(f"Error: {e}")