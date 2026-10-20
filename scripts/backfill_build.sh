#!/usr/bin/env bash
set -euo pipefail
ROOT="$GITHUB_WORKSPACE"
SOURCE="$ROOT/source"
TOOLS="$ROOT/tooling/scripts"
cd "$SOURCE"
test "$(uname -m)" = "$BACKFILL_ARCH"
if [[ $(uname) == Darwin ]]; then
  if [[ ${NATIVE_RELEASE:-false} == true ]]; then
    python "$TOOLS/native_macos_toolchain.py" preflight --report "$ROOT/macos-toolchain.json"
  fi
  brew install swig libomp doxygen graphviz pandoc zstd
  if [[ ${NATIVE_RELEASE:-false} == true ]]; then
    brew install "llvm@$BACKFILL_LLVM" --force-bottle --ignore-dependencies
    python "$TOOLS/native_macos_toolchain.py" verify --report "$ROOT/macos-toolchain.json"
  else
    brew install "llvm@$BACKFILL_LLVM" --ignore-dependencies
  fi
  export CC="$(brew --prefix "llvm@$BACKFILL_LLVM")/bin/clang"
  export CXX="$(brew --prefix "llvm@$BACKFILL_LLVM")/bin/clang++"
  python -m venv "$ROOT/venv"
else
  sudo apt-get update
  sudo apt-get install --yes build-essential gcc-13 g++-13 git zip unzip \
    python3-dev python3-venv libxml2-dev libjpeg-dev libglm-dev fonts-noto-cjk \
    xvfb xauth libglew-dev libglu1-mesa-dev libfltk1.3-dev fluid xorg-dev swig doxygen graphviz pandoc
  export CC=gcc-13 CXX=g++-13
  python3 -m venv "$ROOT/venv"
fi
source "$ROOT/venv/bin/activate"
python -m pip install 'cmake==3.31.6' 'numpy==1.26.4' 'setuptools<76' wheel
python -c 'import os,sys; assert ".".join(map(str,sys.version_info[:2])) == os.environ["BACKFILL_PYTHON"]'
# ExternalProject children inherit these flags. Do not claim a lower macOS deployment target.
export CFLAGS="-O2 -fPIC -ffile-prefix-map=$ROOT=/usr/src/openvsp -fdebug-prefix-map=$ROOT=/usr/src/openvsp"
export CXXFLAGS="$CFLAGS"
libargs=()
args=()
if [[ $(uname) == Darwin ]]; then
  libargs+=("-DCMAKE_OSX_ARCHITECTURES=$BACKFILL_ARCH")
  args+=("-DCMAKE_OSX_ARCHITECTURES=$BACKFILL_ARCH" "-DOpenMP_ROOT=$(brew --prefix libomp)" -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON)
  export LDFLAGS='-Wl,-headerpad_max_install_names'
  if grep -q 'CMAKE_ARGS' Libraries/cmake/External_LibXml2.cmake; then
    export CMAKE_TOOLCHAIN_FILE="$TOOLS/backfill_libxml_toolchain.cmake"
    export BACKFILL_LIBXML_SYSCONFDIR=/etc
  else
    # 3.51.x uses historical autotools; do not assume CMake settings affect it.
    export BACKFILL_LIBXML_SYSCONFDIR=historical-autotools-default
  fi
else
  args+=(-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=OFF '-DCMAKE_INSTALL_RPATH=$ORIGIN/lib')
  libargs+=(-DVSP_USE_SYSTEM_LIBXML2=ON -DVSP_USE_SYSTEM_GLM=ON -DVSP_USE_SYSTEM_GLEW=ON)
fi
if [[ -f scripts/localization_tests/CMakeLists.txt ]]; then
  cmake -S scripts/localization_tests -B "$ROOT/localization-tests"
  cmake --build "$ROOT/localization-tests" --parallel 2
  ctest --test-dir "$ROOT/localization-tests" --output-on-failure
else
  echo 'Historical source has no C++ localization test target; independent package/model tests remain mandatory.'
fi
cmake -S Libraries -B buildlibs -DCMAKE_BUILD_TYPE=Release "${libargs[@]}"
cmake --build buildlibs --parallel 2
if [[ ${BACKFILL_LIBXML_SYSCONFDIR:-} == /etc ]]; then
  # Fail if a child ignored the scoped toolchain setting; never patch binary bytes.
  grep -Fx '#define XML_SYSCONFDIR "/etc"' buildlibs/LIBXML2-prefix/src/LIBXML2-build/config.h
fi
cmake -S src -B build -DCMAKE_BUILD_TYPE=Release -DVSP_CPACK_GEN=ZIP -DVSP_NO_PYDOC=ON -DPANDOC_EXECUTABLE=/nonexistent/pandoc \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DCMAKE_INSTALL_PREFIX=/opt/OpenVSP \
  "-DVSP_LIBRARY_PATH=$SOURCE/buildlibs" "-DPython3_EXECUTABLE=$(command -v python)" \
  "-DPYTHON_EXECUTABLE=$(command -v python)" "${args[@]}"
cmake --build build --target package --parallel 2
# Build options must not rewrite the immutable historical source.
git diff --quiet --exit-code
git diff --cached --quiet --exit-code
python "$TOOLS/check_source_worktree.py" "$SOURCE"
# Historical sources lack a common archive checker; verify the final relocated ZIP below.
package=$(find build -maxdepth 1 -type f -name 'OpenVSP-*.zip')
test "$(printf '%s\n' "$package" | wc -l | tr -d ' ')" = 1
unzip -t "$package"
mkdir "$ROOT/stage"
unzip -q "$package" -d "$ROOT/stage"
# 3.51.2 did not install AGENTS.md. Supplement it from that same immutable source.
package_root=$(find "$ROOT/stage" -mindepth 1 -maxdepth 1 -type d)
test -n "$package_root"
if [[ ! -f "$package_root/AGENTS.md" ]]; then
  git show HEAD:AGENTS.md > "$package_root/AGENTS.md"
fi
if [[ ${NATIVE_RELEASE:-false} == true ]]; then
  python "$TOOLS/native_verify.py" "$ROOT/stage" "$SOURCE" "$ROOT/deliverables"
  if [[ $(uname) == Darwin ]]; then
    cp "$ROOT/macos-toolchain.json" "$ROOT/deliverables/toolchain.json"
  fi
else
  python "$TOOLS/backfill_verify.py" "$ROOT/stage" "$SOURCE" "$ROOT/deliverables"
fi
