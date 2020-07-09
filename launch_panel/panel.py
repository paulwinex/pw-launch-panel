"""
Simple launching panel GUI
"""
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import json
from functools import partial
from pathlib import Path
from launch_panel.launcher import launch_app

readme_url = '#'
# text whit buttons not configured
no_buttons_text = '<h1>NO BUTTONS</h1><br><a href="{}" style="color: gray">How to add?</a>'.format(readme_url)
# text for help window
help_text = '''<h2>Simple Launch Panel</h2>
by <a href="https://paulwinex.com" style="color: gray">Paulwinex</a>

Using:
1. Create file "settings/buttons.json and add your apps. Use buttons_example.json as reference.
2. Use Middle Mouse Button to move panel
3. Use Left click on buttons to launch default app and Right Click to select specific app. 

Full readme: <a href="{}" style="color: gray">???</a>

'''.format(readme_url)

class LaunchPanelClass(QMainWindow):
    """
    Simple launch panel class
    """
    _prefs_file = Path('~/.launch_panel_prefs.json').expanduser()  # saved preferences

    def __init__(self):
        super(LaunchPanelClass, self).__init__()    # call constructor of parent class
        ### VARIABLES
        self.anim = True
        # base path to icons
        self.icon_path = Path(__file__).parent / 'icons'
        # settings dict
        self.settings = self.load_settings()
        # drag variables
        self._is_moved = False
        self._last_pos = None

        ################### BUTTONS
        buttons = self.load_buttons()
        # if buttons:
        self.init_panel(buttons)

        ################# TIMERS
        self.hideTimer = QTimer()
        self.hideTimer.timeout.connect(self.hide_window)

        ## UI
        # set custom ui style
        self.set_style()
        # add window flags: tool dialog,   no window frames,       always on top
        self.setWindowFlags(Qt.Tool |      Qt.FramelessWindowHint| Qt.WindowStaysOnTopHint)
        self.__help_dialog = HelpWindow(self)   # this is help window

        ## Show
        self.resize(10, 10) # make small size, window will be expanded later when widgets will added
        self.show_panel(True)   # open panel on startup
        self.hide_timer_start(self.settings['hide_timeout'])    # hide with timeout

    def load_settings(self):
        """
        Load UI settings
        """
        default_file = Path(__file__).parent / 'settings' / 'default_ui.json'   # default settings
        custom_file = Path(__file__).parent / 'settings' / 'custom_ui.json'     # user overrides
        s = json.load(default_file.open())      # load settings from JSON
        if custom_file.exists():
            s.update(json.load(custom_file.open()))     # extend settings from custom file
        return s

    def init_panel(self, buttons):
        """
        Init buttons on panel
        """
        # central widget
        w = QWidget(self)
        self.setCentralWidget(w)
        ly = QHBoxLayout()
        w.setLayout(ly)
        ly.setContentsMargins(*self.settings['panel_padding'])      # padding from settings
        ly.setSpacing(self.settings['button_spacing'])      # spacing from settings
        # app buttons
        if buttons: # buttons exists
            for name, opt in buttons.items():
                but = QPushButton() # create widget
                ly.addWidget(but)   # add to layout
                but.setFixedSize(QSize(self.settings['button_size'],self.settings['button_size']))  # set fixed size
                # add icon
                icon = Path(opt['icon'])
                if not icon.is_absolute():
                    icon = self.icon_path / icon
                ico = QIcon(str(icon))
                but.setIconSize(QSize(self.settings['button_size']*0.8,self.settings['button_size']*0.8))   # set icon size
                but.setIcon(ico)
                but.setToolTip(opt.get('tooltip', name.title()))    # set tooltip
                but.clicked.connect(partial(self.launch_default, opt))  # set button callback
                but.setContextMenuPolicy(Qt.CustomContextMenu)  # allow custom context menu
                but.customContextMenuRequested.connect(partial(self.button_context_menu, opt))  # add right click callback

            self.set_geo(len(buttons))  # resize window
        else:   # buttons not exists
            lb = QLabel(no_buttons_text, alignment=Qt.AlignHCenter|Qt.AlignVCenter)
            # set link clickable
            lb.setTextInteractionFlags(Qt.TextBrowserInteraction)
            lb.setOpenExternalLinks(True)
            ly.addWidget(lb)
        # close button
        but = QPushButton()
        but.setFixedSize(QSize(10,int(self.settings['height'])))    # small button on right of panel
        ly.addWidget(but)
        but.clicked.connect(self.on_close)  # connect to exit

    def on_close(self):
        """Save position on exit"""
        self._save_geo()
        QApplication.quit()

    def button_context_menu(self, data, *args):
        """Context menu for button"""
        if len(data['commands']) == 1:
            # dont open meu if button has only one command
            return
        menu = QMenu(self)
        # iterate commands
        for data in data['commands']:
            # add action to the menu
            menu.addAction(
                # create new action
                QAction(data['title'], self,
                          # add callback for action
                          triggered=partial(self.launch_app, data))

                )
        # show menu
        menu.exec_(QCursor.pos())

    def load_buttons(self):
        """Read button options"""
        # get buttons config file
        buttonsFile = Path(__file__).parent / 'settings' / 'buttons.json'
        if buttonsFile.exists():
            return json.load(buttonsFile.open())
        else:
            # error
            QMessageBox.critical(self, 'Error', 'No buttons file')

    def launch_default(self, data):
        """Run default app from array of apps"""
        for item in data['commands']:
            # looking for default command
            if item.get('default'):
                app_data = item
                break
        else:
            # if default not set
            # use first command
            app_data = data['commands'][0]
        self.launch_app(app_data)

    def launch_app(self, data):
        """Launch selected app"""
        # send data to launch script
        launch_app(data['executable'], args=data.get('args'), env=data.get('env'))

    def anim_transparency(self, start=1, end=0.01, d=None):
        """Start transparency animation"""
        # get animation speed
        d = d or self.settings['animation_speed']
        if start is False:
            # get current value to continue animation
            start = self.windowOpacity()
        # animate property
        anim = QPropertyAnimation(self, QByteArray(b"windowOpacity"), self)
        anim.setStartValue(start)   # from start value
        anim.setEndValue(end)       # to end value
        anim.setDuration(d)         # in this time duration
        anim.start()                # GO!

    def show_panel(self, full_opacity=False):
        """Show panel"""

        if full_opacity:
            # disable opacity
            self.setWindowOpacity(1)
        else:
            # set opacity from settings
            self.setWindowOpacity(self.settings['transparency'])

        if self.anim:
            # enable animation on show
            self.show_hide_animation(1)
        self.show()

    def hide_window(self):
        """Hide panel"""
        self.hide_time_stop()   # disable timer
        if not self.check_cursor():
            # set no focus transparency
            self.setWindowOpacity(self.settings['transparency'])
            # start hiding animation
            self.show_hide_animation(0)

    def show_hide_animation(self, direct):
        """Start slide animation"""
        # start pos
        opened = QPoint(self.pos().x(), self.settings['padding_top'])
        # end pos
        closed = QPoint(self.pos().x(),-self.settings['height']+2)
        # animate property pos
        anim = QPropertyAnimation(self, QByteArray(b'pos'), self)
        # finish callback
        anim.finished.connect(partial(self.allow_anim, direct))
        # select direction
        if not direct:
            anim.setStartValue(opened)  # from
            anim.setEndValue(closed)    # to
        else:
            anim.setStartValue(closed)  # from
            anim.setEndValue(opened)    # to
        anim.setDuration(self.settings['animation_speed'])  # set duration
        self.anim = not direct  # switch anim enabled
        # GO!
        anim.start()

    def allow_anim(self, val):
        """Trigger on end of animation"""
        self.anim = not val     # set animation enabled
        if self.geometry().y() < 0:
            # null opacity if window is hidden
            self.setWindowOpacity(0.01)

    def set_geo(self, count=None):
        """Move to saved or default position"""
        # read from file
        pos = self._load_geo()
        if pos:
            # move to saved position
            self.move(pos['x'], pos['y'])
        else:
            # move to default position
            geo = QDesktopWidget().screenGeometry()     # get screen size
            w = count * self.settings['button_size']    # get panel width
            x = geo.width()/2 - (w/2)                   # compute left side position (x)
            self.move(x, 0)                             # move

    def hide_timer_start(self, timeout=None):
        """Hide with timeout (on cursor leave)"""
        self.hideTimer.start(timeout or self.settings['hide_timeout'])

    def hide_time_stop(self):
        """Stop timer for hiding (on cursor back)"""
        self.hideTimer.stop()

    def open_menu(self):
        """Open menu for panel (not buttons)"""
        # open panel menu if bo button under cursor
        if not isinstance(QApplication.widgetAt(QCursor.pos()), QPushButton):
            menu = QMenu(self)
            # add actions
            menu.addAction(QAction('Help', self, triggered=self.__help_dialog.show))
            menu.addAction(QAction('Exit', self, triggered=self.on_close))
            # show menu
            menu.exec_(QCursor.pos())

    def check_cursor(self):
        """Check if cursor under panel"""
        rec = self.geometry()       # get current geometry
        point = QCursor.pos()       # get cursor pos
        return rec.contains(point)  # check intersection


    def set_style(self):
        """Get nice panel stylesheet"""
        style = ''
        path = Path(__file__).parent / 'res' / 'style.qss'  # type: Path
        if path.exists():
            style += path.read_text()
        path2 = Path(__file__).parent / 'res' / 'custom_style.qss'  # type: Path
        if path2.exists():
            style += path2.read_text()
        # update panel style
        self.setStyleSheet(style)

    def enterEvent(self, event):
        """Stop hiding on cursor is up"""
        self.hideTimer.stop()   # disable hiding
        self.show_panel(True)   # show no transparency
        QWidget.enterEvent(self,event)

    def leaveEvent(self, event):
        """Start hiding timeout"""
        # start timer
        self.hide_timer_start(self.settings['hide_timeout'])
        # animate transparency to down
        self.anim_transparency(False, self.settings['transparency'], self.settings['animation_speed'])
        QWidget.leaveEvent(self, event)

    def keyPressEvent(self, event):
        """Exit on ESC"""
        if event.key() == Qt.Key_Escape:
            # exit
            self.on_close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:   # is middle click
            # set dragging by middle button is active
            self._is_moved = True
            # save click position here, because mouseMoveEvent has no position parameter
            self._last_pos = event.globalPos()
        elif event.button() == Qt.RightButton:  # is right click
            # open panel menu
            self.open_menu()
        super(LaunchPanelClass, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_moved:
            # move panel
            event_pos = event.globalPos()       # get click pos
            dist = self._last_pos - event_pos   # compute difference
            new_pos = self.pos() - dist         # add diff to current panel position
            new_pos.setY(self.pos().y())        # reset Y
            self.move(new_pos)                  # move panel
            self._last_pos = event_pos          # save previous pos
        super(LaunchPanelClass, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # reset drag options
        self._is_moved = False
        self._last_pos = None
        super(LaunchPanelClass, self).mouseReleaseEvent(event)

    def _save_geo(self):
        """Save last position"""
        geo = self.pos()
        json.dump(dict(x=geo.x(), y=geo.y()), self._prefs_file.open('w'), indent=2)

    def _load_geo(self):
        """Load last position"""
        if self._prefs_file.exists():
            return json.load(self._prefs_file.open())


class HelpWindow(QWidget):
    """Help Window"""
    def __init__(self, *args):
        super(HelpWindow, self).__init__(*args)
        self.setWindowFlags(Qt.Tool)    # set dialog type
        self.setWindowTitle('Help')     # set dialog title text
        # add layout
        self.ly = QVBoxLayout(self)
        # add label
        self.text = QLabel()
        self.text.setTextInteractionFlags(Qt.TextBrowserInteraction)    # send link clicks to browser
        self.text.setOpenExternalLinks(True)                            # make links works
        self.ly.addWidget(self.text)
        # set label text
        self.text.setText(help_text.replace('\n', '<br>'))  # convert new lint to <br> tag for HTML view
        # add close btn
        self.ly.addWidget(QPushButton('Close', clicked=self.close)) # close() method for Qt.Tool dialog is equal hide()

    def showEvent(self, event):
        # compute position under panel
        par = self.parent().pos()   # parent pos
        x = par.x() + int((self.parent().width()/2) - (self.width() / 2)) # move center of window under center of panel
        y = self.parent().settings['height'] + 100    # 100 pixels under panel
        self.move(x, y) # move before showing
        super(HelpWindow, self).showEvent(event)



