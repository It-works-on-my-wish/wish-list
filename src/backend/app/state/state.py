from __future__ import annotations
from abc import ABC, abstractmethod
import context


class State(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """

    @property
    def context(self) -> context.Context:
        return self._context

    @context.setter
    def context(self, context: context.Context) -> None:
        self._context = context

    @abstractmethod
    def getPrice(self) -> float:
        pass

    @abstractmethod
    def getStateName(self) -> str:
        pass


"""
Concrete States implement various behaviors, associated with a state of the
Context.
"""
