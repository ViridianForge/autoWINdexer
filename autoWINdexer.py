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
import argparse
import logging

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
# Split controls into their own script
# This file should only be for BC_related scraping tools

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

def get_bc_discography(urls):
    """
    Function to return the total list of albums
    and tracks from an artist's bandcamp webpage

    Parameters:
        urls - list of URLs to scrape
    """

    return []

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


def main(stype, sterms, url, outputs, depth=None):
    '''
    Generic main method
    Purpose is to select the specific mode of operation using
    input and then run a scrape in that fashion

    Parameters
    __________
    stype - String describing the specific type of search being done
    sterms - List of strings describing tags or terms to be used in the search
    urls - List of URLs to be searched on
    outputs - List of Files to output to
    depth - Level of recursion if set
    '''
    #Initialize Defaults
    if depth is None:
        depth=0

    #Logger here Eventually
    #TODO - Switch from IfEl ladder to catch all
    #Explore Tag relationships
    logging.debug(stype)
    if stype=='tags':
        logging.info('Hunting Related Tags')
        collatedTags = collateRelatedTags([url],[],[sterms])
        logging.info('Output Tag Data')
        with open(outputs,'w') as tagfile:
            for tag in collatedTags:
                tagfile.write(tag + '\n')
    #Collect Album Data
    elif stype=='albums':
        logging.info('Hunting Album Data')
        logging.debug(depth)
        collatedAlbums = collateAlbums([url],[],[sterms],depth)
        huntResult = {}
        logging.info('Collecting Output Data')
        for alb in collatedAlbums:
            huntResult[alb] = collateAlbum(alb, ['tracks','artist','release','tags'])
        logging.info('Search returned ' + str(len(collatedAlbums)) + ' unique albums.')
        logging.info('Outputting Results')
        with open(outputs, 'w') as outfile:
            json.dump(huntResult, outfile)
        logging.info('Results saved to ' + outputs)
    #Collect Artist Discog Data
    elif stype=='artistDive':
        logging.info('Artist Data')
        collatedDiscog = get_bc_discography(urls,[],sterms)
    else:
        logging.debug('Search Style ' + style + ' is not a valid style.')

    logging.info('Done.')

    #collatedTags = collateRelatedTags(['https://bandcamp.com/tag/'],[],['chiptune','vgm','nerdcore','synthwave'])
    #logging.info('Number of potential related tags found: ' + str(len(collatedTags)))
    #with open('relatedTags.txt', 'w') as tagfile:
    #    for tag in collatedTags:
    #        tagfile.write(tag + '\n')
    #result = collateAlbums(['https://bandcamp.com/tag/'],[],['chiptune','vgm','nerdcore','synthwave','gameboy','lsdj'],0)
    #diveResult = {}
    #print("Number of Albums Found: " + str(len(result))
    #for res in result:
    #    diveResult[res] = collateAlbum(res, ['tracks','artist','release','tags'])
    #Save the results to json file
    #with open('albumDive.json', 'w') as outfile:
    #    json.dump(diveResult, outfile)
    #print("Done.")
    return 0

if __name__ == '__main__':
    #Run input grabbing only if someone's running the CLI
    #Starter version, very discrete, limited options and control
    parser = argparse.ArgumentParser()
    parser.add_argument('scantypes', help='The scan to be run.')
    parser.add_argument('scanterms', help='The term to scan for.')
    parser.add_argument('urls', help='The URL to scan')
    parser.add_argument('output', help='The filename to write to.')
    parser.add_argument('--depth', help='How deep to recurse for recursive scans')
    parser.add_argument('--log', help='Whether output should be logged to a file')
    args=parser.parse_args()

    if args.log:
        logging.basicConfig(filename=args.log, filemode='w', level=logging.INFO)

    #Args parsed, run scan
    main(args.scantypes, args.scanterms, args.urls, args.output, args.depth)

