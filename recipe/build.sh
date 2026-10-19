#! /bin/bash

set -ex

export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$BUILD_PREFIX/lib/pkgconfig
export XDG_DATA_DIRS=${XDG_DATA_DIRS}:$PREFIX/share

meson_config_args=(
    -Ddocumentation=false
    -Dman-pages=false
    -Dintrospection=enabled
    -Dbuild-examples=false
    -Dbuild-tests=false
    -Dbuild-testsuite=false
    -Dwayland-backend=true
    -Dmedia-gstreamer=disabled
)

if test $(uname) == 'Darwin' ; then
	meson_config_args+=("-Dprint-cups=disabled")
	meson_config_args+=("-Dx11-backend=false")
	meson_config_args+=("-Dmacos-backend=true")
elif test $(uname) == 'Linux' ; then
	meson_config_args+=("-Dx11-backend=true")
fi

# ensure that the post install script is ignored
export DESTDIR="/"
# stub out update-mime-database
printf '#!/bin/bash\nexit 0\n' > "$BUILD_PREFIX/bin/update-mime-database"
chmod +x "$BUILD_PREFIX/bin/update-mime-database"

meson setup builddir \
    ${MESON_ARGS} \
    --default-library=shared \
    "${meson_config_args[@]}" \
    --prefix=$PREFIX \
    -Dlibdir=lib \
    --wrap-mode=nofallback \
    || (cat builddir/meson-logs/meson-log.txt; false)

# print full meson configuration
meson configure builddir
ninja -v -C builddir -j ${CPU_COUNT}
ninja -C builddir install -j ${CPU_COUNT}

# Compile only GTK-owned schemas, without writing the shared environment cache.
mkdir -p "$PREFIX/share/gtk-4.0/schemas" builddir/gtk4-schemas
cp gtk/*.gschema.xml demos/gtk-demo/*.gschema.xml builddir/gtk4-schemas/
"$BUILD_PREFIX/bin/glib-compile-schemas" --strict \
    --targetdir="$PREFIX/share/gtk-4.0/schemas" builddir/gtk4-schemas

mkdir -p "$PREFIX/etc/conda/activate.d" "$PREFIX/etc/conda/deactivate.d"
for shell in sh fish; do
    cp "$RECIPE_DIR/activate.$shell" "$PREFIX/etc/conda/activate.d/zz-gtk4_activate.$shell"
    cp "$RECIPE_DIR/deactivate.$shell" "$PREFIX/etc/conda/deactivate.d/zz-gtk4_deactivate.$shell"
done