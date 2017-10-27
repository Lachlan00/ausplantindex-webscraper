# Australian Plant Image Index - Web Scraper

"""
A program to download low resolution images from the Australian Plant Image Index on the Australian National Botanical Gardens webpage. 
As of 2017-Oct-10, non-commercial use of low-resolution images downloaded from the Photo Collection area of the website 
is allowed on condition that the photographer is credited by name, if known, and that the copyright holder is also acknowledged. 
The source of the image should be listed as the Australian National Botanic Gardens and these words linked to the 
Photo Collection home page, http://www.anbg.gov.au/photo. For more up to date information on licensing visit: 
https://www.anbg.gov.au/photo/photo-collection-use.html
"""

# load modules
import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import re
import lxml.html as html # to get locations due to soup bug
import numpy as np
from os.path import basename 
import os
import math

# Use this section to parse your own input file
# # make parser
# parser = argparse.ArgumentParser()
# # add a positional writable file argument
# parser.add_argument('input_file')
# #parser.add_argument('output_file', type=argparse.FileType('w'))
# args = parser.parse_args()

# # read datas
# plants_df = pd.read_csv(args.input_file)

### or import your own csv file directly here
plants_df = pd.read_csv('/directory/to/csv')

# find number of images in results, used to determine successful search (>0)
def fun_resultcheck(soup):
	results = str(soup.find_all('h3'))
	results = re.findall(r'\d+', results)
	if len(results) == 3:
	    results = int(results[1])
	else:
	    results = 0
	return(results)

# functions for downloading webpages with lxml.html and Beautifulsoup
# genus + species
def fun_pagedownload(genus, species):
	page = requests.get("https://www.anbg.gov.au/cgi-bin/apiiName?030=" + genus + "+" + species)
	soup = BeautifulSoup(page.content, 'html.parser')
	# with lxml.html for locations (soup bug)
	root = html.fromstring(page.content)
	# find number of images in results, used to determine successful search (>0)
	results = fun_resultcheck(soup)
	return {'soup':soup, 'root':root ,'results':results}
# genus + species + sub/var
def fun_pagedownload_subsp(genus, species, subsp):
	page = requests.get("https://www.anbg.gov.au/cgi-bin/apiiName?030=" + genus + "+" + species + "+" + subsp)
	soup = BeautifulSoup(page.content, 'html.parser')
	# with lxml.html for locations (soup bug)
	root = html.fromstring(page.content)
	# find number of images in results, used to determine successful search (>0)
	results = fun_resultcheck(soup)
	return {'soup':soup, 'root':root ,'results':results}

# list to hold results
df_ls = []

print('Getting image links')
# get dataframe with all values rquired to download images
for index, row in plants_df.iterrows():
	group = row['group']
	family = row['family']
	genus = row['genus']
	species = row['species']
	subsp = row['sub.var']
	
	# reset subsp search checker
	subsp_fail = False

	# conduct search
	if (pd.isnull(subsp)):
		download = fun_pagedownload(genus, species)
	else:
		download = fun_pagedownload_subsp(genus, species, subsp)
		# check result
		if download['results'] == 0:
			download = fun_pagedownload(genus, species)
			subsp_fail = True

	# pull out results
	soup = download['soup']
	root = download['root']
	results = download['results']

	# continue if there are results, else enter 'NaN'
	if results > 0:
		# find all photo links
		if (pd.isnull(subsp)) or subsp_fail == True:
		    grep_str = genus + ' ' + species
		else:
		    grep_str = genus + ' ' + species + ' ' + subsp
		links = []
		for a in root.xpath("//a[contains(.,'" + grep_str + "')]"):
		    links.append(a)
		# find location (alternative method due to soup bug not finding text followed by links)
		location = []
		for td in root.xpath("//td[contains(text(),'Taken at')]"):
		    location.append(td.text_content())
		# find photographers
		grep_str = '^Photographer.*$'
		pattern = re.compile(grep_str)
		photographer = soup.findAll('td', text=pattern)

		# save results to data.frame
		dat = {'group':np.repeat(group, results), 'family':np.repeat(family, results), 
				'genus':np.repeat(genus, results), 'species':np.repeat(species, results), 
				'sub.var':np.repeat(subsp, results),'link':links,'location':location, 
				'photographer':photographer}
		df = pd.DataFrame(dat, columns=dat.keys())
	else:
		dat = {'group':group, 'family':family, 'genus':genus, 'species':species, 
				'sub.var':subsp,'link':np.NaN,'location':np.NaN, 'photographer':np.NaN}
		df = pd.DataFrame(dat, columns=dat.keys(), index=[0])

	# save to list
	df_ls.append(df)

# concat data frames
df = pd.concat(df_ls)
df = df.reset_index()


print('Downloading images...')
# download photos and save to directory
for index, row in df.iterrows():
    # names and directory stuff
    group = row['group']
    family = row['family']
    genus = row['genus']
    species = row['species']
    subsp = row['sub.var']
    idx = row['index']
	
    # get link
    link = row['link']
    
    if (pd.isnull(link)):
        print('no image for ' + genus + ' ' + species)
    else:
    	link = link.attrib
    	link = str(link)
    	link = re.search(": '(.+?)'}", link).group(1)
    	# get photo page
    	link = 'https://www.anbg.gov.au' + link + '&size=3'
    	page = requests.get(link)
    	soup = BeautifulSoup(page.content, 'html.parser')
    	img = soup.findAll('img')
    	img = img[2].get('src')
    	img = 'https://www.anbg.gov.au' + img
    	
    	# construct file paths
 		# put the directory where you want the images saved to here
    	base_dir = '/directory/to/output/folder/'
    	group_dir = base_dir + group + '/'
    	family_dir = group_dir + family + '/'
    	if (pd.isnull(subsp)):
    	    species_dir = family_dir + genus + '_' + species + '/'
    	    # make file name
    	    fn = str(idx) + '-' + genus + '_' + species
    	else:
    	    species_dir = family_dir + genus + '_' + species + '_' + subsp + '/'
    	    # make file name
    	    fn = str(idx) + '-' + genus + '_' + species + '_' + subsp 
    	
    	# make directories if required
    	if not os.path.exists(group_dir):
    		os.makedirs(group_dir)
    	if not os.path.exists(family_dir):
    		os.makedirs(family_dir)
    	if not os.path.exists(species_dir):
    		os.makedirs(species_dir)

    	# download and save image
    	f = open(species_dir + fn + ".jpg", 'wb')
    	f.write(requests.get(img).content)
    	f.close()

# if you need the links as strings in the metadata, convert them here

print('Saving metadata...')
df.to_csv(base_dir + "photo_metadata.csv", index=False)

print('Done')
    