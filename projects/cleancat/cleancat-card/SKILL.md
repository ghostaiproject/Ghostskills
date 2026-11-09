---
name: cleancat-card
description: Use only when a core skill (load, save, cmds) picks cleancat (#5): holds the CleanCat cleaning calendar app's card (CER-01 unit 06). Never typed by the user.
---
# cleancat card
ctx cleancat · #5 · cleaning calendar Android app · repo ghostaiproject/Cleaningcalendar (private) · branch main · state HANDOFF.md (French) · also load: — · load extras: `adb devices` (phone on? wireless debugging port changes after Wi-Fi drops) · save extras: CER-01 unit 06 card if version/status changed (cer01-releases `units.json`, `ver`).
Ship: API = push to main → Vercel deploys (cleaningcalendar-gamma.vercel.app) · APK = push in `android/**` → `.github/workflows/apk.yml` → release `apk` (Propre.apk, main only); version in `android/app/build.gradle.kts` (verMajor/Minor/Patch) · branch build on the phone: `scripts/apk-test.sh run` · local: `npm run check` (API tests + French text) · `npm run e2e`.
List: default (DECISIONS.md, PLAN.md, IMPROVEMENTS.md, QA-LOG.md) · Extra cmds: /phone shot|tap|swipe|fold|unfold → `scripts/phone.sh …`.
App: Kotlin Compose, package `dev.ghost.propre` (internal name Propre), UI text in French. Signing key stays out of git (`~/.android-keys/propre/`). Secrets live only in Vercel.
