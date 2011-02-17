"""
 Copyright (c) 2010 Johan Wieslander, <johan.wieslander@gmail.com>

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

from BeautifulSoup import BeautifulStoneSoup
import xbmcutils.net, re
import sys, xbmc, xbmcaddon, xbmcgui, xbmcplugin

# plugin constants
__settings__ = xbmcaddon.Addon(id='plugin.video.radbox')
__language__ = __settings__.getLocalizedString

re_vimeo = 'vimeo.com/(|video/)(\d+)"'
re_youtube = 'http://www.youtube.com/(watch\?.*v=(.*?)["&]|v/(.*?)["\?])'

#http://player.vimeo.com/video/19474258
#http://www.youtube.com/v/SYweCrksFWI?version=3



#Get the rss stream
def getFeed(url):
  reqHeader = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'}
  data = xbmcutils.net.retrieve(url, None, reqHeader)
  return BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
 

def listFeed(feedUrl):
   
  feedTree = getFeed(feedUrl)
  
  items = feedTree.findAll('item')
  nItems = len(items)
  if (nItems == 0):
    __settings__.openSettings()
  else:
    for n in range(nItems):
        itemTitle = items[n]('title')[0].contents[0]
        itemUrl = items[n]('media:content')[0]
        print itemUrl
        itemUrl = pluginUrl(str(itemUrl))
        if not (itemUrl == "&"):
            addPosts(itemTitle, itemUrl)

def pluginUrl(url):
 vimeoId = re.findall(re_vimeo, url, re.IGNORECASE)
 youtubeId = re.findall(re_youtube, url)
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
  
def addPosts(title, url):
 listitem=xbmcgui.ListItem(title, iconImage="DefaultFolder.png")
 listitem.setInfo( type="Video", infoLabels={ "Title": title } )
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