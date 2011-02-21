"""
 Copyright (c) 2010 Johan Wieslander, <johan[d0t]wieslander<(a)>gmail[d0t]com>

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import re
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import urllib2
from xml.dom.minidom import parse, parseString

# plugin constants
__settings__ = xbmcaddon.Addon(id='plugin.video.radbox')
__language__ = __settings__.getLocalizedString

RE_VIMEO = 'vimeo.com/(|video/)(\d+)'
RE_YOUTUBE = 'http://www.youtube.com/(watch\?.*v=(.*?)["&]|v/(.*?)["\?])'

NS_MEDIA = "http://search.yahoo.com/mrss/"


def listFeed(feedUrl):
    doc = load_xml(feedUrl)
    for item in doc.getElementsByTagName("item"):
        title = get_node_value(item, "title")
        description = get_node_value(item, "description")
        url = None
        url_nodes = item.getElementsByTagNameNS(NS_MEDIA, "content")
        if url_nodes:
            url = url_nodes[0].getAttribute("url")
            url = pluginUrl(url)
        thumb = None
        thumbnail_nodes = item.getElementsByTagNameNS(NS_MEDIA, "thumbnail")
        if thumbnail_nodes:
            thumb = thumbnail_nodes[0].getAttribute("url")

        addPosts(title, url, description, thumb)
    return
            
def pluginUrl(url):
    vimeoId = re.findall(RE_VIMEO, url, re.IGNORECASE)
    youtubeId = re.findall(RE_YOUTUBE, url)
    out = ""
    videoType = ""
    videoId = ""
    if vimeoId:
       videoType = "videotype=vimeo"
       (first, second) = vimeoId[0]
       videoId = "videoid=%s" % str(second)
    elif youtubeId:
       videoType = "videotype=youtube"
       (first, second, third) = youtubeId[0]
       if second:
           videoId = "videoid=%s" % str(second)
       else:
           videoId = "videoid=%s" % str(third)
    out = videoType + "&" + videoId
    return out
  
def addPosts(title, url, description='', thumb=''):
 listitem=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=thumb)
 listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot" : description } )
 xurl = "%s?play=ok&" % sys.argv[0]
 xurl = xurl + url
 listitem.setPath(xurl)
 xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem)
 
# FROM plugin.video.youtube.beta  -- converts the request url passed on by xbmc to our plugin into a dict  
def getParameters(parameterString):
    commands = {}
    splitCommands = parameterString[parameterString.find('?')+1:].split('&')
    
    for command in splitCommands: 
        if (len(command) > 0):
            splitCommand = command.split('=')
            name = splitCommand[0]
            value = splitCommand[1]
            commands[name] = value
    
    return commands
    
def playVideo(params):
    get = params.get
    videoType = get("videotype")
    videoId = get("videoid")
    url = ""
    if (videoType == "youtube"):
        youTubeType = __settings__.getSetting( "youTubeType" )
        if (youTubeType == "0"):
            ytt = "youtube"
        else:
            ytt = "youtube.beta"
        url = ("plugin://plugin.video." + ytt + "/?action=play_video&videoid=%s") % videoId
    if (videoType == "vimeo"):
        vimeoType = __settings__.getSetting( "vimeoType" )
        if (vimeoType == "0"):
            vt = "vimeo"
        else:
            vt = "vimeo.beta"
        url = ("plugin://plugin.video." + vt + "/?action=play_video&videoid=%s") % videoId

    xbmc.executebuiltin("xbmc.PlayMedia("+url+")")

def get_node_value(parent, name, ns=""):
    if ns:
        return parent.getElementsByTagNameNS(ns, name)[0].childNodes[0].data
    else:
        return parent.getElementsByTagName(name)[0].childNodes[0].data

def load_xml(url):
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
    except:
        xbmc.log("unable to load url: " + url)

    xml = response.read()
    response.close()
    xml = xml.replace("& ", "&amp; ")
    return parseString(xml)

if (__name__ == "__main__" ):
    if ( not __settings__.getSetting( "firstrun" ) ):
        __settings__.openSettings()
        __settings__.setSetting( "firstrun", '1' )
    if (not sys.argv[2]):
        feedUrl = __settings__.getSetting( "feedUrl" )
        listFeed(feedUrl)
    else:
        params = getParameters(sys.argv[2])
        get = params.get
        if (get("play")):
            playVideo(params)

xbmcplugin.endOfDirectory(int(sys.argv[1]))