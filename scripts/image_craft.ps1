[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("generate", "transform")]
    [string]$Command,

    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [Parameter(Mandatory = $true)]
    [string]$Output,

    [string]$InputImage,

    [string]$Model,

    [string]$BaseUrl
)

$ErrorActionPreference = "Stop"

function Get-SkillDirectory {
    Split-Path -Parent (Split-Path -Parent $PSCommandPath)
}

function Get-ImageCraftConfig {
    $skillDir = Get-SkillDirectory
    $configPath = Join-Path $skillDir "private_config.json"
    $config = @{}

    if (Test-Path -LiteralPath $configPath) {
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
    }

    $baseUrl = $BaseUrl
    if ([string]::IsNullOrWhiteSpace($baseUrl)) {
        $baseUrl = $env:IMAGE_CRAFT_BASE_URL
    }
    if ([string]::IsNullOrWhiteSpace($baseUrl)) {
        $baseUrl = $config.base_url
    }
    if ([string]::IsNullOrWhiteSpace($baseUrl)) {
        throw "Missing base URL. Set IMAGE_CRAFT_BASE_URL, use -BaseUrl parameter, or add base_url to private_config.json."
    }

    $apiKey = $env:IMAGE_CRAFT_API_KEY
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = $config.api_key
    }
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        throw "Missing API key. Set IMAGE_CRAFT_API_KEY or add api_key to private_config.json."
    }

    $model = $Model
    if ([string]::IsNullOrWhiteSpace($model)) {
        $model = $env:IMAGE_CRAFT_MODEL
    }
    if ([string]::IsNullOrWhiteSpace($model)) {
        $model = $config.model
    }
    if ([string]::IsNullOrWhiteSpace($model)) {
        $model = "gpt-image-2"
    }

    [pscustomobject]@{
        BaseUrl = $baseUrl.TrimEnd("/")
        ApiKey = $apiKey
        Model = $model
    }
}

function Invoke-RightCodesJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,

        [Parameter(Mandatory = $true)]
        [object]$Payload,

        [Parameter(Mandatory = $true)]
        [string]$ApiKey
    )

    $headers = @{
        Authorization = "Bearer $ApiKey"
        "Content-Type" = "application/json"
    }
    $body = $Payload | ConvertTo-Json -Depth 20
    Invoke-RestMethod -Method Post -Uri $Url -Headers $headers -Body $body
}

function Convert-ImageToDataUrl {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Input image does not exist: $Path"
    }

    $extension = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
    $mimeType = switch ($extension) {
        ".jpg" { "image/jpeg" }
        ".jpeg" { "image/jpeg" }
        ".webp" { "image/webp" }
        ".gif" { "image/gif" }
        default { "image/png" }
    }

    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $Path))
    "data:$mimeType;base64,$([Convert]::ToBase64String($bytes))"
}

function Get-FirstDataItem {
    param(
        [object]$Data
    )

    if ($null -eq $Data) {
        return $null
    }

    if ($Data -is [System.Array]) {
        if ($Data.Count -eq 0) {
            return $null
        }
        return $Data[0]
    }

    $Data
}

function Get-ImageResultFromString {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    if ($Value -match "^data:image/[a-zA-Z0-9.+-]+;base64,([A-Za-z0-9+/=\r\n]+)") {
        return [pscustomobject]@{
            ImageBase64 = ($Matches[1] -replace "\s+", "")
            ImageUrl = $null
            RevisedPrompt = $null
        }
    }

    if ($Value -match "^https?://") {
        return [pscustomobject]@{
            ImageBase64 = $null
            ImageUrl = $Value
            RevisedPrompt = $null
        }
    }

    $null
}

function Get-ImageResult {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Response
    )

    $dataItem = Get-FirstDataItem -Data $Response.data
    if ($dataItem -and $dataItem.b64_json) {
        return [pscustomobject]@{
            ImageBase64 = $dataItem.b64_json
            ImageUrl = $null
            RevisedPrompt = $dataItem.revised_prompt
        }
    }
    if ($dataItem -and $dataItem.url) {
        return [pscustomobject]@{
            ImageBase64 = $null
            ImageUrl = $dataItem.url
            RevisedPrompt = $dataItem.revised_prompt
        }
    }
    if ($Response.data -is [string]) {
        $stringResult = Get-ImageResultFromString -Value $Response.data
        if ($stringResult) {
            return $stringResult
        }
    }

    if ($Response.choices -and $Response.choices.Count -gt 0) {
        $content = $Response.choices[0].message.content
        if ($content -match "data:image/[a-zA-Z0-9.+-]+;base64,([A-Za-z0-9+/=\r\n]+)") {
            return [pscustomobject]@{
                ImageBase64 = ($Matches[1] -replace "\s+", "")
                ImageUrl = $null
                RevisedPrompt = $null
            }
        }
        if ($content -match "!\[[^\]]*\]\((https?://[^)]+)\)") {
            return [pscustomobject]@{
                ImageBase64 = $null
                ImageUrl = $Matches[1]
                RevisedPrompt = $null
            }
        }
    }

    throw "Could not find image data or URL in API response."
}

function Save-ImageBase64 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ImageBase64,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $resolvedOutput = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
    $outputDir = Split-Path -Parent $resolvedOutput
    if (-not [string]::IsNullOrWhiteSpace($outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    [System.IO.File]::WriteAllBytes($resolvedOutput, [Convert]::FromBase64String($ImageBase64))
    $resolvedOutput
}

function Save-ImageUrl {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ImageUrl,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $resolvedOutput = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
    $outputDir = Split-Path -Parent $resolvedOutput
    if (-not [string]::IsNullOrWhiteSpace($outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    Invoke-WebRequest -Method Get -Uri $ImageUrl -OutFile $resolvedOutput | Out-Null
    $resolvedOutput
}

$config = Get-ImageCraftConfig

if ($Command -eq "generate") {
    $payload = @{
        model = $config.Model
        prompt = $Prompt
    }
    $response = Invoke-RightCodesJson -Url "$($config.BaseUrl)/v1/images/generations" -Payload $payload -ApiKey $config.ApiKey
}
else {
    if ([string]::IsNullOrWhiteSpace($InputImage)) {
        throw "-InputImage is required for transform."
    }
    $payload = @{
        model = $config.Model
        messages = @(
            @{
                role = "user"
                content = @(
                    @{
                        type = "text"
                        text = $Prompt
                    },
                    @{
                        type = "image_url"
                        image_url = @{
                            url = Convert-ImageToDataUrl -Path $InputImage
                        }
                    }
                )
            }
        )
    }
    $response = Invoke-RightCodesJson -Url "$($config.BaseUrl)/v1/chat/completions" -Payload $payload -ApiKey $config.ApiKey
}

$imageResult = Get-ImageResult -Response $response
if ($imageResult.ImageBase64) {
    $savedPath = Save-ImageBase64 -ImageBase64 $imageResult.ImageBase64 -OutputPath $Output
}
elseif ($imageResult.ImageUrl) {
    $savedPath = Save-ImageUrl -ImageUrl $imageResult.ImageUrl -OutputPath $Output
}
else {
    throw "Could not find image data or URL in API response."
}

@{
    output = $savedPath
    image_url = $imageResult.ImageUrl
    revised_prompt = $imageResult.RevisedPrompt
} | ConvertTo-Json -Depth 5
