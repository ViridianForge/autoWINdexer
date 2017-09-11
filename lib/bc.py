#
# AutoWINdexer.py
# Author: Wayne "ViridianForge" Manselle
# Version 0.1
#
# Changelog:
# 0.1 - 08/05/17 -- Initial Creation
# 0.2 - 09/06/17 -- Noting that I got this working for scraping new releases, etc and the whole album tear apart
#
#
# The AutoWINdexer is a script whose purpose is to scrape multiple musical services and
# collect data on the Genres of music that Chiptunes = WIN gives a shit about.
#
# Why? Because Wayne and Ryn have been doing this shit by hand for way too fucking long.
#
# Tons of credit to 59Naga at Github for their coffeescript BC scraper that Wayne read
# over to figure out how to do this in Python.
#
# Requirements:

from bs4 import BeautifulSoup
import requests

def bc_get_related_tags(dataLocs, relatedTags, queries):
    """
    Function that pulls together all the related tags from
    a list of primary tags for analysis.
    
    Parameters:
    ____________
    dataLocs - URLS to scan
    relatedTags - The list of related tags to be assembled
    queries - The specific tags to search for
    """

    #Begin by querying the main location for target URLs
    for url in dataLocs:
        for query in queries:
            sourceData = requests.get(url + query + '?page=1&sort_field=pop')
            #Load the target URL's text data
            txData = sourceData.text
            soup = BeautifulSoup(txData,"html.parser")

            rTags = soup.find_all("a", class_="related_tag")
            #Recursively scan down related tags
            for tag in rTags:
                if not tag in relatedTags:
                    relatedTags.append(tag.text)

    return relatedTags

def bc_get_genre(dataLocs, albumURLs, queries, depth):
    """
    Function that pulls together all the data from a query
    
    The goal of this function is to grab all relevant data from the list
    of services given, for the list of tags given.

    Parameters
    ----------
    dataLocs : the Data Locations to query for data
    queries: the queries to run on each dataLocations
    options: any options to modify the queries with
    depth: how deeply to track down albums from related tags, if at all
    """

    for url in dataLocs:
        for query in queries:
            curPageURLs = []
            for page in range(1,10):
                #Begin by querying the main location for target URLs
                sourceData = requests.get(url + query + '?page='+ str(page) + '&sort_field=pop')
                #Load the target URL's text data
                txData = sourceData.text
                soup = BeautifulSoup(txData,"html.parser")
                #Pop down into related tags if we want to
                if page==1 and depth > 0:
                    rTags = soup.find_all("a", class_="related_tag")
                    #Recursively scan down related tags
                    if depth > 0:
                        tags = []
                        for tag in rTags:
                            tags.append(tag.text)
                        collateAlbums(dataLocs, albumURLs, tags, depth -1)
                
                albumElems = soup.find_all("li", class_=["item", "item_end"])
                
                #Todo - can probably make this a list comprehension
                #Add all album URLs not already added
                for album in albumElems:
                    albumURL = album.find("a").get("href")
                    if not albumURL in albumURLs:
                        albumURLs.append(album.find("a").get("href"))
    #Return the awesome stuff
    return albumURLs

def bc_get_discog(urls):
    """
    Function to return the total list of albums
    and tracks from an artist's bandcamp webpage

    Parameters:
        urls - list of URLs to scrape
    """
    discog = []

    for url in urls:
        sourceData = requests.get(url)
        txData = sourceData.text
        soup = BeautifulSoup(txData, "html.parser")
    
        discElems = soup.find_all("li", class_=["music-grid-item"])

        for disc in discElems:
            discURL = url + disc.find("a").get("href")
            discog.append(discURL)

    return discog

def bc_get_album(albumURL, fields):
    """
    Function that pulls the relevant fields that we care about from an Album's website.

    Parameters
    _________
    albumURL: the URL to scrape for album data
    fields: the Fields to scrape for, provided they exist
    """
    
    sourceData = requests.get(albumURL)
    txtData = sourceData.text
    soup = BeautifulSoup(txtData, "html.parser")

    albumData = {}

    if "tracks" in fields:
        #Pull track data here
        trackList = soup.find_all("tr", class_=["track_row_view"])
        trackData = []
        for track in trackList:
            curTrack = {}
            curTrack['number'] = track.find("div", class_=["track_number"]).text
            curTrack['name'] = track.find("span", itemprop=["name"]).text
            curTrack['lyrics'] = ''
            if track.find("span", class_=["time"]):
                duration = track.find("span", class_=["time"]).text
                curTrack['duration'] = duration.strip()
            trackData.append(curTrack)
        
        albumData['tracks'] = trackData
        
    if "artist" in fields:
        #Pull artist data here
        artistData = soup.find("span", itemprop=["byArtist"])
        if artistData.find("a").text:
            albumData['artist'] = artistData.find("a").text

    if "release" in fields:
        #Pull release date here
        releaseDate = soup.find('meta',itemprop=['datePublished'])
        if releaseDate['content']:
            albumData['release']=releaseDate['content']

    if "tags" in fields:
        #Pull album tags here
        alTagElems = soup.find_all("a", class_=["tag"])
        tags = []
        for tag in alTagElems:
            tags.append(tag.text)
        albumData['tags'] = tags

    return albumData
