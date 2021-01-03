global LAYER_UNKNOWN
LAYER_UNKNOWN = 'unknown'


class Design(object):
    def __init__(self, layers, smells) -> None:
        self.layers = layers
        self.smells = smells
        super().__init__()
