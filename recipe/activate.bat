@rem shortcut: single-level backups match libglib; revisit for stacked activation.
@set "GTK4_GSETTINGS_SCHEMA_DIR_CONDA_BACKUP=%GSETTINGS_SCHEMA_DIR%"
@if defined GSETTINGS_SCHEMA_DIR (
    set "GSETTINGS_SCHEMA_DIR=%GSETTINGS_SCHEMA_DIR%;%CONDA_PREFIX%\Library\share\gtk-4.0\schemas"
) else (
    set "GSETTINGS_SCHEMA_DIR=%CONDA_PREFIX%\Library\share\gtk-4.0\schemas"
)
