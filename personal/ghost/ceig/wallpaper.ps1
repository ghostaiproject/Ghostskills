# Upscale an image (default: newest Gemini download) to Width x Height, center-cropped to that aspect; optionally set it as wallpaper.
param([Parameter(Mandatory)][string]$Name, [string]$Source, [int]$Width = 3840, [int]$Height = 2160, [switch]$SetWallpaper)
Add-Type -AssemblyName System.Drawing

$src = if ($Source) { (Resolve-Path $Source).Path } else {
    (Get-ChildItem "$env:USERPROFILE\Downloads\Gemini_Generated_Image_*" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName }
if (-not $src) { throw 'No Gemini_Generated_Image_* in Downloads (or pass -Source)' }
$Name = $Name -replace '[\/:*?"<>|]', '_'
$dst = "$env:USERPROFILE\Pictures\Wallpapers\$Name.png"
New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null

# Load from bytes so the source file isn't locked while we work.
$img = [System.Drawing.Image]::FromStream((New-Object IO.MemoryStream (, [IO.File]::ReadAllBytes($src))))
$bmp = New-Object System.Drawing.Bitmap $Width, $Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
try {
    $cw = [math]::Min($img.Width, [int]($img.Height * $Width / $Height)); $ch = [int]($cw * $Height / $Width)
    $cx = [int](($img.Width - $cw) / 2); $cy = [int](($img.Height - $ch) / 2)
    $g.InterpolationMode = 'HighQualityBicubic'; $g.PixelOffsetMode = 'HighQuality'; $g.CompositingQuality = 'HighQuality'
    $attr = New-Object System.Drawing.Imaging.ImageAttributes; $attr.SetWrapMode('TileFlipXY')
    $g.DrawImage($img, (New-Object System.Drawing.Rectangle 0, 0, $Width, $Height), $cx, $cy, $cw, $ch, 'Pixel', $attr)
    Write-Output "Source: $src ($($img.Width)x$($img.Height))"
    $bmp.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output "Saved: $dst (${Width}x$Height)"
} finally { $g.Dispose(); $img.Dispose(); $bmp.Dispose() }

if ($SetWallpaper) {
    Set-ItemProperty 'HKCU:\Control Panel\Desktop' WallpaperStyle '10'
    Set-ItemProperty 'HKCU:\Control Panel\Desktop' TileWallpaper '0'
    Add-Type -Namespace Win -Name WP -MemberDefinition '[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int SystemParametersInfo(int a, int b, string c, int d);'
    [void][Win.WP]::SystemParametersInfo(0x14, 0, $dst, 3)
    Write-Output 'Wallpaper set.'
}
