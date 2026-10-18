setlocal EnableDelayedExpansion
@echo on

:: set pkg-config path so that host deps can be found
:: (set as env var so it's used by both meson and during build with g-ir-scanner)
set "PKG_CONFIG_PATH=%LIBRARY_LIB%\pkgconfig;%LIBRARY_PREFIX%\share\pkgconfig;%BUILD_PREFIX%\Library\lib\pkgconfig"

set "XDG_DATA_DIRS=%XDG_DATA_DIRS%;%LIBRARY_PREFIX%\share"

:: By default Meson tries to run the glib tools with the %BUILD_PREFIX% Python,
:: which fails. In order to override this, we need to use a Meson machine file,
:: because otherwise Meson prioritizes the results from the glib-2.0 pkg-config
:: file, which don't work.
echo [binaries] >native_file.txt
echo glib-mkenums = ['%PREFIX%\python.exe', '%LIBRARY_PREFIX%\bin\glib-mkenums'] >>native_file.txt
echo glib-genmarshal = ['%PREFIX%\python.exe', '%LIBRARY_PREFIX%\bin\glib-genmarshal'] >>native_file.txt

:: ensure that the post install script is ignored
set "DESTDIR=%BUILD_PREFIX:~0,3%"

:: meson options
:: (set pkg_config_path so deps in host env can be found)
set ^"MESON_OPTIONS=^
  --prefix="%LIBRARY_PREFIX%" ^
  --default-library=shared ^
  --wrap-mode=nofallback ^
  --force-fallback-for=DirectX-Headers ^
  --buildtype=release ^
  --backend=ninja ^
  --native-file=native_file.txt ^
  -Ddocumentation=false ^
  -Dman-pages=false ^
  -Dintrospection=enabled ^
  -Dbuild-examples=false ^
  -Dbuild-tests=false ^
  -Dbuild-testsuite=false ^
  -Dmedia-gstreamer=disabled ^
 ^"

:: configure build using meson
meson setup builddir !MESON_OPTIONS!
if errorlevel 1 exit 1

:: print results of build configuration
meson configure builddir
if errorlevel 1 exit 1

ninja -v -C builddir -j %CPU_COUNT%
if errorlevel 1 exit 1

ninja -C builddir install -j %CPU_COUNT%
if errorlevel 1 exit 1

:: Keep GTK's precompiled schemas separate from the environment-wide cache.
mkdir "%LIBRARY_PREFIX%\share\gtk-4.0\schemas"
if errorlevel 1 exit 1
copy /Y "builddir\gtk\gschemas.compiled" "%LIBRARY_PREFIX%\share\gtk-4.0\schemas\gschemas.compiled"
if errorlevel 1 exit 1
