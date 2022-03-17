from log_symbols import LogSymbols
import subprocess
import platform
import psutil
import os

# Hide CMD windows while using subprocess

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def icon(type_: str):
    return eval(f"LogSymbols.{type_.upper()}.value")

def get_system():
    return f"{platform.system()} {platform.release()}"

def normalize(value, dec=8):
    try:
        if not isinstance(value, int):
            value = int(value)
        return value / 10 ** dec
    except Exception:
        return value


def manage_cwd(func):
    # Save current CWD
    cwd = os.getcwd()

    def wrapper(*args, **kwargs):
        # Change CWD to directory right directory
        os.chdir(args[0].binary_path)
        return func(*args, **kwargs)

    # Change CWD back to previous
    os.chdir(cwd)

    return wrapper


def kill_process(process):
    if isinstance(process, psutil.Process):
        try:
            process.kill()
            # return print(f"(PID:{process.ppid()}) {process.name()} is closed")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as er:
            # print(er)
            pass
    else:
        for proc in psutil.process_iter():
            if (str(process) in proc.name()) \
                or (str(proc.pid) in str(process)):
                try:
                    proc.kill()
                    # print(f"(PID:{proc.ppid()}) {proc.name()} is closed")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as er:
                    # print(er)
                    continue

