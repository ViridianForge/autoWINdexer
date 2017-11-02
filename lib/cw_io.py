"""
    This library is a collection of IO utilities
    for use with the autoWINDexer utilities.

    The ultimate goal with this library is to contain
    a method for each popular IO method.
"""
import json


def cw_out(func, data, opts):
    """
    This catch-all method is a shell for the built-in CLI.
    It will pass-through data and options to the selected 
    format of output.

    Parameters:
    ________________________
    
    fmt: The Output method to pass-through to
    data: The data to output
    opts: The options to pass-through to the called method

    """
    try:
        func(data,opts)
    except:
        print("Unexpected error:", sys.exc_info()[0])

def cw_csv(data, opts):
    return 0

def cw_json(data, opts):
    """
    Method that dumps the passed data into a json file.

    Parameters:
    _____________________
    
    data: The data output
    opts: Array of options to control the function
    """
    with open(opts[0], opts[1]) as outfile:
        json.dump(data, outfile)
    return

def cw_txt(data, opts):
    return 0

def cw_mysql(data, opts):
    return 0
