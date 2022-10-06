
def find_class_from_module(module, parent_class, has_attributes=[]):
    results = []
    for i in dir(module):
        # print('module', module, 'class', i, 'has_attributes', has_attributes)
        x = getattr(module, i)
        if isinstance(x, type) and issubclass(x, parent_class):
            if has_attributes:
                bypass = False
                for attr in has_attributes:
                    if not hasattr(x, attr) or not getattr(x, attr):
                        # print('\tbypass ', x, hasattr(x, attr), f'get {attr}', getattr(x, attr))
                        bypass = True
                        break
                if not bypass:
                    results.append(x)
            else:
                results.append(x)
    return results
