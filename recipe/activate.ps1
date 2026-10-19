# shortcut: single-level backups match libglib; revisit for stacked activation.
$env:GTK4_GSETTINGS_SCHEMA_DIR_CONDA_BACKUP = $env:GSETTINGS_SCHEMA_DIR
if ($env:GSETTINGS_SCHEMA_DIR) {
    $env:GSETTINGS_SCHEMA_DIR += ";$env:CONDA_PREFIX\Library\share\gtk-4.0\schemas"
} else {
    $env:GSETTINGS_SCHEMA_DIR = "$env:CONDA_PREFIX\Library\share\gtk-4.0\schemas"
}
