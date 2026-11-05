# Nav guide (Fire Stick + Projectivy): known key paths, so no trial and error

Run a macro: `firetv.ps1 run <name>` (keys from `nav/<name>.txt`, then a 640px jpg). `firetv.ps1 go <keys>` = keys + jpg in one call.
Add a macro whenever a path works twice. One key per token; `#` = comment.

## Rules learned
- Keys go through ONE `monkey -f` script per call (~1.5 s + 0.15 s/key). `input keyevent` costs ~1 s per key; batched `input keyevent a b c` drops keys in animations; `sendevent` is blocked by SELinux.
- Put `wait` (1 s) after `home`, `menu` and any ok that opens a new screen, or later keys land on the old screen (e.g. ok launches the focused app).
- `shot` fails (empty file) while a DRM app (Netflix, Prime...) is in front: `stop` it first.
- `ui` (uiautomator dump) works but makes Projectivy toast "Accessibility service" (service stays bound). Prefer `go`/jpg in Projectivy; `ui` is fine in other apps.
- Fire keyboard (IME) is not in the ui dump. After `text`, press `right ok` (Previous -> Next) to confirm.
- `input keyevent --longpress 23` launches the app (no tile menu). `menu` (82) opens Projectivy's settings panel, not tile options.
- Row order (Custom sort) = order apps were ticked in Manage apps. To reorder: untick all, tick in the wanted order.
- Home focus lands on the 1st tile of the 1st row (Watch).

## Projectivy map
- Home: rows = Watch (Netflix, Prime, YouTube, Crave, Fibe TV, Tou.tv, TVA+, Plex, Kodi) then Settings shortcuts. TV Apps + Mobile Apps rows hidden.
- `menu` panel: All apps, Edit categories, Edit channels, Projectivy settings, Android settings, Display Profiles...
- Edit categories: New category, then rows (Watch, Settings, Display, Applications, System, About, Now Playing; hidden rows show an eye icon).
- Row settings: Title, Change icon, Visible, Grid, Sliding row, Show title, Size, Advanced settings > Sort, Set as default, Manage apps, Delete.
- Manage apps (alphabetical, focus starts at 1): 1 Luna, 2 Amazon Settings, 3 Crave, 4 Downloader, 5 Fibe TV, 6 Troubleshooting, 7 Tou.tv, 8 Kodi, 9 Music & More, 10 Netflix, 11 Plex, 12 Prime, 13 TVA+, 14 YouTube, then Mobile Apps. Shifts if apps are added/removed.
- Projectivy settings: General, Appearance (Categories/Channels, Cards, Wallpaper, Status Bar...), Power, Parental Control, Remote Control, Accessibility service, Display Profiles.
- Wallpaper source list: None, Reddit (random photos), Dynamic colors, Default wallpaper (set), Media file*, Folder* (*premium).
