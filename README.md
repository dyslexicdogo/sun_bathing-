## Notifications

`sun_bathing` doesn't send notifications itself — notification setup varies
too much between users (which device, what time, how much detail) to bake
into the integration. Instead, a ready-made **Blueprint** is included so you
can set this up with a few clicks rather than hand-writing YAML.

### Import the blueprint

1. In Home Assistant: **Settings → Automations & Scenes → Blueprints tab → Import Blueprint**
2. Paste this URL (once pushed to GitHub):
   `https://github.com/dyslexicdogo/sun_bathing-/blob/main/blueprints/automation/sun_bathing/morning_notification.yaml`
3. Click **Preview** → **Import Blueprint**
4. Go to **Automations tab → Create Automation → pick "Sunbathing Morning Notification"**
5. Fill in the fields:
   - **Sunbathing Window Sensors** — select all 7 (10am-11am through 4pm-5pm)
   - **Notify Service** — e.g. `notify.mobile_app_your_phone` (find yours under **Developer Tools → Actions**, search "notify")
   - **Notification Time** — default 8:00 AM
   - **Minimum Score to Notify** — default 40 (skips notifying on days even the best window scores below this)
6. Save

Each day's notification replaces the previous one on your phone (uses a
notification tag), rather than piling up.