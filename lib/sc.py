"""
Actual documentation should go here
"""

from bs4 import BeautifulSoup
import requests

def sc_get_genre(query):

    sourceData = requests.get('https://soundcloud.com/tags/' + query)
    txData = sourceData.text
    soup = BeautifulSoup(txData, "html.parser")


    return True

