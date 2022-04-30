# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcgui
import xbmcaddon
import xbmcgui as gui
import xbmcplugin as plugin
import datetime
import urllib
import xbmc
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from database import Neo4j
import os
import sys

_url = sys.argv[0]
addon = xbmcaddon.Addon()
ADDON_NAME = addon.getAddonInfo('name')
CWD = addon.getAddonInfo('path')

host_name = addon.getSetting(id='neo4j-host')
port = int(addon.getSetting(id='neo4j-port'))
user = addon.getSetting(id='neo4j-user')
password = addon.getSetting(id='neo4j-password')
# cbz_files_dir = addon.getSetting(id='cbz-files-dir')
# cbz_thumbs_dir = addon.getSetting(id='cbz-thumbs-dir')
cbz_files_dir = 'sftp://192.168.1.40:22/DATA/test2/documents/'
cbz_thumbs_dir = 'sftp://192.168.1.40:22/DATA/test2/documents/thumbs/'


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_project_path():
    return os.path.dirname(os.path.abspath(__file__))


def error_message():
    dialog = gui.Dialog()
    dialog.ok(ADDON_NAME, 'ERROR hay')


def log(msg):
    xbmc.log('CulturaComics Plugin: %s' % msg)


def get_gui_items(data):
    items = []
    for record in data:
        media = record['media']
        for relationship in record['relationships']:
            if relationship.type == 'HAS_AUTHOR':
                author = relationship.end_node
            elif relationship.type == 'HAS_COLLECTION':
                collection = relationship.end_node
        # cbz_file = cbz_files_dir + media.get('mediaId') + '.cbz'
        cbz_thumb = cbz_thumbs_dir + media.get('mediaId') + '.jpg'
        # file_time = datetime.datetime.fromtimestamp(os.path.getmtime(cbz_file))
        item = gui.ListItem(label=media.get('mediaId'))
        item.setInfo('pictures', {
                'title': media.get('name'),
                # 'size': os.path.getsize(cbz_file),
                # 'date': file_time.strftime("%d.%m.%Y"),
            }
         )
        item.setArt({'thumb': cbz_thumb, 'icon': cbz_thumb, 'fanart': cbz_thumb})
        item.setProperty('IsPlayable', 'true')
        items.append(item)
    return items


def play_comic(media):
    url = urllib.parse.quote_plus(cbz_files_dir) + media + ".cbz"
    xbmc.executebuiltin('SlideShow("zip://' + url + '", pause)'.format(media))


def list_items():
    # tmp_cover = get_project_path() + '/tmp/'
    scheme = "neo4j"
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    bd = Neo4j(url, user, password)
    medias = bd.list_last()
    last = get_gui_items(medias)
    medias = bd.list_by_author('slasher')
    slasher = get_gui_items(medias)
    medias = bd.list_by_author('fernando')
    fernando = get_gui_items(medias)
    bd.close()
    window = GUI('script-main-window.xml', CWD, 'default', '1080i', True, control1=last, control2=slasher, control3=fernando)
    window.doModal()
    del window


class GUI(gui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.control1 = kwargs['control1']
        self.control2 = kwargs['control2']
        self.control3 = kwargs['control3']

    def onInit(self):
        self.cont1 = self.getControl(100)
        self.cont2 = self.getControl(200)
        # self.cont3 = self.getControl(300)
        self.cont1.addItems(self.control1)
        self.cont2.addItems(self.control2)
        # self.cont3.addItems(self.control3)
        xbmc.sleep(100)
        self.setFocusId(self.getCurrentContainerId())

    def onClick(self, control_id):
        if control_id == 100 or control_id == 200:
            control_list = self.getControl(control_id)
            item = control_list.getSelectedItem()
            media_id = item.getLabel()
            play_comic(media_id)


if __name__ == '__main__':
    list_items()
# the end!
