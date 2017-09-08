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
import json

#Static Variables

#Default Datalocations
#This should be overridable by the user - BUT - these
#are the default locations to scan for Chiptunes=WIN purposes
#
#VF's notes:
# BANDCAMP
#bcFullArts -- Bandcamp's complete list of all artist *NOT LIMITED TO CHIP
#bcSearchQ -- Bandcamp's direct search capabilities. Syntax seems to be q?=<search term>
#bcTargQ -- Bandcamp's tag by tag hunts - the related tags section could be useful here. 
#bcTagsQ -- Full lists of tags and locations on Bandcamp
# SOUNDCLOUD
# TODO

dataLoc = {
    'bcFullArts': 'https://bandcamp.com/artist_index',
    'bcSearchQ': 'https://bandcamp.com/search',
    'bcTagQ': 'https://bandcamp.com/tag/',
    'bcTagsQ': 'https://bandcamp.com/tags'
}

#Functions
def collateRelatedTags(dataLocs, relatedTags, queries):
    """
    Function that pulls together all the related queries from
    a list of primary queries for analysis.
    Specific to Bandcamp
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

#Main driver here
def collateAlbums(dataLocs, albumURLs, queries, depth):
    """
    Function that pulls together all the data from a query
    
    The goal of this function is to grab all relevant data from the list
    of services given, for the list of tags given.

    Parameters
    ----------
    dataLocs : the Data Locations to query for data
    queries: the queries to run on each dataLocations
    options: any options to modify the queries with
    """

    for url in dataLocs:
        for query in queries:
            print(query)
            curPageURLs = []
            for page in range(1,10):
                #Begin by querying the main location for target URLs
                sourceData = requests.get(url + query + '?page='+ str(page) + '&sort_field=pop')
                #Load the target URL's text data
                txData = sourceData.text
                soup = BeautifulSoup(txData,"html.parser")
                #Grab what we need
                if page==1:
                    rTags = soup.find_all("a", class_="related_tag")
                    #Recursively scan down related tags
                    if depth >=1:
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

def collateAlbum(albumURL, fields):
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


'''
Main method documentation
'''
def main():
    #Input Grabber here Eventually
    #Logger here Eventually
    collatedTags = collateRelatedTags(['https://bandcamp.com/tag/'],[],['chiptune','vgm','nerdcore','synthwave'])
    print('Number of potential related tags found: ' + str(len(collatedTags)))
    with open('relatedTags.txt', 'w') as tagfile:
        for tag in collatedTags:
            tagfile.write(tag + '\n')
    result = collateAlbums(['https://bandcamp.com/tag/'],[],['chiptune','vgm','nerdcore','synthwave','gameboy','lsdj'],0)
    diveResult = {}
    print("Number of Albums Found: " + str(len(result)))
    for res in result:
        diveResult[res] = collateAlbum(res, ['tracks','artist','release','tags'])
    #Save the results to json file
    with open('albumDive.json', 'w') as outfile:
        json.dump(diveResult, outfile)
    print("Done.")
    return 0

if __name__ == '__main__':
    main()

