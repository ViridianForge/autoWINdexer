#
# AutoWINdexer.py
# Author: Wayne "ViridianForge" Manselle
# Version 0.1
#
# Changelog:
# 0.1 - 08/05/17 -- Initial Creation
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

#Main driver here
def collateData(dataLocs, queries, options):
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
		albumURLs = []
		for query in queries:
			relatedTags = []
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
					print("Printing current Related Tags!")
					for tag in rTags:
						print(tag.text,"\n")
						relatedTags.append(tag.text)
				albumElems = soup.find_all("li", class_=["item", "item_end"])
				for album in albumElems:
					albumURLs.append(album.find("a").get("href"))
	#Return the awesome stuff
	return albumURLs

'''
Main method documentation
'''
def main():
	#Input Grabber here Eventually
	#Logger here Eventually
	#Temp for testing
	result = collateData(['https://bandcamp.com/tag/'],['chiptune'],0)
	print("Results:")
	for res in result:
		print(res,"\n")
	print("Done.")
	return 0

if __name__ == '__main__':
	main()
