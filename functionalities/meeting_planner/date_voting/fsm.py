import enum
from abc import ABC, abstractmethod
from typing import Dict

from .states import VOTE_STATE_NAME


class VoteException(Exception):
    pass

class StateNotReady(VoteException):
    """
    Exception raised when current state of voute FSM
    reports that it's not ready to move futher
    """
    def __init__(self, state: VOTE_STATE_NAME, message: str =""):
        self.message = f"state {state} is not ready because of reason: '{message}'"
        super().__init__(self.message)

class VoteProcessIsDone(VoteException):
    pass

class ProsOfVoteStateInvalid(VoteException):
    pass


class VoteState(ABC):
    name: VOTE_STATE_NAME
    state_properties: Dict

    @abstractmethod
    def count_next_state(self) -> VoteState:
        ...

    @abstractmethod
    def validate_props(self) -> None:
        ...

    @abstractmethod
    def collect_more_data(self) -> None:
        ...

class VoteFSM:
    state: VoteState

    def move_next(self) -> None:
        try:
            self.state.validate_props()
            self.state = self.state.count_next_state()
        except StateNotReady:
            self.state.collect_more_data()
