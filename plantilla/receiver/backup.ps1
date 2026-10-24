<#
ADR-0078: the receiver asks the server of a product for its backup, and keeps it in Repos.

    .\backup.ps1 -Product <app> -Server <host> -Repos <folder>

rest-server and ssh are on the PATH. From canone: plataformas/despliegue.md.
#>
param(
    [Parameter(Mandatory)] [string] $Product,
    [Parameter(Mandatory)] [string] $Server,
    [Parameter(Mandatory)] [string] $Repos
)
$ErrorActionPreference = "Stop"
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
exit $code
