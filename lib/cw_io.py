"""
    This library is a collection of IO utilities
    for use with the autoWINDexer utilities.

    The ultimate goal with this library is to contain
    a method for each popular IO method.
"""
import json
import csv

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

def cw_delim(data, opts):
    """
    Generic Delimited Text Output
    Print out data to file in opt[0]
    Default to csv, quoted with | and quote minimal behavior

    Parameters:
    ________________________
    data: The data to output
    opts: Options to pass to function
    opt[0]: Filename to write to
    opt[1]: File mode
    opt[2]: Delimiter to use in output - defaults to ,
    opt[3]: Quote character to surrounded delimited strings - defaults to |
    opt[4]: Quoting Behavior constant - defaults to minimal
    """
    delim = opts[2] or ","
    quote = opts[3] or "|"
    quotopt = opts[4] or csv.QUOTE_MINIMAL
    try:
        with open(opts[0], opts[1]) as outfile:
            cw_writer = csv.writer(outfile, delimiter=delim, quotechar=quote, quoting=quotopt)
            for row in data:
                cw_writer.writerow(row)
    except:
        print("Unexpected error:", sys.exc_info()[0])

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
