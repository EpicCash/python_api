from typing import Union
import os

from src.tools import normalize, get_system, icon
from src.transaction import Transaction
from src.wallet_config import Config
from src.api_manager import API


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

