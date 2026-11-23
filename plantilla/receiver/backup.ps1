<#
ADR-0078: the receiver asks the server of a product for its backup, and keeps it in Repos.
Then it forgets what passed its retention and checks its copy, with the password of the
repository in PasswordFile: the server only adds.

    .\backup.ps1 -Product <app> -Server <host> -Repos <folder> -PasswordFile <file>

rest-server 0.14.0, from its release on GitHub, restic 0.18.0 and ssh are on the PATH. From
canone: plataformas/despliegue.md.
#>
param(
    [Parameter(Mandatory)] [string] $Product,
    [Parameter(Mandatory)] [string] $Server,
    [Parameter(Mandatory)] [string] $Repos,
    [Parameter(Mandatory)] [string] $PasswordFile
)
$ErrorActionPreference = "Stop"
$version = "0.14.0"
if ((& restic version) -notmatch "^restic 0\.18\.0 ") {
    throw "restic is not 0.18.0"
}
if ((& rest-server --version) -notmatch " rest-server $([regex]::Escape($version)) ") {
    throw "rest-server is not $version"
}
# The server adds backups, but cannot delete or rewrite them.
$rest = Start-Process rest-server -NoNewWindow -PassThru -ArgumentList @(
    "--path", "`"$Repos`"", "--listen", "127.0.0.1:8001", "--append-only", "--no-auth"
)
try {
    $client = New-Object System.Net.Sockets.TcpClient
    for ($tries = 50; -not $client.Connected; $tries--) {
        if ($tries -eq 0 -or $rest.HasExited) {
            throw "rest-server does not listen on 127.0.0.1:8001"
        }
        try { $client.Connect("127.0.0.1", 8001) } catch { Start-Sleep -Milliseconds 200 }
    }
    $client.Close()
    # Without the tunnel, ssh ends instead of asking for the backup.
    ssh -T -o ExitOnForwardFailure=yes -R 127.0.0.1:8001:127.0.0.1:8001 "$Product-receiver@$Server"
    $code = $LASTEXITCODE
}
finally {
    Stop-Process -Id $rest.Id -ErrorAction SilentlyContinue
}
if ($code -ne 0) { exit $code }
$repository = Join-Path $Repos $Product
# The server is done, and a backup cut short leaves its lock.
& restic --repo $repository --password-file $PasswordFile unlock --remove-all
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& restic --repo $repository --password-file $PasswordFile forget --group-by= `
    --keep-within-daily 7d --keep-within-weekly 1m --keep-within-monthly 1y --prune
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& restic --repo $repository --password-file $PasswordFile check --read-data-subset 5%
exit $LASTEXITCODE
