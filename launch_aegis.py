import sys
import os
import signal
import atexit

AEGIS_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.expanduser("~/.aegis.pid")

def _already_running() -> bool:
    if not os.path.exists(LOCK_FILE):
        return False
    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())

        os.kill(pid, 0)

        with open(f"/proc/{pid}/cmdline", "r") as f:
            cmd = f.read()
            if "python" in cmd and "aegis" in cmd.lower():
                return True
    except (ProcessLookupError, ValueError, PermissionError, FileNotFoundError):
        pass

    try:
        os.unlink(LOCK_FILE)
    except:
        pass
    return False

def _write_lock() -> None:
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def _remove_lock() -> None:
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            if pid == os.getpid():
                os.unlink(LOCK_FILE)
    except:
        pass

def main() -> None:
    if _already_running():
        sys.exit(0)

    _write_lock()
    atexit.register(_remove_lock)

    def _sighandler(sig, frame):
        _remove_lock()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _sighandler)
    signal.signal(signal.SIGINT,  _sighandler)

    if AEGIS_DIR not in sys.path:
        sys.path.insert(0, AEGIS_DIR)

    from aegis_engine import main as run_hud
    run_hud()

if __name__ == "__main__":
    main()
