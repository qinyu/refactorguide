

def set_layers(layers):
    global LAYERS
    LAYERS = layers


def set_logic_packages(logic_packages):
    global LOGIC_PACKAGES
    LOGIC_PACKAGES = logic_packages


def set_smells(smells):
    global SMELLS
    SMELLS = smells


def init():
    set_layers({})
    set_logic_packages({})
    set_smells([])
