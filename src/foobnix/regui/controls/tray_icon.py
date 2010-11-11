#-*- coding: utf-8 -*-
'''
Created on 29 сент. 2010

@author: ivan
'''
from foobnix.regui.model.signal import FControl
import gtk
from foobnix.util.fc import FC
from foobnix.helpers.toolbar import MyToolbar
from foobnix.util.mouse_utils import is_middle_click
from foobnix.regui.state import LoadSave
import gobject
from foobnix.helpers.image import ImageBase
from foobnix.regui.model import FModel
from foobnix.helpers.pref_widgets import VBoxDecorator, IconBlock
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.util.const import STATE_STOP, STATE_PLAY, STATE_PAUSE, FTYPE_RADIO
 
class PopupWindowMenu(gtk.Window, FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window. __init__(self, gtk.WINDOW_POPUP)

        self.set_position(gtk.WIN_POS_MOUSE)

        self.connect("leave-notify-event", self.on_leave_window)

        vbox = gtk.VBox(False, 0)

        toolbar = MyToolbar()
        toolbar.add_button("Exit", gtk.STOCK_QUIT, self.controls.quit, None)
        toolbar.add_separator()
        toolbar.add_button("Stop", gtk.STOCK_MEDIA_STOP, self.controls.state_stop, None)
        toolbar.add_button("Play", gtk.STOCK_MEDIA_PLAY, self.controls.state_play, None)
        toolbar.add_button("Pause", gtk.STOCK_MEDIA_PAUSE, self.controls.state_pause, None)
        toolbar.add_button("Previous", gtk.STOCK_MEDIA_PREVIOUS, self.controls.prev, None)
        toolbar.add_button("Next", gtk.STOCK_MEDIA_NEXT, self.controls.next, None)
        toolbar.add_separator()
        toolbar.add_button("Close Popup", gtk.STOCK_OK, lambda * a:self.hide(), None)

        self.poopup_text = gtk.Label("Foobnix")
        self.poopup_text.set_line_wrap(True)

        vbox.pack_start(toolbar, False, False)
        vbox.pack_start(self.poopup_text, False, False)
        self.add(vbox)
        self.show_all()
        self.hide()
        
    def set_text(self, text):
        self.poopup_text.set_text(text)

    def on_leave_window(self, w, event):
        print w, event
        max_x, max_y = w.size_request()
        x, y = event.x, event.y
        if 0 < x < max_x and 0 < y < max_y:
            return True
        print "hide"
        self.hide()


class TrayIconControls(gtk.StatusIcon, ImageBase, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.StatusIcon.__init__(self)
        ImageBase.__init__(self, "foobnix_icon.svg", 150)
                
        self.set_has_tooltip(True)
        self.tooltip = gtk.Tooltip()
        self.set_tooltip("Foobnix music player")
        
        self.popup_menu = PopupWindowMenu(self.controls)
        print "IN TRAYICON"
        '''static_icon'''
        self.static_icon = IconBlock("Icon", controls, FC().static_icon_entry)
        
        """dynamic icons"""
        self.play_icon = IconBlock("Play", controls, FC().play_icon_entry)
        self.pause_icon = IconBlock("Pause", controls, FC().pause_icon_entry)
        self.stop_icon = IconBlock("Stop", controls, FC().stop_icon_entry)
        self.radio_icon = IconBlock("Radio", controls, FC().radio_icon_entry)
        
        self.connect("activate", self.on_activate)
        self.connect("popup-menu", self.on_popup_menu)

        self.connect("button-press-event", self.on_button_press)
        self.connect("scroll-event", self.controls.volume.on_scroll_event)
        self.connect("query-tooltip", self.on_query_tooltip)
        
        self.current_bean = FModel().add_artist("Artist").add_title("Title")
        self.tooltip_image = ImageBase("foobnix-big.png", 150)
        
    def on_save(self):
        FC().static_icon_entry = self.static_icon.entry.get_text()
        FC().play_icon_entry = self.play_icon.entry.get_text()
        FC().pause_icon_entry = self.pause_icon.entry.get_text()
        FC().stop_icon_entry = self.stop_icon.entry.get_text()
        FC().radio_icon_entry = self.radio_icon.entry.get_text()
        
  
    def on_load(self):
        if FC().show_tray_icon:
            self.show()
        else:
            self.hide()
        
        self.static_icon.entry.set_text(FC().static_icon_entry)
        #self.static_icon.combobox.set_active(FC().static_icon_entry[1])
        self.play_icon.entry.set_text(FC().play_icon_entry)
        #self.play_icon.combobox.set_active(FC().play_icon_entry[1])
        self.pause_icon.entry.set_text(FC().pause_icon_entry)
        #self.pause_icon.combobox.set_active(FC().pause_icon_entry[1])
        self.stop_icon.entry.set_text(FC().stop_icon_entry)
        #self.stop_icon.combobox.set_active(FC().stop_icon_entry[1])
        self.radio_icon.entry.set_text(FC().radio_icon_entry)
        #self.radio_icon.combobox.set_active(FC().radio_icon_entry[1])
        
    def update_info_from(self, bean):
        self.current_bean = bean
        self.tooltip_image.update_info_from(bean)
        if FC().change_tray_icon:
            super(TrayIconControls, self).update_info_from(bean)
            
    def on_dynamic_icons(self, state):
        if FC().static_tray_icon:
            self.check_active_dynamic_icon(self.static_icon)
        if FC().system_icons_dinamic:
            if state == FTYPE_RADIO:
                self.check_active_dynamic_icon(self.radio_icon)
            elif state == STATE_PLAY:
                self.check_active_dynamic_icon(self.play_icon)
            elif state == STATE_PAUSE:
                self.check_active_dynamic_icon(self.pause_icon)
            elif state == STATE_STOP:
                self.check_active_dynamic_icon(self.stop_icon)

    def check_active_dynamic_icon(self, icon_object):
        icon_name = icon_object.entry.get_text()
        path = get_foobnix_resourse_path_by_name(icon_name)
        self.controls.trayicon.set_image_from_path(path)
        
    def on_query_tooltip(self, widget, x, y, keyboard_tip, tooltip):
        artist = "Artist"
        title = "Title"
        if self.current_bean:
            artist = self.current_bean.artist
            title = self.current_bean.title
        
        alabel = gtk.Label()
        alabel.set_markup("<b>%s</b>" % artist)
                
        vbox = VBoxDecorator(gtk.Label(), alabel, gtk.Label(), gtk.Label(title))        
        
        tooltip.set_icon(self.tooltip_image.get_pixbuf())
        tooltip.set_custom(vbox)
        return True
        
    def on_activate(self, *a):
        self.controls.windows_visibility()

    def on_button_press(self, w, e):
        if is_middle_click(e):            
            self.controls.play_pause()

    def hide(self):
        self.set_visible(False)

    def show(self):
        self.set_visible(True)

    def show_window(self, *a):
        self.popup_menu.reshow_with_initial_size()
        self.popup_menu.show()
        print "show"

    def hide_window(self, *a):
        self.popup_menu.hide()
        print "hide"

    def on_popup_menu(self, *a):
        self.show_window()

    def set_text(self, text):
        def task():
            self.popup_menu.set_text(text)
            self.set_tooltip(text)
        gobject.idle_add(task)   
