import time

from stellar_sdk import Keypair, Network, SorobanServer, TransactionBuilder, scval
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.exceptions import PrepareTransactionException
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus

# TODO fill out config values
secret = "ASSET_ISSUER_PRIVATE_KEY"
contract_id = "CONTRACT_ID" 
contract_to_blacklist = "CONTRACT_ID_TO_BE_BLACKLISTED"

network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
soroban_server = SorobanServer("https://soroban-testnet.stellar.org:443")

kp = Keypair.from_secret(secret)
source = soroban_server.load_account(kp.public_key)


tx = (
    TransactionBuilder(source, network_passphrase, base_fee=100)
    .set_timeout(300)
    .append_invoke_contract_function_op(
        contract_id=contract_id,
        function_name="set_authorized",
        parameters=[scval.to_address(contract_to_blacklist), scval.to_bool(True)],
    )
    .build()
)
print(f"XDR: {tx.to_xdr()}")

try:
    tx = soroban_server.prepare_transaction(tx)
except PrepareTransactionException as e:
    print(f"Got exception: {e.simulate_transaction_response}")
    raise e

tx.sign(kp)
print(f"Signed XDR: {tx.to_xdr()}")

send_transaction_data = soroban_server.send_transaction(tx)
print(f"sent transaction: {send_transaction_data}")
if send_transaction_data.status != SendTransactionStatus.PENDING:
    raise Exception("send transaction failed")
while True:
    print("waiting for transaction to be confirmed...")
    get_transaction_data = soroban_server.get_transaction(send_transaction_data.hash)
    if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
        break
    time.sleep(3)

print(f"transaction: {get_transaction_data}")

if get_transaction_data.status == GetTransactionStatus.SUCCESS:
    assert get_transaction_data.result_meta_xdr is not None
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
        get_transaction_data.result_meta_xdr
    )
    result = transaction_meta.v3.soroban_meta.return_value  # type: ignore[union-attr]
    output = [x.sym.sc_symbol.decode() for x in result.vec.sc_vec]  # type: ignore
    print(f"transaction result: {output}")
else:
    print(f"Transaction failed: {get_transaction_data.result_xdr}")
