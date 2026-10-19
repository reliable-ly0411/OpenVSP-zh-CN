$ErrorActionPreference = 'Stop'
# One pinned family only. No tags, assets, releases, or branch updates are made.
$workspace = $env:GITHUB_WORKSPACE
$tooling = Join-Path $workspace 'tooling'
$evidence = Join-Path $workspace 'unicode-evidence'
New-Item -ItemType Directory -Force $evidence | Out-Null
$expectedBaseline = '1d6b0b6078716db5854ff04a92610aa58956a0c6'
$actual = git -C (Join-Path $workspace 'source') rev-parse HEAD
if ($actual.Trim() -ne $expectedBaseline) { throw 'Wrong diagnostic source baseline' }

# Reuse the production build, including its source and package checks. An expected
# STL gate failure is caught only after the original native package exists.
$baselineFailed = $false
try {
    & "$tooling\scripts\native_build_windows.ps1"
} catch {
    $runtimeFile = Join-Path $workspace 'diagnostics\runtime.json'
    if (!(Test-Path -LiteralPath $runtimeFile)) { throw }
    $failure = Get-Content -LiteralPath $runtimeFile -Raw | ConvertFrom-Json
    if ($failure.command -ne 'vspscript' -or $failure.script -ne 'native_functional_smoke.as' -or
        $failure.category -ne 'functional-output-invalid' -or
        @($failure.functional_failure_categories).Count -ne 1 -or
        $failure.functional_failure_categories[0] -ne 'stl-file-missing') { throw }
    $baselineFailed = $true
}
if (!$baselineFailed) { throw 'Pinned baseline did not reproduce the expected native gate failure' }
if (!(Test-Path -LiteralPath (Join-Path $workspace 'stage'))) { throw 'Baseline CPack extraction is missing' }

if (Test-Path O:\) { throw 'Neutral diagnostic build drive is already occupied' }
subst O: $workspace
if ($LASTEXITCODE -ne 0) { throw 'Could not create neutral build drive' }
try {
    $python = 'O:\venv\Scripts\python.exe'
    $cmake = 'O:\venv\Scripts\cmake.exe'
    $env:PATH = "O:\venv\Scripts;$env:PATH"
    & $python -X utf8 O:\tooling\scripts\native_windows_unicode.py package `
        --package O:\stage --source O:\source --phase baseline --output O:\unicode-evidence\baseline.json
    if ($LASTEXITCODE -ne 0) { throw 'Baseline diagnostic capture failed' }
    & $python -X utf8 O:\tooling\scripts\native_windows_unicode.py apply `
        --source O:\source --tooling O:\tooling --output O:\unicode-evidence\patch.json
    if ($LASTEXITCODE -ne 0) { throw 'Pinned minimal source patch failed' }
    $patch = Get-Content -LiteralPath O:\unicode-evidence\patch.json -Raw | ConvertFrom-Json
    $env:BACKFILL_SHA = $patch.temporary_source_sha
    & $cmake --build O:\source\build --target package --config Release --parallel 2
    if ($LASTEXITCODE -ne 0) { throw 'Patched incremental package build failed' }
    $packages = @(Get-ChildItem O:\source\build -Filter 'OpenVSP-*.zip')
    if ($packages.Count -ne 1) { throw 'Expected one patched CPack ZIP' }
    Expand-Archive -LiteralPath $packages[0].FullName -DestinationPath O:\patched-stage
    & $python -X utf8 O:\tooling\scripts\native_windows_unicode.py package `
        --package O:\patched-stage --source O:\source --phase patched --output O:\unicode-evidence\patched.json
    if ($LASTEXITCODE -ne 0) { throw 'Patched exact Unicode/model/functional gates failed' }
    # Run every production gate against a clean, temporary child commit. No dirty
    # source override exists, and these local diagnostic ZIPs are never uploaded.
    if (Test-Path -LiteralPath O:\diagnostics\runtime.json) { Remove-Item -LiteralPath O:\diagnostics\runtime.json }
    & $python -X utf8 O:\tooling\scripts\native_verify.py O:\patched-stage O:\source O:\diagnostic-deliverables
    if ($LASTEXITCODE -ne 0) {
        @{ stage = 'patched-production-verification'; exit_code = $LASTEXITCODE; diagnostic_only = $true } |
            ConvertTo-Json | Set-Content -LiteralPath O:\unicode-evidence\production-failure.json -Encoding utf8
        if (Test-Path -LiteralPath O:\diagnostics\runtime.json) {
            Copy-Item -LiteralPath O:\diagnostics\runtime.json -Destination O:\unicode-evidence\production-runtime.json
        }
        throw 'Patched complete production verification failed'
    }
    Copy-Item -LiteralPath O:\diagnostic-deliverables\verification.json -Destination O:\unicode-evidence\production-verification.json
    & $python -X utf8 O:\tooling\scripts\native_windows_unicode.py compare `
        --baseline O:\unicode-evidence\baseline.json --patched O:\unicode-evidence\patched.json `
        --output O:\unicode-evidence\comparison.json
    if ($LASTEXITCODE -ne 0) { throw 'Baseline and patched causal comparison failed' }
    git -C O:\source diff --check
    if ($LASTEXITCODE -ne 0) { throw 'Patch whitespace check failed' }
} finally {
    Set-Location $workspace
    subst O: /D
}
