# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/telem1"

MAIN_URL = "http://www.telem1.ch"
SHOW_LIST_URL = MAIN_URL + "/de/showgrid.html"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.png'
ICON          = 'icon-default.png'

####################################################################################################

def Start():

    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

  


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def VideoMainMenu():

    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="InfoList")

    xml = XML.ElementFromURL(SHOW_LIST_URL, True)
    for show in xml.xpath("//div[@id='sidebar']//li[not(contains(@class, 'first'))]"):
        title = show.xpath("a")[0].text
        url = show.xpath("a")[0].get('href')
        Log(title + ": " + url)
        show_page = XML.ElementFromURL(MAIN_URL + url, True)
        try:
            description = show_page.xpath("//div[@class='content']/p")[0].text
        except:
            description = None
        try:
            thumb = MAIN_URL + show_page.xpath("//div[@class='img-r-Containter']/img")[0].get('src')
        except:
            thumb = None
        dir.Append(
            Function(
                DirectoryItem(
                    ShowDetails,
                    title,
                    summary=description,
                    thumb=thumb,
                )
            )
        )


    # ... and then return the container
    return dir

def ShowDetails(sender):
    dir = MediaContainer(viewGroup="InfoList")

    return dir

  
