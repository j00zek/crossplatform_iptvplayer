﻿# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.dToolsSet.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.dToolsSet.iptvtools import printDBG, printExc, GetCookieDir, byteify, rm, CSelOneLink
from Plugins.Extensions.IPTVPlayer.itools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist, getMPDLinksWithMeta
from Plugins.Extensions.IPTVPlayer.dToolsSet.iptvplayerinit import SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.icomponents.ihost import CBaseHostClass
###################################################

###################################################
# FOREIGN import
###################################################
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
import re
import urllib
import random
import string
try:    import json
except Exception: import simplejson as json

from os import path as os_path
############################################

###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.icomponents.asynccall import MainSessionWrapper
###################################################

###################################################
# Config options for HOST
###################################################

def GetConfigList():
    optionList = []
    return optionList
    
###################################################

class DjingComApi(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self)
        self.MAIN_URL         = 'https://www.djing.com/'
        self.DEFAULT_ICON_URL = 'https://www.djing.com/newimages/content/c01.jpg'
        self.HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36', 'Accept': 'text/html', 'Accept-Encoding':'gzip, deflate'}
        self.AJAX_HEADER = dict(self.HTTP_HEADER)
        self.AJAX_HEADER.update( {'X-Requested-With': 'XMLHttpRequest'} )
        
        self.COOKIE_FILE = GetCookieDir('viortv.cookie')
        
        self.defaultParams = {}
        self.defaultParams.update({'header':self.HTTP_HEADER, 'cookiefile': self.COOKIE_FILE}) #'save_cookie': True, 'load_cookie': True,
        self.loggedIn = False
        self.accountInfo = ''
    
    def getList(self, cItem):
        printDBG("DjingComApi.getChannelsList")
        
        channelsTab = []
        
        sts, data = self.cm.getPage(self.getMainUrl(), self.defaultParams)
        if not sts: return channelsTab
        
        data = self.cm.ph.getDataBeetwenNodes(data, ('<ul', '>', 'bgImages'), ('</ul', '>'))[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
        for item in data:
            icon  = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''<img[^>]+?src=['"]([^"^']+?)['"]''')[0] )
            url   = self.getFullUrl( self.cm.ph.getSearchGroups(item, '''<source[^>]+?src=['"]([^"^']+?)['"]''')[0] )
            if not self.cm.isValidUrl(url): continue
            
            title = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<h3', '</h3>')[1] )
            desc  = self.cleanHtmlStr( self.cm.ph.getDataBeetwenMarkers(item, '<p', '</p>')[1] )
            params = {'name':cItem['name'], 'type':'video', 'title':title, 'url':self.getMainUrl(), 'iptv_hls_url':url, 'icon':icon, 'desc':desc}
            channelsTab.append(params)
        
        return channelsTab
        
    def getVideoLink(self, cItem):
        printDBG("DjingComApi.getVideoLink")
        urlsTab = []
        hlsUrl = cItem.get('iptv_hls_url', '')
        printDBG("hlsUrl||||||||||||||||| " + hlsUrl)
        if hlsUrl != '':
            hlsUrl = strwithmeta(hlsUrl, {'User-Agent':self.defaultParams['header']['User-Agent'], 'Referer':cItem['url']})
            urlsTab = getDirectM3U8Playlist(hlsUrl, checkContent=True)
            
        def __getLinkQuality( itemLink ):
            try: return int(itemLink['bitrate'])
            except Exception: return 0
        
        return CSelOneLink(urlsTab, __getLinkQuality, 99999999).getSortedLinks()