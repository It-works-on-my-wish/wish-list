from app.state.concrete_state_purchased import ConcreteStatePurchased
from app.state.state import State

class ConcreteStatePending(State):
    def getPrice(self) -> float:
        return 10.0 # to be replaced with actual price retrieval logic

    def getStateName(self) -> str:
        return "pending"
