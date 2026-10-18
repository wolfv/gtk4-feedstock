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

# rattler-build does not install recipe-side post-link scripts automatically.
cp "$RECIPE_DIR/post-link.sh" "$PREFIX/bin/.gtk4-post-link.sh"
chmod +x "$PREFIX/bin/.gtk4-post-link.sh"