A program to download low resolution images from the Australian Plant Image Index on the Australian National Botanical Gardens webpage. As of 2017-Oct-10, non-commercial use of low-resolution images downloaded from the Photo Collection area of the website is allowed on condition that the photographer is credited by name, if known, and that the copyright holder is also acknowledged. The source of the image should be listed as the Australian National Botanic Gardens and these words linked to the Photo Collection home page, http://www.anbg.gov.au/photo. For more up to date information on licensing visit: https://www.anbg.gov.au/photo/photo-collection-use.html

Have a look at the example plant list input. The program will save images into directories based on the groups (can be whatever you want, in the example it's based on native and introduced species that are presently around or absent from an area), then families and then the genus/species. If a "subsp." or "var." is presnt the program will first look for this and if it cannot find a result, will then just search for the base species.

The code at present does not convert the html link and photgrapher name to strings in the output metadata so if you need this you'll need to add just a couple of lines to do so. Sorry to leave the job half finished! Just do this down the bottom before the final metadata data.frame is written.  