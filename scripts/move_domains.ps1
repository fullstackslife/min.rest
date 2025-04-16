# List of domain folders to move
$domains = @(
    'FullStacks.shop',
    'BellaAmour.me',
    'TouchedByChanelsCleaning.com',
    'NewAgeWeb.it.com',
    'FullStacks.live',
    'FullStacks.life',
    'ForeverWingsLLC.com',
    'C-Suite.xyz',
    'BucketGoats.com'
)

# Create domains directory if it doesn't exist
if (-not (Test-Path -Path "domains")) {
    New-Item -ItemType Directory -Path "domains"
}

foreach ($domain in $domains) {
    if (Test-Path -Path $domain) {
        Write-Host "Moving $domain to domains folder..."
        
        # Remove target if it exists
        if (Test-Path -Path "domains\$domain") {
            Remove-Item -Path "domains\$domain" -Recurse -Force
        }
        
        # Move the folder
        Move-Item -Path $domain -Destination "domains\" -Force
        
        Write-Host "Successfully moved $domain"
    }
} 