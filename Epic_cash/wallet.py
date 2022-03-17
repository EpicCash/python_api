from datetime import datetime
from typing import Union
import time
import os

import password

from src.tools import normalize, get_system, icon
from src.transaction import Transaction
from src.wallet_config import Config
from src.api_manager import API


# //-- Example data --\\ #
owner_api_address_receiver = 'http://127.0.0.1:33420/v2/owner'
owner_api_address_sender = 'http://127.0.0.1:3420/v2/owner'

binary_path_receiver = 'C:\\epicpy_project\\Epic_cash\\epic-wallet'
binary_path_sender = 'C:\\epicpy_project\\Epic_cash\\epic-wallet2'

top_level_path_receiver = binary_path_receiver
top_level_path_sender = "C:\\Users\\IOPDG\\.epic\\main"
x = "C:\\Users\\IOPDG\\.epic\\main\\epic-wallet2.toml"
api_ports_sender = {'foreign': 3415, 'owner': 3420}
api_ports_receiver = {'foreign': 33415, 'owner': 33420}

password_ = 'majkut11'
node_url = 'https://fastepic.eu:3413'

destination2 = 'http://localhost:33415'
destination1 = 'https://fastepic.eu/keybaseid_blacktyg3r'
bitmart = 'http://42.192.85.182:3415'


class Wallet:
    """ Manage epic-wallet with Python"""

    def __init__(self, name: str):
        self.api = API()
        self.cfg = Config()
        self.name = name
        self.listener = None

    def load_settings(self, **kwargs) -> None:
        """Load settings from configuration file and/or set epic-wallet binary path"""
        if 'binary_path' in kwargs.keys():
            self.api.load_settings(binary_path=kwargs['binary_path'])
            # print(f'binary_path successfully loaded')

        if 'config_path' in kwargs.keys():
            self.cfg = Config(config_path=kwargs['config_path'])
            # print(kwargs['config_path'])
            try:
                self.api.load_settings(settings=self.cfg.settings)
                # print(f'config_path successfully loaded')
            except AttributeError:
                print(icon('error'), 'Wrong configuration file path')

    def update_settings(self, key: str, value: Union[str, int], category: str = 'wallet') -> None:
        """Update settings and save to configuration file"""
        self.cfg.save(key, value, category)

    def version(self) -> str:
        response = self.api.binary.version()
        if 'epic' in response.stdout:
            return f"\nSystem ver: {get_system()}" \
                   f"\nWallet ver: {response.stdout.split(' ')[-1]}"

    def create(self, **kwargs) -> None:
        """Create new wallet instance, new mnemonic/private key and wallet data"""
        path = self.api.binary.create_wallet(**kwargs)
        if path:
            self.load_settings(config_path=os.path.join(path, 'epic-wallet.toml'))
            print(self.cfg.settings['wallet']['data_file_dir'])

    def get_balance(self, password: str):
        balance = False
        owner_api = self.api.binary.start_owner_api(password=password)
        response = self.api.http.retrieve_summary_info()
        if response:
            balance = response['result']['Ok'][1]
            b_str = f"\nNODE HEIGHT: {balance['last_confirmed_height']}\n" \
                    f"----- BALANCE -----\n" \
                    f"{icon('success')} SPENDABLE: {normalize(balance['amount_currently_spendable'])}\n"\
                    f"{icon('info')} WAITING CONFIRMATION: {normalize(balance['amount_awaiting_confirmation'])}\n" \
                    f"{icon('warning')} WAITING FINALIZATION: {normalize(balance['amount_awaiting_finalization'])}\n" \
                    f"{icon('error')} LOCKED: {normalize(balance['amount_locked'])}\n"\
                    f"{icon('info')} MINING: {normalize(balance['amount_immature'])}\n"

            print(b_str)

        self.api.binary.stop_listener(owner_api)
        return balance

    def start_listener(self, password: str) -> None:
        if not self.listener:
            self.listener = self.api.binary.start_listener(password=password)
        else:
            print(f"{icon('info')} Wallet listener already running, PID: {self.listener}")

    def stop_listener(self) -> None:
        try: self.api.binary.stop_listener(self.listener)
        except Exception: pass
        self.listener = None

    def get_transactions(self, password: str, length: int = 100) -> Union[list, dict]:
        transactions = []
        owner_api = self.api.binary.start_owner_api(password=password)
        response = self.api.http.retrieve_txs()
        if response:
            transactions = response['result']['Ok'][1]
            transactions.reverse()
            transactions = transactions[:length]

        self.api.binary.stop_listener(owner_api)
        return transactions[:length]

    def send_transaction(self,
                         transaction: Union[Transaction, dict],
                         password: str, account: str = None) -> Union[Transaction, bool]:
        if not isinstance(transaction, Transaction):
            try:
                transaction = Transaction(**transaction)
            except Exception as e:
                print(e)
                return False

        if self.api.binary.send(transaction=transaction, password=password, account=account):
            # For HTTP transaction return save updates to tx.data
            if 'http' in transaction.method:
                tx = self.get_transactions(password=password, length=1)
                transaction.data = tx
                transaction.executed = tx['creation_ts']

        return transaction

    def cancel_transaction(self, password: str, uuid: str = None,
                           id: Union[str, int] = None):
        if id:
            self.api.binary.cancel(password=password, id=id)
        elif uuid:
            self.api.binary.cancel(password=password, uuid=uuid)
        else:
            print(f"{icon('warning')} To cancel provide transaction ID or UUID")


# =====================


def spawn_wallet(name):
    # print(f"// RECEIVER WALLET SECTION //")
    wallet = Wallet(name=name)
    # print(f"{binary_path_sender}\\epic-wallet.toml")
    wallet.load_settings(
        config_path=f"{binary_path_receiver}\\epic-wallet.toml",
        binary_path=binary_path_receiver)
    wallet.update_settings('check_node_api_http_addr', node_url)
    wallet.update_settings('owner_api_listen_port', api_ports_receiver['owner'])
    wallet.update_settings('api_listen_interface', '127.0.0.1')
    wallet.update_settings('api_listen_port', api_ports_receiver['foreign'])
    return wallet


tx = Transaction(destination='babuu',
                 message='testing python',
                 created=datetime.now(),
                 amount=0.1, method='file')

w1 = spawn_wallet(name='sender')
# w1.send_transaction(tx, password_)
# time.sleep(5)
file = fr"C:\epicpy_project\Epic_cash\epic-wallet\babuu.tx"
# w1.api.binary.finalize(file_path=file, password=password_)
# print(w1.api.binary.info(node_address='https:128.0.0.1', account='dups', password=password_))
# w1.cancel_transaction(password=password_, uuid='d12df9b4-1ccd-4467-a716-d6f342994039')
w1.api.binary.txs(password=password_)
# w1.start_listener(password_)
# time.sleep(2)
# w1.api.binary.create_account('dusps', password_)


#
# batch = 20
# tx_height = 0
#
#
# while batch > 0:
#     height = int(w1.api.http.node_height()['result']['Ok']['height'])
#     print(f'tx height: {tx_height}, chain height: {height}')
#     if not tx_height or (height-tx_height) > 10:
#         w1.send_transaction(tx, password_)
#         w1.send_transaction(tx, password_)
#         w1.send_transaction(tx, password_)
#         batch -= 3
#         tx_height = height
#         print(f"{batch} transactions left")
#         w1.balance(password_)
#     else:
#         time.sleep(60)
