import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

isolated = TemporaryDirectory()
os.environ["XDG_CONFIG_HOME"] = isolated.name
os.environ["XDG_DATA_HOME"] = isolated.name
os.environ["GSETTINGS_BACKEND"] = "memory"

prefix = Path(sys.prefix)
data_prefix = prefix / "Library" if sys.platform == "win32" else prefix
private = str(data_prefix / "share/gtk-4.0/schemas")
assert private in os.environ.get("GSETTINGS_SCHEMA_DIR", "").split(os.pathsep)
cache = Path(private, "gschemas.compiled")
before = cache.read_bytes()

# Check activation and restoration with unset, empty and custom search paths.
for previous in (None, "", os.pathsep.join(("custom schemas", "other schemas"))):
    env = dict(os.environ, CONDA_PREFIX=str(prefix))
    env.pop("GSETTINGS_SCHEMA_DIR", None)
    if previous is not None:
        env["GSETTINGS_SCHEMA_DIR"] = previous
    env["EXPECTED_ACTIVE"] = (previous + os.pathsep if previous else "") + private
    env["EXPECTED_RESTORED"] = previous or ""
    active_check = "import os; assert os.environ['GSETTINGS_SCHEMA_DIR'] == os.environ['EXPECTED_ACTIVE']"
    restored_check = "import os; assert os.environ.get('GSETTINGS_SCHEMA_DIR', '') == os.environ['EXPECTED_RESTORED']; assert 'GTK4_GSETTINGS_SCHEMA_DIR_CONDA_BACKUP' not in os.environ"
    scripts = prefix / "etc/conda"
    if sys.platform == "win32":
        activate = scripts / "activate.d/zz-gtk4_activate.bat"
        deactivate = scripts / "deactivate.d/zz-gtk4_deactivate.bat"
        command = (f'call "{activate}" && "{sys.executable}" -c "{active_check}" && '
                   f'call "{deactivate}" && "{sys.executable}" -c "{restored_check}"')
        subprocess.run(command, shell=True, env=env, check=True)
    else:
        subprocess.run([
            "sh", "-ec", '. "$1"; "$3" -c "$4"; . "$2"; "$3" -c "$5"', "activation-test",
            str(scripts / "activate.d/zz-gtk4_activate.sh"),
            str(scripts / "deactivate.d/zz-gtk4_deactivate.sh"),
            sys.executable, active_check, restored_check,
        ], env=env, check=True)

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gsk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gsk, Gtk

# Ordinary GSettings clients and the CLI must discover every packaged schema.
cli_schemas = set(subprocess.check_output(["gsettings", "list-schemas"], text=True).splitlines())
for schema_id in (
    "org.gtk.gtk4.Settings.FileChooser", "org.gtk.gtk4.Settings.ColorChooser",
    "org.gtk.gtk4.Settings.EmojiChooser", "org.gtk.gtk4.Settings.Debug",
    "org.gtk.gtk4.Inspector.Recorder", "org.gtk.Demo4.Application",
):
    assert schema_id in cli_schemas, schema_id
    Gio.Settings.new(schema_id)

if Gtk.init_check() and Gdk.Display.get_default() is not None:
    dialog = Gtk.FileChooserDialog(action=Gtk.FileChooserAction.SAVE)
    settings = Gio.Settings.new("org.gtk.gtk4.Settings.ColorChooser")
    settings.set_value("selected-color", GLib.Variant("(bdddd)", (True, 1., 0., 0., 1.)))
    color = Gtk.ColorChooserWidget()
    assert color.get_rgba().red == 1. and color.get_rgba().green == 0.
    emoji = Gtk.EmojiChooser()
    dialog.destroy()

# Existing earlier search paths and their overrides must keep precedence.
shutil.copy(data_prefix / "share/glib-2.0/schemas/org.gtk.gtk4.Settings.ColorChooser.gschema.xml", isolated.name)
Path(isolated.name, "test.gschema.override").write_text(
    "[org.gtk.gtk4.Settings.ColorChooser]\n"
    "selected-color=(true, 0.0, 1.0, 0.0, 1.0)\n"
)
subprocess.run(["glib-compile-schemas", isolated.name], check=True)
subprocess.run([sys.executable, "-c", """
from gi.repository import Gio
color = Gio.Settings.new('org.gtk.gtk4.Settings.ColorChooser')
assert color.get_value('selected-color').unpack() == (True, 0., 1., 0., 1.)
"""], env=dict(os.environ, GSETTINGS_SCHEMA_DIR=isolated.name + os.pathsep + os.environ["GSETTINGS_SCHEMA_DIR"]), check=True)
assert cache.read_bytes() == before
print("Schema discovery, activation/restoration, preferences and overrides passed")
