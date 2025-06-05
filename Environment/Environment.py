class Environment:
    def __init__(self, other=None):
        if other is None:
            self.prev = None  # Pointer to the previous environment
            self.name = "env0"  # Default name
            self.boundVar = {}  # Map of bound variables to their values
        else:
            self.prev = other.prev
            self.name = other.name
            self.boundVar = other.boundVar.copy()