[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("generate", "transform", "suggest", "prompt")]
    [string]$Command,

    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [Parameter(Mandatory = $false)]
    [string]$Output,

    [string]$InputImage,

    [string]$Model,

    [string]$BaseUrl,

    [string]$StyleName,

    [string]$StyleId,

    [string]$StyleMix,

    [string]$Template,

    [string[]]$Var,

    [string]$Color,

    [int]$Limit = 5,

    [ValidateSet("style", "prompt", "color", "all")]
    [string]$Domain = "style",

    [string]$Category,

    [ValidateSet("text", "json")]
    [string]$Format = "text",

    [switch]$DesignSystem,

    [switch]$Random,

    [switch]$Negative,

    [switch]$NoQuality
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

function Get-PythonCommand {
    $candidates = @("python", "python3", "py")
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            return $candidate
        }
    }
    throw "Python is required for search integration. Install Python or use scripts/image_craft.py directly."
}

function Invoke-SearchScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Query,

        [string]$SearchDomain = "style",

        [int]$SearchLimit = 5,

        [string]$SearchCategory,

        [string]$SearchFormat = "text"
    )

    $scriptPath = Join-Path $PSScriptRoot "search.py"
    $python = Get-PythonCommand
    $arguments = @($scriptPath)
    if (-not [string]::IsNullOrWhiteSpace($Query)) {
        $arguments += $Query
    }
    $arguments += @("--domain", $SearchDomain, "--limit", [string]$SearchLimit, "--format", $SearchFormat)
    if (-not [string]::IsNullOrWhiteSpace($SearchCategory)) {
        $arguments += @("--category", $SearchCategory)
    }
    if ($DesignSystem) {
        $arguments += "--design-system"
    }
    if ($Random) {
        $arguments += "--random"
    }
    & $python @arguments
}

function Invoke-PromptPreviewScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InputPrompt,

        [string]$InputStyleName,

        [string]$InputStyleId,

        [string]$InputStyleMix,

        [string]$InputTemplate,

        [string[]]$InputVar,

        [string]$InputColor,

        [string]$OutputFormat = "text"
    )

    $scriptPath = Join-Path $PSScriptRoot "image_craft.py"
    $python = Get-PythonCommand
    $arguments = @($scriptPath, "prompt", "--prompt", $InputPrompt, "--format", $OutputFormat)
    if (-not [string]::IsNullOrWhiteSpace($InputStyleName)) {
        $arguments += @("--style-name", $InputStyleName)
    }
    if (-not [string]::IsNullOrWhiteSpace($InputStyleId)) {
        $arguments += @("--style-id", $InputStyleId)
    }
    if (-not [string]::IsNullOrWhiteSpace($InputStyleMix)) {
        $arguments += @("--style-mix", $InputStyleMix)
    }
    if (-not [string]::IsNullOrWhiteSpace($InputTemplate)) {
        $arguments += @("--template", $InputTemplate)
    }
    foreach ($variable in @($InputVar)) {
        if (-not [string]::IsNullOrWhiteSpace($variable)) {
            $expandedVariables = $variable -split ",(?=[^,=]+=)"
            foreach ($expandedVariable in $expandedVariables) {
                if (-not [string]::IsNullOrWhiteSpace($expandedVariable)) {
                    $arguments += @("--var", $expandedVariable.Trim())
                }
            }
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($InputColor)) {
        $arguments += @("--color", $InputColor)
    }
    if ($Negative) {
        $arguments += "--negative"
    }
    if ($NoQuality) {
        $arguments += "--no-quality"
    }
    & $python @arguments
}

function Get-StylePrompt {
    param(
        [string]$Subject,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return $Subject
    }

    $skillDir = Get-SkillDirectory
    $stylesPath = Join-Path $skillDir "data\styles.csv"
    if (-not (Test-Path -LiteralPath $stylesPath)) {
        return $Subject
    }

    $styles = Import-Csv -LiteralPath $stylesPath
    $style = $styles | Where-Object {
        $_.id -eq $Name -or $_.name_en -like "*$Name*" -or $_.name_cn -like "*$Name*"
    } | Select-Object -First 1

    if (-not $style) {
        try {
            $searchOutput = Invoke-SearchScript -Query $Name -SearchDomain "style" -SearchLimit 1 -SearchFormat "json"
            $searchData = $searchOutput | ConvertFrom-Json
            $styleMatches = @($searchData.styles)
            if ($styleMatches.Count -gt 0) {
                $style = $styleMatches[0]
            }
        }
        catch {
            $style = $null
        }
    }

    if (-not $style) {
        return $Subject
    }

    if ([string]::IsNullOrWhiteSpace($style.prompt_template)) {
        return $Subject
    }

    $style.prompt_template.Replace("{subject}", $Subject)
}

if ($Command -eq "suggest") {
    Invoke-SearchScript -Query $Prompt -SearchDomain $Domain -SearchLimit $Limit -SearchCategory $Category -SearchFormat $Format
    return
}

if ($Command -eq "prompt") {
    Invoke-PromptPreviewScript -InputPrompt $Prompt -InputStyleName $StyleName -InputStyleId $StyleId -InputStyleMix $StyleMix -InputTemplate $Template -InputVar $Var -InputColor $Color -OutputFormat $Format
    return
}

if ([string]::IsNullOrWhiteSpace($Output)) {
    throw "-Output is required for generate and transform."
}

$config = Get-ImageCraftConfig
$promptPreviewJson = Invoke-PromptPreviewScript -InputPrompt $Prompt -InputStyleName $StyleName -InputStyleId $StyleId -InputStyleMix $StyleMix -InputTemplate $Template -InputVar $Var -InputColor $Color -OutputFormat "json"
$promptPreview = $promptPreviewJson | ConvertFrom-Json
$finalPrompt = $promptPreview.enhanced_prompt
$negativePrompt = $promptPreview.negative_prompt

if ($Command -eq "generate") {
    $payload = @{
        model = $config.Model
        prompt = $finalPrompt
    }
    if (-not [string]::IsNullOrWhiteSpace($negativePrompt)) {
        $payload.negative_prompt = $negativePrompt
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
                        text = $finalPrompt
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
    if (-not [string]::IsNullOrWhiteSpace($negativePrompt)) {
        $payload.negative_prompt = $negativePrompt
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
    prompt = $finalPrompt
    negative_prompt = $negativePrompt
} | ConvertTo-Json -Depth 5
