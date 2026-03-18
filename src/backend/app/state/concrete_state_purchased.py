from app.state.state import State

class ConcreteStatePurchased(State):
    def getPrice(self) -> float:
        return 20.0 # to be replaced with actual price retrieval logic for purchased state

    def getStateName(self) -> str:
        return "purchased"
