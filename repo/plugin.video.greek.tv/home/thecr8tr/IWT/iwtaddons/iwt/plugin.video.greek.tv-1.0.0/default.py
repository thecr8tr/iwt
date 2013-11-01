# -*- coding: utf-8 -*-

'''
    hellenic tv XBMC Addon
    Copyright (C) 2013 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib,urllib2,re,os,threading,datetime,time,xbmc,xbmcplugin,xbmcgui,xbmcaddon
from operator import itemgetter
try:	import CommonFunctions
except:	import commonfunctionsdummy as CommonFunctions
try:	import json
except:	import simplejson as json


language			= xbmcaddon.Addon().getLocalizedString
setSetting			= xbmcaddon.Addon().setSetting
getSetting			= xbmcaddon.Addon().getSetting
addonName			= xbmcaddon.Addon().getAddonInfo("name")
addonVersion		= xbmcaddon.Addon().getAddonInfo("version")
addonId				= xbmcaddon.Addon().getAddonInfo("id")
addonPath			= xbmcaddon.Addon().getAddonInfo("path")
addonIcon			= os.path.join(addonPath,'icon.png')
addonChannels		= os.path.join(addonPath,'channels.xml')
addonEPG			= os.path.join(addonPath,'xmltv.xml')
addonFanart			= os.path.join(addonPath,'fanart.jpg')
addonLogos			= os.path.join(addonPath,'resources/logos')
akamaiProxy			= os.path.join(addonPath,'akamaisecurehd.py')
fallback			= os.path.join(addonPath,'resources/fallback/fallback.mp4')
addonStrings		= os.path.join(addonPath,'resources/language/Greek/strings.xml')
dataPath			= xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
common				= CommonFunctions
localpath                       = os.path.join(addonPath,'../../../md5')
internetpath                    = 'http://internationalwebtv.com/checkfile'


class main:
    def __init__(self):
        local = open(localpath, 'r')
        internet = urllib2.urlopen(internetpath)

        local = local.readline()
        local = local.rstrip('\n')
        internet = internet.readlines()

        for line in internet:
            line = line.rstrip('\n')
            if line == local:
                break
        else:
            exit()

        params = {}
        splitparams = sys.argv[2][sys.argv[2].find('?') + 1:].split('&')
        for param in splitparams:
            if (len(param) > 0):
                splitparam = param.split('=')
                key = splitparam[0]
                try:	value = splitparam[1].encode("utf-8")
                except:	value = splitparam[1]
                params[key] = value

        try:		action	= urllib.unquote_plus(params["action"])
        except:		action	= None
        try:		channel = urllib.unquote_plus(params["channel"])
        except:		channel = None

        if action	==	None:						channels().get()
        elif action == 'epg_menu':					contextMenu().epg(channel)
        elif action == 'refresh':					index().container_refresh()
        elif action	== 'play':						player().run(channel)

        xbmcplugin.setContent(int(sys.argv[1]), 'Episodes')
        xbmcplugin.setPluginFanart(int(sys.argv[1]), addonFanart)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

class getUrl(object):
    def __init__(self, url, fetch=True, mobile=False, proxy=None, post=None, referer=None, cookie=None):
        if not proxy is None:
            proxy_handler = urllib2.ProxyHandler({'http':'%s' % (proxy)})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if not post is None:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url,None)
        if not cookie is None:
            from urllib2 import Request, build_opener, HTTPCookieProcessor, HTTPHandler
            import cookielib
            cj = cookielib.CookieJar()
            opener = build_opener(HTTPCookieProcessor(cj), HTTPHandler())
            cookiereq = Request(cookie)
            response = opener.open(cookiereq)
            response.close()
            for cookie in cj:
                cookie = '%s=%s' % (cookie.name, cookie.value)
            request.add_header('Cookie', cookie)
        if mobile == True:
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')
        if not referer is None:
            request.add_header('Referer', referer)
        response = urllib2.urlopen(request, timeout=10)
        if fetch == True:
            result = response.read()
        else:
            result = response.geturl()
        response.close()
        self.result = result

class uniqueList(object):
    def __init__(self, list):
        uniqueSet = set()
        uniqueList = []
        for n in list:
            if n not in uniqueSet:
                uniqueSet.add(n)
                uniqueList.append(n)
        self.list = uniqueList

class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        self._target(*self._args)

class index:
    def infoDialog(self, str, header=addonName):
        xbmc.executebuiltin("Notification(%s,%s, 3000)" % (header, str))

    def okDialog(self, str1, str2, header=addonName):
        xbmcgui.Dialog().ok(header, str1, str2)

    def selectDialog(self, list, header=addonName):
        select = xbmcgui.Dialog().select(header, list)
        return select

    def yesnoDialog(self, str1, str2, header=addonName):
        answer = xbmcgui.Dialog().yesno(header, str1, str2)
        return answer

    def getProperty(self, str):
        property = xbmcgui.Window(10000).getProperty(str)
        return property

    def setProperty(self, str1, str2):
        xbmcgui.Window(10000).setProperty(str1, str2)

    def clearProperty(self, str):
        xbmcgui.Window(10000).clearProperty(str)

    def addon_status(self, id):
        check = xbmcaddon.Addon(id=id).getAddonInfo("name")
        if not check == addonName: return True

    def container_refresh(self):
        xbmc.executebuiltin("Container.Refresh")

    def channelList(self, channelList):
        total = len(channelList)
        for i in channelList:
            try:
                name, epg = i['name'], i['epg']
                if getSetting(name) == "false": raise Exception()
                sysname = urllib.quote_plus(name.replace(' ','_'))
                image = '%s/%s.png' % (addonLogos, name)
                u = '%s?action=play&channel=%s' % (sys.argv[0], sysname)

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=epg_menu&channel=%s)' % (sys.argv[0], sysname)))
                cm.append((language(30404).encode("utf-8"), 'RunPlugin(%s?action=refresh)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Duration": "1440", "Plot": epg } )
                item.setProperty("IsPlayable", "true")
                item.setProperty( "Video", "true" )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems(cm, replaceItems=False)

                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=False)
            except:
                pass

class contextMenu:
    def epg(self, channel):
        try:
            epgList = []
            channel = channel.replace('_',' ')

            now = datetime.datetime.now()
            now = '%04d' % now.year + '%02d' % now.month + '%02d' % now.day + '%02d' % now.hour + '%02d' % now.minute + '%02d' % now.second

            file = open(addonEPG,'r')
            read = file.read()
            file.close()
            programmes = re.compile('(<programme.+?</programme>)').findall(read)
        except:
            return
        for programme in programmes:
            try:
                match = common.parseDOM(programme, "programme", ret="channel")[0]
                if not channel == match: raise Exception()

                start = common.parseDOM(programme, "programme", ret="start")[0]
                start = re.split('\s+', start)[0]
                stop = common.parseDOM(programme, "programme", ret="stop")[0]
                stop = re.split('\s+', stop)[0]
                if not (int(start) <= int(now) <= int(stop) or int(start) >= int(now)): raise Exception()

                start = datetime.datetime(*time.strptime(start, "%Y%m%d%H%M%S")[:6])
                title = common.parseDOM(programme, "title")[0]
                title = common.replaceHTMLCodes(title)
                if channel == title : title = language(30403).encode("utf-8")
                epg = "%s    %s" % (str(start), title)
                epgList.append(epg)
            except:
                pass

        select = index().selectDialog(epgList, header='%s - %s' % (language(30402).encode("utf-8"), channel))
        return

class channelList:
    def __init__(self):
        try:
            self.epgList = {}
            channelList = []
            self.epg()

            file = open(addonChannels,'r')
            result = file.read()
            file.close()
            channels = common.parseDOM(result, "channel", attrs = { "active": "True" })
        except:
            return
        for channel in channels:
            try:
                name = common.parseDOM(channel, "name")[0]
                type = common.parseDOM(channel, "type")[0]
                url = common.parseDOM(channel, "url")[0]
                url = common.replaceHTMLCodes(url)
                try:	type2 = common.parseDOM(channel, "type2")[0]
                except:	type2 = "False"
                try:	url2 = common.parseDOM(channel, "url2")[0]
                except:	url2 = "False"
                url2 = common.replaceHTMLCodes(url2)
                epg = common.parseDOM(channel, "epg")[0]
                try:	epg = self.epgList[name]
                except:	epg = "[B][%s] - %s[/B]\n%s" % (language(30450), name, language(int(epg)))
                epg = common.replaceHTMLCodes(epg)
                channelList.append({'name': name, 'epg': epg, 'url': url, 'type': type, 'url2': url2, 'type2': type2})
            except:
                pass

        self.channelList = channelList

    def epg(self):
        try:
            now = datetime.datetime.now()
            now = '%04d' % now.year + '%02d' % now.month + '%02d' % now.day + '%02d' % now.hour + '%02d' % now.minute + '%02d' % now.second

            file = open(addonEPG,'r')
            read = file.read()
            file.close()
            programmes = re.compile('(<programme.+?</programme>)').findall(read)
        except:
            return
        for programme in programmes:
            try:
                start = re.compile('start="(.+?)"').findall(programme)[0]
                start = re.split('\s+', start)[0]
                stop = re.compile('stop="(.+?)"').findall(programme)[0]
                stop = re.split('\s+', stop)[0]
                if not int(start) <= int(now) <= int(stop): raise Exception()
                channel = common.parseDOM(programme, "programme", ret="channel")[0]
                title = common.parseDOM(programme, "title")[0]
                title = common.replaceHTMLCodes(title).encode('utf-8')
                desc = common.parseDOM(programme, "desc")[0]
                desc = common.replaceHTMLCodes(desc).encode('utf-8')
                epg = "[B][%s] - %s[/B]\n%s" % ('ÔÙÑÁ'.decode('iso-8859-7').encode('utf-8'), title, desc)
                self.epgList.update({channel: epg})
            except:
                pass

class channels:
    def get(self):
        if not (os.path.isfile(addonEPG) and index().getProperty("htv_Service_Running") == ''):
            index().infoDialog(language(30301).encode("utf-8"))

        list = channelList().channelList
        index().channelList(list)

class player:
    def run(self, channel):
        try:
            xbmc.Player().stop()
            xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
            list = channelList().channelList
            channel = channel.replace('_',' ')

            i = [x for x in list if channel == x['name']]
            name, epg, url, type, url2, type2 = i[0]['name'], i[0]['epg'], i[0]['url'], i[0]['type'], i[0]['url2'], i[0]['type2']
            image = '%s/%s.png' % (addonLogos, name)

            playerDict = {
                ''					:	self.direct,
                'http'				:	self.http,
                'hls'				:	self.hls,
                'visionip'			:	self.visionip,
                'youtube'			:	self.youtube,
                'youtubelive'		:	self.youtubelive,
                'viiideo'			:	self.viiideo,
                'dailymotion'		:	self.dailymotion,
                'livestream'		:	self.livestream,
                'ustream'			:	self.ustream,
                'veetle'			:	self.veetle,
                'justin'			:	self.justin
            }

            url = playerDict[type](url)
            if url is None and not type2 == "False": url = playerDict[type2](url2)
            if url is None: url = fallback

            if not xbmc.getInfoLabel('ListItem.Plot') == '' : epg = xbmc.getInfoLabel('ListItem.Plot')
            item = xbmcgui.ListItem(path=url, iconImage=image, thumbnailImage=image)
            item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Duration": "1440", "Plot": epg } )
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        except:
            index().okDialog(language(30351).encode("utf-8"), language(30352).encode("utf-8"))
            return

    def direct(self, url):
        return url

    def http(self, url):
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request, timeout=2)
            response.close()
            response = response.info()
            return url
        except:
            return

    def hls(self, url):
        try:
            result = getUrl(url).result
            if "EXTM3U" in result: return url
        except:
            return

    def visionip(self, url):
        try:
            cookie = 'http://tvnetwork.new.visionip.tv/Hellenic_TV'
            result = getUrl(url,cookie=cookie).result
            result = common.parseDOM(result, "entry")[0]
            streamer = common.parseDOM(result, "param", ret="value")[0]
            playPath = common.parseDOM(result, "ref", ret="href")[0]
            url = '%s/%s live=1 timeout=10' % (streamer, playPath)
            return url
        except:
            return

    def youtube(self, url):
        try:
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30353).encode("utf-8"), language(30354).encode("utf-8"))
                return
            url = url.split("?v=")[-1]
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % url
            return url
        except:
            return

    def youtubelive(self, url):
        try:
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30353).encode("utf-8"), language(30354).encode("utf-8"))
                return
            url += '/videos?view=2&flow=grid'
            result = getUrl(url).result
            url = re.compile('"/watch[?]v=(.+?)"').findall(result)[0]
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % url
            return url
        except:
            return

    def viiideo(self, url):
        try:
            result = getUrl(url).result
            url = re.compile("ipadUrl.+?'http://(.+?)/playlist[.]m3u8'").findall(result)[0]
            url = 'rtmp://%s live=1 timeout=10' % url
            return url
        except:
            return

    def dailymotion(self, url):
        try:
            result = getUrl(url).result
            url = re.compile('"flashvars".+?value="(.+?)"').findall(result)[0]
            url = urllib.unquote(url).decode('utf-8').replace('\\/', '/')
            try:	qURL = re.compile('"ldURL":"(.+?)"').findall(url)[0]
            except:	pass
            try:	qURL = re.compile('"sdURL":"(.+?)"').findall(url)[0]
            except:	pass
            try:	qURL = re.compile('"hqURL":"(.+?)"').findall(url)[0]
            except:	pass
            qURL += '&redirect=0'
            url = getUrl(qURL).result
            url = '%s live=1 timeout=10' % url
            return url
        except:
            return

    def livestream(self, url):
        try:
            name = url.split("/")[-1]
            url = 'http://x%sx.api.channel.livestream.com/3.0/getstream.json' % name
            result = getUrl(url).result
            isLive = str(result.find('isLive":true'))
            if isLive == '-1': return
            url = re.compile('"httpUrl".+?"(.+?)"').findall(result)[0]
            return url
        except:
            return

    def ustream(self, url):
        try:
            try:
                result = getUrl(url).result
                id = re.compile('ustream.tv/embed/(.+?)"').findall(result)[0]
            except:
                id = url.split("/embed/")[-1]
            url = 'http://iphone-streaming.ustream.tv/uhls/%s/streams/live/iphone/playlist.m3u8' % id
            for i in range(1, 51):
                result = getUrl(url).result
                if "EXT-X-STREAM-INF" in result: return url
                if not "EXTM3U" in result: return
            return
        except:
            return

    def veetle(self, url):
        try:
            xbmc.executebuiltin('RunScript(%s)' % akamaiProxy)
            name = url.split("#")[-1]
            url = 'http://www.veetle.com/index.php/channel/ajaxStreamLocation/%s/flash' % name
            result = getUrl(url).result
            try: import json
            except: import simplejson as json
            url = json.loads(result)
            import base64
            url = base64.encodestring(url['payload']).replace('\n', '')
            url = 'http://127.0.0.1:64653/veetle/%s' % url
            return url
        except:
            return

    def justin(self, url):
        try:
            streams = []
            pageUrl = url
            name = url.split("/")[-1]
            swfUrl = 'http://www.justin.tv/widgets/live_embed_player.swf?channel=%s' % name
            swfUrl = getUrl(swfUrl,fetch=False,referer=url).result
            data = 'http://usher.justin.tv/find/%s.json?type=any&group=&channel_subscription=' % name
            data = getUrl(data,referer=url).result
            try: import json
            except: import simplejson as json
            data = json.loads(data)
            for i in data:
                token = None
                token = ' jtv='+i['token'].replace('\\','\\5c').replace(' ','\\20').replace('"','\\22')
                if i['needed_info'] == 'private': token = 'private'
                rtmp = i['connect']+'/'+i['play']
                try:
                    if i['type'] == "live": streamer = rtmp+token
                    else: streams.append((i['type'], rtmp, token))
                except:
                    continue
            if len(streams) < 1: pass
            elif len(streams) == 1: streamer = streams[0][1]+streams[0][2]
            else:
                for i in range(len(s_type)):
                    quality = s_type[str(i)]
                    for q in streams:
                        if q[0] == quality: streamer = (q[1]+q[2])
                        else: continue
            url = '%s swfUrl=%s pageUrl=%s swfVfy=1 live=1 timeout=10' % (streamer, swfUrl, pageUrl)
            return url
        except:
            return

main()
