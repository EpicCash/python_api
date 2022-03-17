from typing import Union
import subprocess
import time
import os

from log_symbols import LogSymbols
from halo import Halo

from . import tools


class BINARY_API:
    """Python wrapper for Epic-Cash CLI Wallet using epic-wallet binary file"""
    binary_file = 'epic-wallet.exe'
    spinner = Halo(text='', spinner='growVertical')

    def __init__(self, settings: dict = None, binary_path: str = None):
        self.binary_path = binary_path
        self.settings = settings

        self.check_node_api_http_addr: str = ''
        self.owner_api_listen_port: Union[str, int] = 0
        self.api_listen_port: Union[str, int] = 0
        self.top_level_path: str = ''
        self.binary: str = ''

        if self.settings:
            self.load_settings(self.settings)
        else:
            print(f"\nPlease provide path to your epic-wallet.toml config file")

        if self.binary_path:
            self.load_binary_path(self.binary_path)
        else:
            print(f"Please provide path to your epic-wallet CLI binary file\n")

    def load_settings(self, settings):
        """Load settings from TOML configuration file"""
        self.settings = settings
        self.check_node_api_http_addr: str = settings['wallet']['check_node_api_http_addr']
        self.owner_api_listen_port = settings['wallet']['owner_api_listen_port']
        self.top_level_path: str = os.path.dirname(settings['wallet']['data_file_dir'])
        self.api_listen_port = settings['wallet']['api_listen_port']

    def load_binary_path(self, binary_path):
        """Load path to epic-wallet binary file"""
        self.binary_path = binary_path
        self.binary = os.path.join(self.binary_path, self.binary_file)

    # command: str, password: str, cwd=None,
    # extra_args: list = None, account: str = None,

    @tools.manage_cwd
    def _command(self, **kwargs):
        """Prepare epic-wallet binary command-line commands and execute via subprocess.run()"""
        cwd = kwargs['cwd'] if 'cwd' in kwargs.keys() else os.getcwd()
        args = [self.binary]
        cut_print = 5

        if 'account' in kwargs.keys():
            cut_print += 2 if kwargs['account'] else 0  # to remove sensitive data from stdout
            args += ['-a', kwargs['account']] if kwargs['account'] else []

        if 'node_address' in kwargs.keys():
            args += ['-r', kwargs['node_address']]
        else:
            args += ['-r', self.check_node_api_http_addr]

        args += ['-p', kwargs['password'], kwargs['command']]
        args += kwargs['extra_args'] if 'extra_args' in kwargs.keys() else []

        args = [str(arg) for arg in args]
        string_cmd = f'Command: {" ".join(c for c in args[cut_print:])}'
        print(string_cmd)
        # print(args)
        self.spinner.start(text=f" working...")
        process = subprocess.run(args, capture_output=True, text=True, cwd=cwd)

        return process

    @tools.manage_cwd
    def _create(self, **kwargs):
        extra_args = ['-h']
        if 'wallet_data_path' not in kwargs.keys():
            kwargs['wallet_data_path'] = os.getcwd()

        if 'password' not in kwargs.keys():
            print(f'{tools.icon("warning")} Please provide password to secure your wallet')
            return

        if 'short_wordlist' in kwargs.keys():
            if kwargs['short_wordlist']:
                extra_args += ['-s', '--short_wordlist']

        output = self._command(command='init',
                               extra_args=extra_args,
                               password=kwargs['password'],
                               cwd=kwargs['wallet_data_path'])

        if 'completed successfully' in output.stdout:
            mnemonic = output.stdout.split('Your recovery phrase is:')[1]
            mnemonic = mnemonic.split('Please back-up these words in a non-digital format.')[0]
            mnemonic = mnemonic.strip()
            print(tools.icon('success'), 'Wallet created successfully!\n'
                                         f'{tools.icon("success")}'
                                         'Please backup your MNEMONIC SEED PHRASE:\n'
                                         f'\n{mnemonic}\n')
            return kwargs['wallet_data_path']

        elif 'already exists' in output.stderr:
            print(tools.icon('warning'), ' Wallet already exists in this directory')

        else:
            print(tools.icon('error'), output.stderr)

    @tools.manage_cwd
    def _run_listener(self, **kwargs):
        # TODO: Handlers for Keybase and TOR listeners/API
        port = self.api_listen_port
        type_ = 'Foreign'
        command = 'listen'

        if 'owner' in kwargs.keys():
            port = self.owner_api_listen_port
            type_ = 'Owner'
            command = 'owner_api'

        self.spinner.start(text=f"")
        args = [self.binary,
                '-p', kwargs['password'],
                '-r', self.check_node_api_http_addr,
                command]
        time.sleep(0.2)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.spinner.stop_and_persist(
            tools.icon('success'),
            f'{type_} API on port {port} running (PID: {process.pid})')

        return process.pid

    def create_wallet(self, **kwargs):
        """Create new wallet instance"""
        return self._create(**kwargs)

    def stop_listener(self, process=None):
        """Specify psutil.Process to kill, if process=None kill all binary file processes"""
        try:
            if process:
                tools.kill_process(process=process)
                print(f"{LogSymbols.INFO.value} BINARY_API: STOP API LISTENER (PID: {process})")
            else:
                print(f"{LogSymbols.INFO.value} BINARY_API: STOPPING all {self.binary_file} processes")
                tools.kill_process(process=self.binary_file)
        except Exception:
            pass

    def start_listener(self, password):
        """Run wallet foreign_api/listener, background process"""
        return self._run_listener(password=password)

    def start_owner_api(self, password):
        """Run wallet owner_api, background process"""
        return self._run_listener(password=password, owner=True)

    def version(self, password=''):
        """Check wallet version"""
        return self._command(command='--version', password=password)

    def info(self, **kwargs) -> None:
        """Return wallet balance"""
        process = self._command(command='info', **kwargs)
        if 'successfully' in process.stdout:
            self.spinner.stop_and_persist(tools.icon('success'), process.stdout)
        else:
            self.spinner.stop_and_persist(tools.icon('error'), process.stdout)

    def txs(self, **kwargs) -> None:
        """Return wallet transaction history"""
        process = self._command(command='txs', **kwargs)
        if 'successfully' in process.stdout:
            success_msg = "Command 'txs' completed successfully"
            self.spinner.stop()
            print(process.stdout.replace(success_msg, '').strip())
            print(f"{tools.icon('success')} {success_msg}")
        else:
            self.spinner.stop_and_persist(tools.icon('error'), process.stdout)

    def send(self, **kwargs):
        """Send Epic-Cash via different methods"""
        tx = kwargs['transaction']
        assert (tx.validate())

        kwargs['extra_args'] = ['-m', tx.method,
                                '-d', tx.destination,
                                '-s', tx.strategy,
                                tx.amount,
                                '-g', tx.message]

        process = self._command(command='send', **kwargs)

        if 'successfully' in process.stdout:
            # Response for success HTTP method
            if 'http' in tx.method:
                self.spinner.stop_and_persist(
                    tools.icon('success'),
                    'Transaction sent successfully!')
                return tx

            # Response for success FILE method
            elif 'file' in tx.method:
                self.spinner.stop_and_persist(
                    tools.icon('success'),
                    f'Transaction file "{tx.destination}" successfully created!')
                return tx

        # Response with error during the process
        else:
            self.spinner.stop_and_persist(tools.icon('error'), 'Transaction Failed!')
            if 'os error 10061' in process.stdout:
                print(tools.icon('error'), f'{tx.destination} is not responding')
            elif 'I/O error' in process.stdout:
                print(tools.icon('error'), f'Invalid transaction file name')
            else:
                print(tools.icon('error'), process.stdout)
        return False

    def receive(self, **kwargs) -> None:
        """Load sender's transaction file, sign it and produce new response file"""
        if os.path.isfile(kwargs['file_path']):
            kwargs['extra_args'] = ['-i', kwargs['file_path']]

            process = self._command(command='receive', **kwargs)

            if 'successfully' in process.stdout:
                self.spinner.stop_and_persist(
                    tools.icon('success'), f'Transaction signed successfully!')
                print(f'{tools.icon("info")} Please send "{kwargs["file_path"]}.response" file back to sender.')

            else:
                self.spinner.stop_and_persist(tools.icon('error'), 'Receiving Failed!')
                print(tools.icon('error'), process.stdout)
        else:
            print(tools.icon('error'), f'"{kwargs["file_path"]}" file does not exists!')

    def finalize(self, **kwargs) -> None:
        """Load receiver's transaction response file, sign it and send transaction to network"""
        if os.path.isfile(kwargs['file_path']):
            kwargs['extra_args'] = ['-i', kwargs['file_path']]

            process = self._command(command='finalize', **kwargs)

            if 'successfully' in process.stdout:
                self.spinner.stop_and_persist(tools.icon('success'), f'Transaction finalized and send successfully!')

            else:
                self.spinner.stop_and_persist(tools.icon('error'), 'Finalization Failed!')
                print(tools.icon('error'), process.stdout)
        else:
            print(tools.icon('error'), f'"{kwargs["file_path"]}" file does not exists!')

    def cancel(self, **kwargs):
        """Cancel transaction with given id from 'txs' or tx-UUID"""
        if 'id' in kwargs.keys():
            kwargs['extra_args'] = ['-i', kwargs['id']]

        if 'uuid' in kwargs.keys():
            kwargs['extra_args'] = ['-t', kwargs['uuid']]

        process = self._command(command='cancel', **kwargs)

        if 'successfully' in process.stdout:
            self.spinner.stop_and_persist(tools.icon('success'),
                                          f'Transaction "{kwargs["extra_args"][-1]}" canceled successfully!')
        else:
            self.spinner.stop_and_persist(tools.icon('error'), process.stdout)

    def create_account(self, **kwargs) -> None:
        """Create account, "subwallet", different balances and public keys but one master seed"""
        kwargs['extra_args'] = ['-c', kwargs['name']]
        process = self._command(command='account', **kwargs)

        if 'successfully' in process.stdout:
            self.spinner.stop_and_persist(tools.icon('success'),
                                          f'Account "{kwargs["name"]}" created successfully!')
        else:
            self.spinner.stop_and_persist(tools.icon('error'), process.stdout)

    def check(self, **kwargs):
        """
        Scans the entire UTXO set from the node, identify which outputs belong to the given
        wallet update the wallet state to be consistent with what's currently in the UTXO set.
        """
        print(tools.icon('info'), f"Scanning blockchain's UTXO's - may take up to 10 minutes")
        process = self._command(command='check', **kwargs)

        if 'successfully' in process.stdout:
            success_msg = "Command 'check' completed successfully"
            self.spinner.stop()
            print(process.stdout.replace(success_msg, '').strip())
            print(f"{tools.icon('success')} {success_msg}")
        else:
            self.spinner.stop_and_persist(tools.icon('error'), process.stdout)

    def outputs(self, **kwargs):
        """
        Returns a list of outputs from the active account in the wallet.
        """
        process = self._command(command='outputs', **kwargs)

        if 'successfully' in process.stdout:
            success_msg = "Command 'outputs' completed successfully"
            self.spinner.stop()
            print(process.stdout.replace(success_msg, '').strip())
            print(f"{tools.icon('success')} {success_msg}")
        else:
            self.spinner.stop_and_persist(tools.icon('error'), process.stdout.strip())

    def recover(self):
        """
        The recover command displays the existing wallet's 24 (or 12) word seed phrase.
        This will spawn nem console to provide seedphrase.
        """
        process = subprocess.Popen(['start', self.binary, 'recover'], shell=True)
        print(f"{tools.icon('info')} Continue recovery process in new console")

    def address(self, **kwargs):
        """for V3 API"""
        pass

    def invoice(self, **kwargs):
        """for V3 API"""
        pass

    def process_invoice(self, **kwargs):
        """for V3 API"""
        pass