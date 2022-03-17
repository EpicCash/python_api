from typing import Union

from requests.auth import HTTPBasicAuth
from log_symbols import LogSymbols
from halo import Halo
import requests

from . import api_calls_args


class HTTP_APIv2:
    """Manage epic-wallet through HTTP API v2"""
    owner_endpoints = ['accounts', 'create_account_path', 'set_active_account',
                       'retrieve_outputs', 'retrieve_txs', 'retrieve_summary_info',
                       'init_send_tx', 'issue_invoice_tx', 'node_height',
                       'process_invoice_tx']

    owner_endpoints_params = [
        # [],  # accounts
        # ['account_label'],  # create_account_path [new_account_name]
        # ['blacktyg3r'],  # set_active_account [existing_account_name]
        # [False, True, None],  # retrieve_outputs [include_spent, refresh, tx_id]
        # [True, None, None],  # retrieve_txs [refresh, tx_id, tx_slate_id]
        # [True, 10],  # retrieve_summary_info [refresh, minimum_conf]
        [api_calls_args.tx_args],  # init_send_tx [transaction args]
        [api_calls_args.invoice_args],  # issue_invoice_tx [invoice_args]
        # [],  # node_height
        # [api_calls_args.process_invoice_tx_args],  # process_invoice_tx [process_invoice_tx_args
        ]

    spinner = Halo(text='Downloading transactions', spinner='growVertical')

    def __init__(self, settings: dict = None):
        self.settings = settings

        if not self.settings:
            print(f"\nPlease provide path to your epic-wallet.toml config file")

    def _owner_api_call(self, method: str, params: Union[dict, list]):
        """Base function to make owner_api POST calls"""
        self.spinner.start(text=f"HTTPAPIv2: call {method} ...")

        # Read settings from TOML file
        api_secret_path = self.settings['wallet']['api_secret_path']
        password = open(api_secret_path).read().strip()
        username = 'epic'
        address = self.settings['wallet']['api_listen_interface']
        port = self.settings['wallet']['owner_api_listen_port']
        url = f"http://{address}:{port}/v2/owner"
        # Prepare auth for API POST call
        auth = HTTPBasicAuth(username=username, password=password)

        # Prepare JSON payload for API POST call
        json = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        try:
            response = requests.post(url, auth=auth, json=json).json()
        except requests.exceptions.ConnectionError:
            self.spinner.stop_and_persist(LogSymbols.ERROR.value,
                                          f'HTTPAPIv2: {address}:{port} is not responding (node/listener offline)')
            return False

        if 'error' in response.keys():
            code = response['error']['code']
            msg = response['error']['message']
            self.spinner.stop_and_persist(LogSymbols.ERROR.value, f'HTTPAPIv2: {method} ERROR [CODE: {code}]: {msg}')
            return False

        elif 'Err' in response['result'].keys():
            code = -999
            msg = response['result']['Err']
            self.spinner.stop_and_persist(LogSymbols.ERROR.value, f'HTTPAPIv2: {method} ERROR [CODE: {code}]: {msg}')
            return False

        self.spinner.stop_and_persist(LogSymbols.SUCCESS.value, f'HTTPAPIv2: call {method} finished')
        return response

    @staticmethod
    def _update_params(default, params):
        """Update params provided to call"""
        for key, value in params.items():
            default[key] = value
        return default

    def accounts(self, **params):
        # TODO: displaying accounts logic
        end_point = 'accounts'
        default = {}
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

    def create_account_path(self, **params):
        # TODO: displaying accounts logic
        end_point = 'create_account_path'
        default = {'label': 'default'}
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

    def set_active_account(self, **params):
        end_point = 'set_active_account'
        default = {'label': 'default'}
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

    def retrieve_outputs(self, **params):
        end_point = 'retrieve_outputs'
        default = {
            "include_spent": False,
            "refresh_from_node": True,
            "tx_id": None
            }
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

    def retrieve_txs(self, **params):
        end_point = 'retrieve_txs'
        default = {
            "refresh_from_node": True,
            "tx_id": None,
            "tx_slate_id": None
            }
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

    def retrieve_summary_info(self, **params):
        end_point = 'retrieve_summary_info'
        default = {
            "refresh_from_node": True,
            "minimum_confirmations": 10
            }
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

    def init_send_tx(self):
        return self._owner_api_call(method=self.owner_endpoints[6],
                                    params=self.owner_endpoints_params[6])

    def issue_invoice_tx(self):
        return self._owner_api_call(method=self.owner_endpoints[7],
                                    params=self.owner_endpoints_params[7])

    def node_height(self, **params):
        end_point = 'node_height'
        default = {}
        params = self._update_params(default, params)
        return self._owner_api_call(method=end_point, params=params)

