from enum import Enum

from InquirerPy.base.control import Choice

from .utils import is_iterm

class Session(Enum):
    TMUX_ITERM2 = "tmux -CC -u new -A -s main"
    TMUX = "tmux new -A -s main"
    SSH = "/bin/bash"


def get_session_choices(is_tmux_available: bool) -> list[Choice]:
    session_choices = [
        Choice(
            value=Session.SSH.value, 
            name="ssh session without tmux (default shell)"
        ),
    ]
    if is_tmux_available:
        session_choices.append(
            Choice(
                value=Session.TMUX.value, 
                name="use tmux (tmux)"
            )
        )
    if is_iterm():
        session_choices.append(
            Choice(
                value=Session.TMUX_ITERM2.value, 
                name="use tmux with iterm2 integration (tmux -CC)"
            )
        )   
    return session_choices