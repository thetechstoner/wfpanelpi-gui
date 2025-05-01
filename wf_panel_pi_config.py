import configparser
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

CONFIG_PATH = os.path.expanduser('~/.config/wf-panel-pi.ini')
APPLICATIONS_DIR = '/usr/share/applications'
ICON_SIZE = 24  # pixels

def get_icon_name_from_desktop(desktop_file):
    """Extract the Icon field from a .desktop file."""
    desktop_path = os.path.join(APPLICATIONS_DIR, desktop_file)
    if os.path.exists(desktop_path):
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(desktop_path)
            if parser.has_section('Desktop Entry') and parser.has_option('Desktop Entry', 'Icon'):
                return parser.get('Desktop Entry', 'Icon')
        except Exception:
            pass
    return None

def scale_pixbuf(pixbuf, size):
    """Scale a pixbuf to (size, size) if needed."""
    if pixbuf is None:
        return None
    if pixbuf.get_width() != size or pixbuf.get_height() != size:
        return pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
    return pixbuf

def load_icon_pixbuf(icon_name):
    """Try to load a GdkPixbuf for the given icon name or file path, always scaling to ICON_SIZE."""
    icon_theme = Gtk.IconTheme.get_default()
    pixbuf = None
    if icon_name:
        # Try loading as a themed icon
        if icon_theme.has_icon(icon_name):
            try:
                pixbuf = icon_theme.load_icon(icon_name, ICON_SIZE, 0)
            except Exception:
                pass
        # Try loading as a file path
        if pixbuf is None and os.path.exists(icon_name):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_name, ICON_SIZE, ICON_SIZE)
            except Exception:
                pass
    # Fallback
    if pixbuf is None:
        try:
            pixbuf = icon_theme.load_icon('application-x-executable', ICON_SIZE, 0)
        except Exception:
            pixbuf = None
    return scale_pixbuf(pixbuf, ICON_SIZE)

class WfPanelPiConfig(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="wf-panel-pi Configurator")
        self.set_border_width(10)
        self.set_default_size(500, 350)

        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(CONFIG_PATH)
        self.launchers = self.get_launchers()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # ListStore: icon (Pixbuf), launcher name (str)
        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        for launcher in self.launchers:
            icon_pixbuf = self.get_launcher_pixbuf(launcher)
            self.liststore.append([icon_pixbuf, launcher])

        self.treeview = Gtk.TreeView(model=self.liststore)

        # Icon column
        renderer_icon = Gtk.CellRendererPixbuf()
        column_icon = Gtk.TreeViewColumn("Icon", renderer_icon, pixbuf=0)
        self.treeview.append_column(column_icon)

        # Name column
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Launcher", renderer_text, text=1)
        self.treeview.append_column(column_text)

        # Enable drag-and-drop reordering
        self.treeview.set_reorderable(True)

        vbox.pack_start(self.treeview, True, True, 0)

        # Control buttons
        button_box = Gtk.Box(spacing=6)
        vbox.pack_start(button_box, False, False, 0)

        self.add_button = Gtk.Button(label="Add Launcher")
        self.add_button.connect("clicked", self.on_add_launcher)
        button_box.pack_start(self.add_button, True, True, 0)

        self.remove_button = Gtk.Button(label="Remove Selected")
        self.remove_button.connect("clicked", self.on_remove_launcher)
        button_box.pack_start(self.remove_button, True, True, 0)

        # Save button
        self.save_button = Gtk.Button(label="Save Configuration")
        self.save_button.connect("clicked", self.on_save)
        vbox.pack_start(self.save_button, False, False, 10)

    def get_launchers(self):
        if 'panel' in self.config:
            # Sort by key to maintain order
            return [self.config['panel'][key]
                    for key in sorted(self.config['panel'])
                    if key.startswith('launcher_')]
        return []

    def get_launcher_pixbuf(self, launcher):
        icon_name = get_icon_name_from_desktop(launcher)
        return load_icon_pixbuf(icon_name)

    def on_add_launcher(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select .desktop File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_current_folder(APPLICATIONS_DIR)
        dialog.set_filter(self.desktop_file_filter())
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            selected_file = dialog.get_filename()
            if selected_file.endswith('.desktop'):
                filename = os.path.basename(selected_file)
                icon_pixbuf = self.get_launcher_pixbuf(filename)
                self.liststore.append([icon_pixbuf, filename])

        dialog.destroy()

    def desktop_file_filter(self):
        file_filter = Gtk.FileFilter()
        file_filter.set_name("Desktop files")
        file_filter.add_pattern("*.desktop")
        return file_filter

    def on_remove_launcher(self, button):
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            model.remove(treeiter)

    def on_save(self, button):
        # Ensure panel section exists
        if 'panel' not in self.config:
            self.config.add_section('panel')

        # Clear existing launchers
        for key in list(self.config['panel']):
            if key.startswith('launcher_'):
                del self.config['panel'][key]

        # Add current launchers in their current order
        for idx, row in enumerate(self.liststore):
            launcher_id = f'launcher_{idx+1:06d}'
            self.config['panel'][launcher_id] = row[1]

        # Write to file
        with open(CONFIG_PATH, 'w') as configfile:
            self.config.write(configfile)

        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Configuration Saved"
        )
        dialog.format_secondary_text(f"Settings saved to {CONFIG_PATH}")
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    win = WfPanelPiConfig()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
