$ErrorActionPreference = 'Stop'
# A neutral drive alias keeps MSVC __FILE__ paths independent of the runner's
# private workspace. This does not alter sources or rewrite compiled bytes.
if (Test-Path O:\) { throw 'Neutral O: build drive is already occupied' }
subst O: $env:GITHUB_WORKSPACE
if ($LASTEXITCODE -ne 0) { throw 'Could not create neutral build drive' }
try {
    $root = 'O:\'
    Set-Location O:\source
    choco install --yes swig pandoc
    if ($LASTEXITCODE -ne 0) { throw 'Build dependency installation failed' }
    python -m venv O:\venv
    if ($LASTEXITCODE -ne 0) { throw 'Build venv creation failed' }
    $env:PATH = "O:\venv\Scripts;$env:PATH"
    python -m pip install 'cmake==3.31.6' 'numpy==1.26.4' 'setuptools<76' wheel 'pefile==2024.8.26'
    if ($LASTEXITCODE -ne 0) { throw 'Build Python dependencies failed' }
    python -c 'import os,sys; assert ".".join(map(str,sys.version_info[:2])) == os.environ["BACKFILL_PYTHON"]'
    if ($LASTEXITCODE -ne 0) { throw 'Wrong Python ABI selected' }
    cmake -S scripts/localization_tests -B O:\localization-tests
    if ($LASTEXITCODE -ne 0) { throw 'Localization test configure failed' }
    cmake --build O:\localization-tests --config Release --parallel 2
    if ($LASTEXITCODE -ne 0) { throw 'Localization test build failed' }
    ctest --test-dir O:\localization-tests -C Release --output-on-failure
    if ($LASTEXITCODE -ne 0) { throw 'Localization regressions failed' }
    cmake -S Libraries -B buildlibs -A x64 -DCMAKE_BUILD_TYPE=Release
    if ($LASTEXITCODE -ne 0) { throw 'Dependency configure failed' }
    cmake --build buildlibs --config Release --parallel 2
    if ($LASTEXITCODE -ne 0) { throw 'Dependency build failed' }
    cmake -S src -B build -A x64 -DCMAKE_BUILD_TYPE=Release -DVSP_CPACK_GEN=ZIP -DVSP_NO_PYDOC=ON `
        -DPANDOC_EXECUTABLE=O:/unavailable/pandoc -DVSP_LIBRARY_PATH=O:/source/buildlibs `
        -DPython3_EXECUTABLE=O:/venv/Scripts/python.exe -DPYTHON_EXECUTABLE=O:/venv/Scripts/python.exe
    if ($LASTEXITCODE -ne 0) { throw 'OpenVSP configure failed' }
    cmake --build build --target package --config Release --parallel 2
    if ($LASTEXITCODE -ne 0) { throw 'OpenVSP package build failed' }
    git diff --quiet --exit-code
    if ($LASTEXITCODE -ne 0) { throw 'Build modified tracked source' }
    git diff --cached --quiet --exit-code
    if ($LASTEXITCODE -ne 0) { throw 'Build modified index' }
    $packages = @(Get-ChildItem build -Filter 'OpenVSP-*.zip')
    if ($packages.Count -ne 1) { throw 'Expected one CPack ZIP' }
    Expand-Archive -LiteralPath $packages[0].FullName -DestinationPath O:\stage
    python -X utf8 O:\tooling\scripts\native_verify.py O:\stage O:\source O:\deliverables
    if ($LASTEXITCODE -ne 0) { throw 'Native package verification failed' }
} finally {
    Set-Location $env:GITHUB_WORKSPACE
    subst O: /D
}
