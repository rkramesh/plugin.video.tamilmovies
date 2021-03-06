"""
    Tamilgun Kodi Addon
    Copyright (C) 2016 gujal

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
"""

import sys
from urlparse import parse_qsl
import urlparse
import urllib2
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from BeautifulSoup import BeautifulSoup, SoupStrainer
import os,re, requests, urllib, json
import os, time, datetime, traceback, re, fnmatch, glob
import jsunpack
import urlresolver
import logging

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
tamilgunurl = _addon.getSetting('tamilgunurl')
tamildboxurl = _addon.getSetting('tamildboxurl')
_download_dir = _addon.getSetting('download_dir')
_addonname = _addon.getAddonInfo('name')
_icon = _addon.getAddonInfo('icon')
_fanart = _addon.getAddonInfo('fanart')
mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
#tamildboxurl='http://tamildbox.me'

logging.warning("{0} {1} {2} {0}".format ('##'*15, 'sysargv',sys.argv))

def GetSearchQuery(sitename):
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Search ' + sitename)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_text = keyboard.getText()

    return search_text

#def download(url,dest,title,dp = None):
def download(url, destination, title, verify, dp=None, headers=None, cookies=None,
             allow_redirects=True,timeout=30, auth=None):
    """
    Download torrent

    :param torrent:
    :return:
    """
    if verify==False:
       xbmc.executebuiltin('XBMC.Dialog.Close(all, true)')
       #xbmc.executebuiltin( 'Dialog.Close(9999)' )
       #xbmc.executebuiltin( 'Container.Refresh' )

    if _download_dir and verify==True:
        #download_torrent(torrent, os.path.join(plugin.download_dir, show_title))
        start_time = time.time()
        if xbmcgui.Dialog().yesno('Download Movie',title+' will be downloaded to '+_download_dir+' directory'):
            xbmcgui.Dialog().notification('Tamil Movies', title+' Movie added  for downloading.',
                                         _icon, 3000, sound=False)
            if not dp:
                dp = xbmcgui.DialogProgressBG()
                # dp.create("Downloading "+title+"...",' ', ' ')
                dp.create("Downloading "+title+"...")
                window_id = xbmcgui.getCurrentWindowDialogId()
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'dp-win',window_id))
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'dp',dp))

            dp.update(0)
            url=url.split('|')[0]
            path = urlparse.urlparse(url).path
            ext = os.path.splitext(path)[1]
            destination = os.path.join(destination, title+ext)
            #logging.warning("{0} {1} {2} {0}".format ('##'*15, 'download',dest))
            #try:
                #urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp,title,start_time))            
                ##

            try:
                with open(destination, 'wb') as f:
                    start = time.time()
                    r = requests.get(url, headers=headers, cookies=cookies,
                                     allow_redirects=allow_redirects, verify=verify,
                                     timeout=timeout, auth=auth, stream=True)
                    content_length = int(r.headers.get('content-length'))
                    if content_length is None:
                        f.write(r.content)
                    else:
                        dl = 0
                        for chunk in r.iter_content(chunk_size=content_length/100):
                            dl += len(chunk)
                            if chunk:
                                f.write(chunk)
                            progress = (dl * 100 / content_length)
                            byte_speed = dl / (time.time() - start)
                            kbps_speed = byte_speed / 1024
                            mbps_speed = kbps_speed / 1024
                            downloaded = float(dl) / (1024 * 1024)
                            file_size = float(content_length) / (1024 * 1024)
                            if byte_speed > 0:
                                eta = (content_length - dl) / byte_speed
                            else:
                                eta = 0
                            line1 = '[COLOR darkgoldenrod]%.1f Mb[/COLOR] Of [COLOR darkgoldenrod]%.1f Mb[/COLOR]' %(downloaded, file_size)
                            line2 = 'Speed: [COLOR darkgoldenrod]%.01f Mbps[/COLOR]' %mbps_speed
                            line2 += ' ETA: [COLOR darkgoldenrod]%02d:%02d[/COLOR]' %divmod(eta, 60)
                            dp.update(progress, line1, line2)
                dp.close()
                xbmcgui.Dialog().notification('Tamil Movies', title+' Download is complete',
                                              _icon, 3000, sound=False)
            except:
                dp.close()
                xbmcgui.Dialog().ok('[COLOR red]Error[/COLOR]', 'Sorry Something Went Wrong Please Try Again')
                    ##
            '''        
            except Exception,e:             
                print e
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'download-exception',e))
            '''


    elif not _download_dir and xbmcgui.Dialog().yesno('Tamil Movies', 'To download movie you need',
                                                           'to set base download directory first!',
                                                           'Open plugin settings?'):
        _addon.openSettings()

def _pbhook(numblocks, blocksize, filesize, url, dp, title, start_time):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        currently_dofwnloaded = float(numblocks) * blocksize / (1024 * 1024)
        kbps_speed = numblocks * blocksize / (time.time() - start_time)
        if kbps_speed > 0: eta = (filesize - numblocks * blocksize) / kbps_speed
        else: eta = 0
        kbps_speed = kbps_speed / 1024
        total = float(filesize) / (1024 * 1024)
        mbs = 'Downloaded %.02f MB of %.02f MB' % (currently_downloaded, total)
        speed = 'Speed: %.02f Kb/s ' % kbps_speed
        eta = 'ETA: %02d:%02d' % divmod(eta, 60)
       # dia.update(percent, mbs, e)
        dp.update(percent, mbs, speed, eta)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled():
        raise Exception("Canceled")
        dp.close()

def convert(url):
    if url.startswith('//'):
        return 'http://' + url[len('//'):]
    return url

def get_strm(url):
    link = requests.get(url, headers=mozhdr).text
    soup = BeautifulSoup(link)
    rawJ = soup.findAll('script')
    J = str(rawJ[4])
    rk=J.split('var mainVideo = ')[1].rsplit('var vastUrl =')[0].rsplit(';', 1)[0]
    return rk

def get_vidhost(url):
    """
    Trim the url to get the video hoster
    :return vidhost
    """
    parts = url.split('/')[2].split('.')
    vidhost = '%s.%s'%(parts[len(parts)-2],parts[len(parts)-1])
    return vidhost

def resolve_media(url,videos):

    non_str_list = ['#', 'magnet:', 'desihome.co', 'thiruttuvcd',
                    'lcineview', 'bollyheaven', 'videolinkz',
                    'imdb.', 'mgid.', 'facebook.', 'm2pub', 
                    'tamilraja.org']

    embed_list = ['cineview', 'bollyheaven', 'videolinkz', 'vidzcode',
                  'embedzone', 'embedsr', 'fullmovie-hd', 'adly.biz',
                  'embedscr', 'hls_stream', 'embedrip', 'movembed', 'power4link.us',
                  'techking.me', 'onlinemoviesworld.xyz', 'cinebix.com']

    logging.warning("{0} {1} {2} {0}".format ('11'*15, 'before',url))
    url=convert(url)    
    logging.warning("{0} {1} {2} {0}".format ('22'*15, 'after',url))
    if any ([x in url for x in embed_list]):
        clink = requests.get(url, headers=mozhdr).text
        csoup = BeautifulSoup(clink)
        try:
            for link in csoup.findAll('iframe'):
                strurl = link.get('src')
                if not any([x in strurl for x in non_str_list]):
                    vidhost = get_vidhost(strurl)
                    videos.append((vidhost,strurl))
        except:
            pass

        try:
                rawJ = csoup.findAll('script')
                J = str(rawJ[4])
                rk=J.split('var mainVideo = ')[1].rsplit('var vastUrl =')[0].rsplit(';', 1)[0]
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'play-list',rk))
                strm_url=rk.replace('\'', '') 
                vidhost = get_vidhost(url)
                videos.append((vidhost,strm_url))
        except:
            pass

        try:
            plink = csoup.find(class_='main-button dlbutton')
            strurl = plink.get('href')
            if not any([x in strurl for x in non_str_list]):
                vidhost = get_vidhost(strurl)
                videos.append((vidhost,strurl))
        except:
            pass

        try:
            plink = csoup.find(class_='aio-pulse')
            strurl = plink.find('a')['href']
            if not any([x in strurl for x in non_str_list]):
                vidhost = get_vidhost(strurl)
                videos.append((vidhost,strurl))
        except:
            pass

        try:
            plink = csoup.find(class_='entry-content rich-content')
            strurl = plink.find('a')['href']
            if not any([x in strurl for x in non_str_list]):
                vidhost = get_vidhost(strurl)
                videos.append((vidhost,strurl))
        except:
            pass

        try:
            for linksSection in csoup.findAll('embed'):
                strurl = linksSection.get('src')
                if not any([x in strurl for x in non_str_list]):
                    vidhost = get_vidhost(strurl)
                    videos.append((vidhost,strurl))
        except:
            pass

    elif 'tamildbox' in url:
        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'embed-list',url))
        link = requests.get(url, headers=mozhdr).text
        try:
            mlink = SoupStrainer('div', {'id':'player-embed'})
            dclass = BeautifulSoup(link, parseOnlyThese=mlink)       
            if 'unescape' in str(dclass):
                etext = re.findall("unescape.'[^']*", str(dclass))[0]
                etext = urllib.unquote(etext)
                dclass = BeautifulSoup(etext)
            glink = dclass.iframe.get('src')
            vidhost = get_vidhost(glink)
            videos.append((vidhost,glink))
            mlink = SoupStrainer('div', {'class':'item-content toggled'})
            dclass = BeautifulSoup(link, parseOnlyThese=mlink)
            glink = dclass.p.iframe.get('src')
            vidhost = get_vidhost(glink)
            videos.append((vidhost,glink))
        except:
            pass
                
        try:
                rawJ = csoup.findAll('script')
                J = str(rawJ[4])
                rk=J.split('var mainVideo = ')[1].rsplit('var vastUrl =')[0].rsplit(';', 1)[0]
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'play-list',rk))
                strm_url=rk.replace('\'', '') 
                vidhost = get_vidhost(url)
                videos.append((vidhost,strm_url))
        except:
            pass


        try:
            codes = re.findall('"return loadEP.([^,]*),(\d*)',link)
            for ep_id, server_id in codes:
#                burl = 'http://www.tamildbox.com/actions.php?case=loadEP&ep_id=%s&server_id=%s'%(ep_id,server_id)
                burl = 'http://www.tamildbox.us/actions.php?case=loadEP&ep_id=%s&server_id=%s'%(ep_id,server_id)
                bhtml = requests.get(burl,headers=mozhdr).text
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'ep-url',bhtml))
                soup = BeautifulSoup(bhtml)
#               blin1k = re.findall('(?i)iframe\s*src="(.*?)"',bhtml)[0]
                blink = soup.find('iframe')['src']
                logging.warning("{0} {1} {2} {0}".format ('##'*15, 'ep-loaded-linkd',blink))
                vidhost = get_vidhost(blink)
                if 'googleapis' in blink:
                    blink = 'https://drive.google.com/open?id=' + re.findall('docid=([^&]*)',blink)[0]
                    vidhost = 'GVideo'
                    videos.append((vidhost,blink))   
                elif 'hls_stream' in blink:
                    resolve_media(blink,videos)
                elif 'player.php' in blink:
                    pass
                else:
                    videos.append((vidhost,blink))   


        except:
            pass

    elif not any([x in url for x in non_str_list]):
        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'embed-list',url))
        vidhost = get_vidhost(url)
        videos.append((vidhost,url))

    return

def get_site_categories():
    items = {}
    sno = 1
    items[str(sno)+'[COLOR blue]TAMILDBOX[/COLOR]'] = tamildboxurl 
    sno+=1
    items[str(sno)+'[COLOR blue]TAMILGUN[/COLOR]'] = tamilgunurl 
    return items

def get_categories():
    """
    Get the list of categories.
    :return: list
    """
#    bu = 'http://tamilgun.pro'
    bu = tamilgunurl
    r = requests.get(bu, headers=mozhdr)
    if r.url != bu:
        bu = r.url
    items = {}
    cats = re.findall('id="menu-item-[^4].*?href="((?=.*categories).*?)">((?!User).*?)<',r.text)
    sno = 1
    for cat in cats:
        items[str(sno)+cat[1]] = cat[0]
        sno+=1
    items[str(sno)+'[COLOR yellow]** Search **[/COLOR]'] = bu + '/?s='
        
    return items
    
def get_movies(iurl):
    """
    Get the list of movies.
    :return: list
    """
    movies = []
    
    logging.warning("{0} {1} {2} {0}".format ('##'*15, 'getmovies',iurl))
    if iurl[-3:] == '?s=':
        search_text = GetSearchQuery('TamilGun')
        search_text = urllib.quote_plus(search_text)
        iurl += search_text

    if 'tamildbox' in iurl:
        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'dbox-iurl',iurl))
        html = requests.get(iurl, headers=mozhdr).text
        tlink = SoupStrainer('div', {'class':re.compile('listbox')})
        items = BeautifulSoup(html, parseOnlyThese=tlink)       
        plink = SoupStrainer('div', {'class':'pagination'})
        Paginator = BeautifulSoup(html, parseOnlyThese=plink)

        for item in items:
            title = item.h4.text
            url = item.find( 'div', attrs={'class' : 'btn btn-primary watch'}).find('a', href=True)['href']
            try:
                thumb = item.find('img')['src'].strip()
            except:
                thumb = _icon
            movies.append((title, thumb, url))

        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'dbox-Pagintor',Paginator))
        if 'current' in str(Paginator):
            purl = Paginator.find('span', {'class':re.compile('current')}).findNext('a')['href']
            if 'http' not in purl:
                purl=url
            currpg = Paginator.find('span', {'class':re.compile('current')}).text
            lastpg = Paginator.findAll('a',text=True)[-1]
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg,lastpg)
            movies.append((title, _icon, purl))


    if 'gun' in iurl:
        if iurl == tamilgunurl:
            list_categories(iurl)

        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'tgun-iurl',iurl))
        html = requests.get(iurl, headers=mozhdr).text
        mlink = SoupStrainer('article', {'class':re.compile('video')})
        items = BeautifulSoup(html, parseOnlyThese=mlink)
        plink = SoupStrainer('ul', {'class':'page-numbers'})
        Paginator = BeautifulSoup(html, parseOnlyThese=plink)

        for item in items:
            title = item.h3.text
            url = item.h3.find('a')['href']
            try:
                thumb = item.find('img')['src'].strip()
            except:
                thumb = _icon
            movies.append((title, thumb, url))
        
        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'tgun-Pagintor',Paginator))
        if 'next' in str(Paginator):
            nextli = Paginator.find('a', {'class':re.compile('next')})
            logging.warning("{0} {1} {2} {0}".format ('##'*15, 'Pagintor',nextli))
            purl = nextli.get('href')
            if 'http' not in purl:
                purl = self.bu[:-12] + purl
            currpg = Paginator.find('span', {'class':re.compile('current')}).text
            pages = Paginator.findAll('a', {'class':re.compile('^page')})
            logging.warning("{0} {1} {2} {0}".format ('##'*15, 'Pages',pages))
            lastpg = pages[len(pages)-1].text
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg,lastpg)
            movies.append((title, _icon, purl))

    return movies


def get_videos(url):
    """
    Get the list of videos.
    :return: list
    """
    videos = []
    if 'cinebix.com' in url:
        resolve_media(url,videos)
        return videos

    if 'tamildbox' in url:
        resolve_media(url,videos)
        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'tamildbox-',url))
        return videos

    html = requests.get(url, headers=mozhdr).text

    try:
        linkcode = jsunpack.unpack(html).replace('\\','')
        sources = json.loads(re.findall('sources:(.*?)\}\)',linkcode)[0])
        for source in sources:    
            url = source['file'] + '|Referer=http://%s/'%get_vidhost(source['file'])
            url = urllib.quote_plus(url)
            videos.append(('tamilgun | %s'%source['label'],url))
    except:
        pass

    mlink = SoupStrainer('div', {'id':'videoframe'})
    videoclass = BeautifulSoup(html, parseOnlyThese=mlink)
    try:
        links = videoclass.findAll('iframe')
        for link in links:
            url = link.get('src')
            resolve_media(url,videos)
    except:
        pass

    mlink = SoupStrainer('div', {'class':'entry-excerpt'})
    videoclass = BeautifulSoup(html, parseOnlyThese=mlink)
    try:
        links = videoclass.findAll('iframe')
        for link in links:
            if 'http' in str(link):
                url = link.get('src')
                resolve_media(url,videos)
    except:
        pass

    try:
        url = videoclass.p.a.get('href')
        resolve_media(url,videos)
    except:
        pass    
    
    try:
        sources = json.loads(re.findall('vdf-data-json">(.*?)<',html)[0])
        url = 'https://www.youtube.com/watch?v=%s'%sources['videos'][0]['youtubeID']
        resolve_media(url,videos)
    except:
        pass
        
    return videos


def list_categories(iurl):
    """
    Create the list of categories in the Kodi interface.
    """
    
    if iurl == tamilgunurl:
        categories = get_categories()
        global _icon
        _icon = _addon.getAddonInfo('path').decode("utf-8") + "/tgun.png"
        
    else:
        categories = get_site_categories()
    listing = []
    for title,iurl in sorted(categories.iteritems()):
        list_item = xbmcgui.ListItem(label=title[1:])
        list_item.setArt({'thumb': _icon,
                          'icon': _icon,
                          'fanart': _fanart})
        url = '{0}?action=list_category&category={1}'.format(_url, urllib.quote(iurl))
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)


def list_movies(category):
    """
    Create the list of movies in the Kodi interface.
    """
    movies = get_movies(category)
    listing = []
    MenuItems = []
    for movie in movies:
        list_item = xbmcgui.ListItem(label=movie[0])
        list_item.setArt({'thumb': movie[1],
                          'icon': movie[1],
                          'fanart': movie[1]})
        list_item.setInfo('video', {'title': movie[0]})
        logging.warning("{0} {1} {2} {0}".format ('??'*15, 'list_movie',movie))
        if 'Next Page' in movie[0]:
            url = '{0}?action=list_category&category={1}'.format(_url, movie[2])
        else:
#            url = '{0}?action=list_movie&thumb={1}&movie={2}&title={3}'.format(_url, movie[1], movie[2], movie[0].encode('ascii', 'ignore').decode('ascii'))
            url = '{0}?action=list_movie&thumb={1}&movie={2}&title={3}'.format(_url, movie[1], movie[2], ''.join(e for e in movie[0] if e.isalnum()))

        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)
 
   
def list_videos(movie,thumb,title):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: str
    """

    logging.warning("{0} {1} {2} {0}".format ('##'*15, 'list_video_movie',movie))
    videos = get_videos(movie)
    listing = []
    for video in videos:
        list_item = xbmcgui.ListItem(label=video[0])
        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})
        list_item.setInfo('video', {'title': video[0]})
        list_item.setProperty('IsPlayable', 'true')
        url = '{0}?action=play&video={1}'.format(_url, video[1])
        durl = '{0}?action=download&video={1}&title={2}'.format(_url, video[1],title)
        caurl = '{0}?action=cancel&video={1}&title={2}'.format(_url, video[1],title)
        logging.warning("{0} {1} {2} {0}".format ('##'*15, 'list_video_get',durl))
        is_folder = False
        #MenuItems=[('Clearall','XBMC.RunScript(special://home/addons/plugin.video.tamilmovies/libs/commands.py,download,url)')]
        MenuItems=[('Download','XBMC.RunPlugin('+durl+')'),('Cancel Download','XBMC.RunPlugin('+caurl+')')]
       # CancelItems=[('Cancel Download','XBMC.RunPlugin('+caurl+')')]
        list_item.addContextMenuItems(MenuItems)
       # list_item.addContextMenuItems(CancelItems)
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def resolve_url(url):
    duration=7500   
    logging.warning("{0} {1} {2} {0}".format ('##'*15, 'resolveurl',url))
    try:
        stream_url = urlresolver.HostedMediaFile(url=url).resolve()
        # If urlresolver returns false then the video url was not resolved.
        if not stream_url or not isinstance(stream_url, basestring):
            try: msg = stream_url.msg
            except: msg = url
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('URL Resolver',msg, duration, _icon))
            return False
    except Exception as e:
        try: msg = str(e)
        except: msg = url
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('URL Resolver',msg, duration, _icon))
        return False
        
    return stream_url


def play_video(path):
    """
    Play a video by the provided path.

    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    logging.warning("{0} {1} {2} {0}".format ('&&'*15, 'playvid_url',play_item))
    vid_url = play_item.getfilename()
    if 'tamilgun' not in vid_url:
        stream_url = resolve_url(vid_url)
        if stream_url:
            play_item.setPath(stream_url)
    # Pass the item to the Kodi player.
    logging.warning("{0} {1} {2} {0}".format ('##'*15, 'play--video',stream_url))
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin

    if params:
        if params['action'] == 'list_category':
           if 'filter' in params['category']:
              list_movies( params['category']+'&page='+params.get("page",'1'))
           else:
               list_movies(params['category'])
        elif params['action'] == 'list_movie':
            list_videos(params['movie'],params['thumb'],params['title'])
        elif params['action'] == 'play':
            play_video(params['video'])
        elif params['action'] == 'download':
            logging.warning("{0} {1} {2} {0}".format ('##'*15, 'params',params))
            download(resolve_url(params['video']),_download_dir,params['title'],dp=None, headers=None, cookies=None, allow_redirects=True, verify=True, timeout=30, auth=None)
        elif params['action'] == 'cancel':
            logging.warning("{0} {1} {2} {0}".format ('##'*15, 'params',params))
            download(resolve_url(params['video']),_download_dir,params['title'],dp=None, headers=None, cookies=None, allow_redirects=True, verify=False, timeout=30, auth=None)
    else:
        list_categories(iurl='test')


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
