# Run after libglib's activation script; no cache generation is needed.
export GTK4_GSETTINGS_SCHEMA_DIR_CONDA_BACKUP="${GSETTINGS_SCHEMA_DIR:-}"
export GSETTINGS_SCHEMA_DIR="${GSETTINGS_SCHEMA_DIR:+$GSETTINGS_SCHEMA_DIR:}$CONDA_PREFIX/share/gtk-4.0/schemas"
