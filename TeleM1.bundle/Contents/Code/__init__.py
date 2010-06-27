# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

from textwrap import dedent

def gettext(elem):
    if elem.text:
        text = dedent(elem.text)
    else:
        text = ""
    for subelem in elem:
        text = text + gettext(subelem)
        if subelem.tail:
            text = text + dedent(subelem.tail)

    return '\n'.join(text.splitlines())

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
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('Title'), ICON, ART)

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


def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")

    xml = XML.ElementFromURL(SHOW_LIST_URL, True)
    for show in xml.xpath("//div[@id='sidebar']//li[not(contains(@class, 'first'))]"):
        title = show.xpath("a")[0].text
        show_url = show.xpath("a")[0].get('href')
        show_page = XML.ElementFromURL(MAIN_URL + show_url, True)
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
                ),
                url = show_url,
            )
        )


    # ... and then return the container
    return dir


def RetreiveVideoURL(thread_url, title=None, description=None, thumb=None):
        thread_page = HTTP.Request(thread_url)
        thread_lines = thread_page.splitlines()
        url = None
        for line in thread_lines:
            if (line.find("var movieNameId = ") >= 0):
                url = MAIN_URL + line.split('"')[1]

        return VideoItem(
                    url,
                    title,
                    summary = description,
                    thumb = thumb,
                )


def ShowDetails(sender, url):
    dir = MediaContainer(viewGroup="InfoList")

    show_page = XML.ElementFromURL(MAIN_URL + url, True)
    show_number = -1
    for show in show_page.xpath("//div[@class='showContainer']"):
        show_number += 1

        try:
            thumb = MAIN_URL + show.xpath("div[@class='showOverviewImageContainer']/img")[0].get('src')
        except:
            thumb = None

        title = show.xpath("div[@class='showOverviewContentContainer']/h2")[0].text

        try:
            description = gettext(show.xpath("div/div/div[@class='showOverviewInformationContainer']")[0])
        except:
            description = None

        threads = show.xpath("div/div/div/ul[@class='showThreads']/li")

        if (len(threads) == 1):
            thread_url = MAIN_URL + threads[0].xpath("a")[0].get('href')
            dir.Append(RetreiveVideoURL(thread_url, title, description, thumb))
        else:
            dir.Append(
                Function(
                    DirectoryItem(
                        ShowParts,
                        title,
                        summary=description,
                        thumb=thumb,
                    ),
                    url = url,
                    show_number = show_number
                )
            )
    return dir


def ShowParts(sender, url, show_number):
    dir = MediaContainer(viewGroup="InfoList")

    show_page = XML.ElementFromURL(MAIN_URL + url, True)
    show = show_page.xpath("//div[@class='showContainer']")[show_number]

    for thread in show.xpath("div/div/div/ul[@class='showThreads']/li"):
        title = thread.xpath("a")[0].text
        thread_url = MAIN_URL + thread.xpath("a")[0].get('href')
        dir.Append(RetreiveVideoURL(thread_url, title))

    return dir

