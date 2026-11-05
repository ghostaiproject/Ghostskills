# Fire Stick UX preset, run by `firetv.ps1 ux` (adb shell). Reverse: firetv.ps1 ux-reset
for k in window_animation_scale transition_animation_scale animator_duration_scale; do settings put global $k 0.5; done
for k in limit_ad_tracking amz_limit_ad_tracking non_amz_limit_ad_tracking; do settings put secure $k 1; done
for k in USAGE_METRICS_UPLOAD_ENABLED usage_metrics_marketing_enabled pact_usage_collection_enabled advertisingIdApp:interestBasedAds:value settingsApp:appUsageData:value settingsApp:deviceUsageData:value; do settings put secure "$k" 0; done
for k in advertisingIdApp:interestBasedAds:syncPending settingsApp:appUsageData:syncPending settingsApp:deviceUsageData:syncPending; do settings put secure "$k" true; done
echo "anim $(settings get global window_animation_scale) | limit_ads $(settings get secure limit_ad_tracking) | usage $(settings get secure settingsApp:appUsageData:value)"
