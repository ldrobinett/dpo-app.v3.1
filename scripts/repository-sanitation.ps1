param(
    [string]$Branch = "mi-v5"
)

$ErrorActionPreference = "Stop"

function Assert-CleanWorkingTree {
    $status = git status --porcelain
    if ($status) {
        throw "Working tree is not clean. Commit or stash changes before running sanitation."
    }
}

function Move-TrackedFile {
    param([string]$Source, [string]$Destination)

    if (Test-Path $Source) {
        $destinationDirectory = Split-Path $Destination -Parent
        if ($destinationDirectory -and -not (Test-Path $destinationDirectory)) {
            New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
        }
        git mv -- $Source $Destination
        Write-Host "Renamed: $Source -> $Destination"
    }
}

function Remove-TrackedPath {
    param([string]$Path)

    if (Test-Path $Path) {
        git rm -r -- $Path
        Write-Host "Removed: $Path"
    }
}

Assert-CleanWorkingTree

git checkout $Branch
git pull origin $Branch

# Sprint 1: Canonical architecture filenames
$renames = @{
    "docs/architecture/Current_State_Decision_Engine.md" = "docs/architecture/Current-State-Decision-Engine.md"
    "docs/architecture/Current_State_Home_Template_Architecture.md" = "docs/architecture/Current-State-Home-Template-Architecture.md"
    "docs/architecture/Current_State_Request_Flow.md" = "docs/architecture/Current-State-Request-Flow.md"
    "docs/architecture/Current_State_Startup_Architecture.md" = "docs/architecture/Current-State-Startup-Architecture.md"
    "docs/architecture/Management_Intelligence_Decision_Pipeline.md" = "docs/architecture/Management-Intelligence-Decision-Pipeline.md"
    "docs/architecture/Management_Intelligence_Knowledge_Model.md" = "docs/architecture/Management-Intelligence-Knowledge-Model.md"
}

foreach ($entry in $renames.GetEnumerator()) {
    Move-TrackedFile -Source $entry.Key -Destination $entry.Value
}

# Sprint 2: Duplicate principles document was removed directly from mi-v5.

# Sprint 3: Source backup files
$sourceBackups = @(
    "blueprints/auth.py.1",
    "blueprints/finance.py.1",
    "blueprints/main.py.040926.py",
    "blueprints/main.py.1",
    "blueprints/main.py.2.py",
    "blueprints/main.py.3.py",
    "forms.py.1",
    "models.py.1"
)
foreach ($path in $sourceBackups) { Remove-TrackedPath $path }

# Sprint 4: Template backup files
$templateBackups = @(
    "templates/base.html.1",
    "templates/home.html.040926.html",
    "templates/home.html.1.html",
    "templates/home.html.v1.html",
    "templates/production_display.html.v1"
)
foreach ($path in $templateBackups) { Remove-TrackedPath $path }

# Sprint 5: Legacy archive
Remove-TrackedPath "old py files.101925"

# Sprint 6: Accidental browser-download assets
Get-ChildItem "static/js" -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "main.min.js_https___cdnjs.cloudflare.com_ajax_libs_fullcalendar_5.11.3_main.min_files*" } |
    ForEach-Object { git rm -r -- $_.FullName }

# Sprint 7: Session 009 was restored directly on mi-v5.

if (-not (git status --porcelain)) {
    Write-Host "No local sanitation changes remain."
    exit 0
}

git status --short
git commit -m "Complete repository sanitation sequence"
git push origin $Branch

Write-Host "Repository sanitation completed and pushed to $Branch."
