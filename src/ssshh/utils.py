import os
import psutil


def is_iterm() -> bool:
    if os.environ.get("TERM_PROGRAM") == "iTerm.app":
        return True

    for key in ("ITERM_SESSION_ID", "ITERM_PROFILE", "ITERM2_SESSION_ID"):
        if key in os.environ:
            return True
    
    try:
        parent = psutil.Process().parent()
        while parent:
            if "iTerm" in parent.name():
                return True
            parent = parent.parent()
    except Exception:
        pass

    return False

def is_vscode_available() -> bool:
    return os.system("which code > /dev/null 2>&1") == 0
