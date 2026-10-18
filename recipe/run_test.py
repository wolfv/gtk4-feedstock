import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

# Prove the private cache works without globally installed or user schemas.
isolated = TemporaryDirectory()
for variable in ("XDG_DATA_DIRS", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "GSETTINGS_SCHEMA_DIR"):
    os.environ[variable] = isolated.name
os.environ["GSETTINGS_BACKEND"] = "memory"

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gsk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gsk, Gtk

prefix = Path(sys.prefix)
if sys.platform == "win32":
    prefix /= "Library"
source = Gio.SettingsSchemaSource.new_from_directory(
    str(prefix / "share/gtk-4.0/schemas"), None, False
)
for name in ("Settings.FileChooser", "Settings.ColorChooser", "Settings.EmojiChooser",
             "Settings.Debug", "Inspector.Recorder"):
    schema_id = f"org.gtk.gtk4.{name}"
    schema = source.lookup(schema_id, False)
    assert schema is not None, schema_id
    Gio.Settings.new_full(schema, None, None)
    default = Gio.SettingsSchemaSource.get_default()
    assert default is None or default.lookup(schema_id, True) is None

# Native desktop runners also exercise GTK's fallback, not just the cache format.
if Gtk.init_check():
    dialog = Gtk.FileChooserDialog(action=Gtk.FileChooserAction.SAVE)
    settings = Gio.Settings.new_full(
        source.lookup("org.gtk.gtk4.Settings.ColorChooser", False), None, None
    )
    settings.set_value("selected-color", GLib.Variant("(bdddd)", (True, 1., 0., 0., 1.)))
    color = Gtk.ColorChooserWidget()
    assert color.get_rgba().red == 1. and color.get_rgba().green == 0.
    emoji = Gtk.EmojiChooser()
    dialog.destroy()

    # A normal shared schema (including its overrides) must take precedence.
    schema_dir = prefix / "share/glib-2.0/schemas"
    shutil.copy(schema_dir / "org.gtk.gtk4.Settings.ColorChooser.gschema.xml", isolated.name)
    Path(isolated.name, "test.gschema.override").write_text(
        "[org.gtk.gtk4.Settings.ColorChooser]\n"
        "selected-color=(true, 0.0, 1.0, 0.0, 1.0)\n"
    )
    subprocess.run(["glib-compile-schemas", isolated.name], check=True)
    subprocess.run([sys.executable, "-c", """
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
Gtk.init()
color = Gtk.ColorChooserWidget()
assert color.get_rgba().red == 0. and color.get_rgba().green == 1.
"""], check=True)
    print("GTK chooser fallback, saved preferences and shared overrides passed")
else:
    print("No display: checked private schemas; chooser tests require a desktop")
