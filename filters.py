def filter_interested_modules(module_dict, module_packages):
    _m_dict = {}
    for m in module_packages.keys():
        if m in module_dict.keys():
            _m_dict[m] = module_dict[m]
        else:
            print("Warning: interested module missed %s" % m)
    return _m_dict


def filter_interested_packages(module_dict, module_packages):
    _m_dict = {}
    for m in module_packages.keys():
        _p_dict = {}
        if m in module_dict.keys():
            for p in module_packages[m]:
                if p in module_dict[m].keys():
                    _p_dict[p] = module_dict[m][p]
                else:
                    print("Warning: interested pacakge missed %s:%s" % (m, p))
            _m_dict[m] = _p_dict
        else:
            print("Warning: interested module missed %s" % m)
    return _m_dict
