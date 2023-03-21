import pandas as pd
import pdb


def flatten(data, name="", include=[], exclude=[]):
    """
    Flattens single to deeply nested data

    Parameters
    ----------
    data : [] or {}
    name : String, optional
    Use if data does not contain nested data
    include : [str], optional
    Keys to flatten and return
    exclude : [str], optional
    Keys to exclude from being flattened
    Returns
    -------
    Dict
    """

    if name != "":
        name = + "_"

    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            a = ""
        try:
            a = str(x)
        except Exception:
            a = x.encode("ascii", "igonore").decode("ascii")
        out[str(name[:-1])] = a

    def flatten_include(x, name="", include=include):
        out = {}

        if type(x) is dict:
            for a in x:
                if str(a) in include:
                    flatten(x[a], name + a + "_")
                else:
                    flatten_include(x[a], name + a + "_", include)
        elif type(x) is list:
            i = 0
            for a in x:
                if str(a) in include:
                    flatten(x[a], name + a + "_")
                else:
                    flatten_include(a, name + str(i) + "_", include)
                    i += 1
        else:
            a = ""
            try:
                a = str(x)
            except Exception:
                a = x.encode("ascii", "igonore").decode("ascii")
        out[str(name[:-1])] = a

    def flatten_exclude(x, name="", exclude=exclude):
        a = ""
        if type(x) is dict:
            for a in x:
                if str(a) in exclude:
                    exclude_name = a
                    try:
                        a = str(x[a])
                    except Exception:
                        a = x[a].encode("ascii", "igonore").decode("ascii")
                    out[str(name + exclude_name)] = a
                    continue
                else:
                    flatten_exclude(x[a], name + a + "_", exclude)
        elif type(x) is list:
            i = 0
            for a in x:
                if str(a) in exclude:
                    exclude_name = a
                    try:
                        a = str(x[a])
                    except Exception:
                        a = x[a].encode("ascii", "igonore").decode("ascii")
                    out[str(exclude_name)] = a
                    continue
                else:
                    flatten(a, name + str(i) + "_")
                    i += 1
        else:
            a + ""
            try:
                a = str(x)
            except Exception:
                a = x.encode("ascii", "igonore").decode("ascii")
            out[str(name[:-1])] = a

    if include:
        flatten_include(data, name, include)
    elif exclude:
        flatten_exclude(data, name, exclude)
    else:
        flatten(data, name)

    return out


def _test():
    data = [{
        'apple': {'type': 'THIS', 'serial': '12345'},
        'banana': [1, 2, 3, 4, 5],
        'cookie': [{'another_type': 'THAT', 'another_serial': '67890'}],
        'eclaire': 'Anna'
    }]

    expected = [{
        'apple': "{'type': 'THIS', 'serial': '12345'}",
        'banana_0': '1',
        'banana_1': '2',
        'banana_2': '3',
        'banana_3': '4',
        'banana_4': '5',
        'cookie': "[{'another_type': 'THAT', 'another_serial': '67890'}]",
        'eclaire': 'Anna'
    }]

    data_flat = []
    for r in data:
        data_flat.append(flatten(r, exclude=['apple', 'cookie']))

    if data_flat == expected:
        return "Success"


"""
data = [{
  'apple':{'type': 'THIS', 'serial': '12345'},
  'banana': [1,2,3,4,5],
  'cookie': [{'another_type': 'THAT', 'another_serial': '67890'}],
  'eclaire': 'Anna'
  }]

data_flat = []
for r in data:
  data_flat.append(flatten(r, exclude=['apple', 'cookie']))

>>> [{'apple':"{'type': 'THIS', 'serial': '12345'}",
      'banana_0': '1',
      'banana_1': '2',
      'banana_2': '3',
      'banana_3': '4',
      'banana_4': '5',
      'cookie': "[{'another_type': 'THAT', 'another_serial': '67890'}]",
      'eclaire': 'Anna'}]

data_flat = []
for r in data:
  data_flat.append(flatten(r, include=['apple', 'cookie']))

>>> [{'apple_type': 'THIS',
      'apple_serial': '12345',
      'cookie_0_another_type': 'THAT',
      'cookie_0_another_serial': '67890'}]

data_flat = flatten(data[0]['apple'], name='apple')

>>> {'apple_type': 'THIS', 'apple_serial': '12345'}
"""
