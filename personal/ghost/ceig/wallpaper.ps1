# Upscale the newest Gemini download to 3840x2160 (center-cropped to 16:9); optionally set it as wallpaper.
param([Parameter(Mandatory)][string]$Name, [switch]$SetWallpaper)
Add-Type -AssemblyName System.Drawing

$src = (Get-ChildItem "$env:USERPROFILE\Downloads\Gemini_Generated_Image_*" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName
if (-not $src) { throw 'No Gemini_Generated_Image_* in Downloads' }
$dst = "$env:USERPROFILE\Pictures\Wallpapers\$Name.png"
New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null

$img = [System.Drawing.Image]::FromFile($src)
$cw = [math]::Min($img.Width, [int]($img.Height * 16 / 9)); $ch = [int]($cw * 9 / 16)
$cx = [int](($img.Width - $cw) / 2); $cy = [int](($img.Height - $ch) / 2)
$bmp = New-Object System.Drawing.Bitmap 3840, 2160
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = 'HighQualityBicubic'; $g.PixelOffsetMode = 'HighQuality'; $g.CompositingQuality = 'HighQuality'
$attr = New-Object System.Drawing.Imaging.ImageAttributes; $attr.SetWrapMode('TileFlipXY')
$g.DrawImage($img, (New-Object System.Drawing.Rectangle 0, 0, 3840, 2160), $cx, $cy, $cw, $ch, 'Pixel', $attr)
Write-Output "Source: $src ($($img.Width)x$($img.Height))"
$g.Dispose(); $img.Dispose(); $bmp.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Write-Output "Saved: $dst (3840x2160)"

if ($SetWallpaper) {
    Set-ItemProperty 'HKCU:\Control Panel\Desktop' WallpaperStyle '10'
    Set-ItemProperty 'HKCU:\Control Panel\Desktop' TileWallpaper '0'
    Add-Type -Namespace Win -Name WP -MemberDefinition '[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int SystemParametersInfo(int a, int b, string c, int d);'
    [void][Win.WP]::SystemParametersInfo(0x14, 0, $dst, 3)
    Write-Output 'Wallpaper set.'
}
