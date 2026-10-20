param(
    [Parameter(Mandatory = $true)]
    [string]$LibraryDirectory,
    [string]$DefinitionDirectory = (Join-Path $PSScriptRoot '../RetailInsight.SemanticModel/definition')
)

# Supply the lib/net8.0 directory from Microsoft's Microsoft.AnalysisServices
# NuGet package (verified with 19.114.12). No server connection or model writes.
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $LibraryDirectory 'Microsoft.AnalysisServices.Core.dll')
Add-Type -Path (Join-Path $LibraryDirectory 'Microsoft.AnalysisServices.Tabular.dll')
$database = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder(
    (Resolve-Path -LiteralPath $DefinitionDirectory).Path
)
if ($database.Model.Tables.Count -ne 3 -or $database.Model.Relationships.Count -ne 2) {
    throw 'Expected three model tables and two relationships.'
}
foreach ($relationship in $database.Model.Relationships) {
    if (-not $relationship.FromColumn -or -not $relationship.ToColumn) {
        throw "Unresolved relationship: $($relationship.Name)"
    }
    if ($relationship.FromCardinality.ToString() -ne 'Many' -or
        $relationship.ToCardinality.ToString() -ne 'One' -or
        $relationship.CrossFilteringBehavior.ToString() -ne 'OneDirection') {
        throw "Unexpected relationship configuration: $($relationship.Name)"
    }
}
Write-Output ('PASS: Microsoft TMDL parser loaded {0} tables and {1} resolved many-to-one relationships.' -f
    $database.Model.Tables.Count, $database.Model.Relationships.Count)
Write-Output 'This does not execute Power Query or DAX and does not verify visual rendering.'
