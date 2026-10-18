from pathlib import Path
import sys

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gsk', '4.0')
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, Gio, Gsk, Gtk

Gtk.disable_setlocale()

prefix = Path(sys.prefix)
if sys.platform == "win32":
    prefix /= "Library"
schemas = Gio.SettingsSchemaSource.new_from_directory(
    str(prefix / "share/glib-2.0/schemas"), None, False
)
for name in ("FileChooser", "ColorChooser", "EmojiChooser"):
    schema_id = f"org.gtk.gtk4.Settings.{name}"
    assert schemas.lookup(schema_id, False) is not None, schema_id
    Gio.Settings.new(schema_id)
