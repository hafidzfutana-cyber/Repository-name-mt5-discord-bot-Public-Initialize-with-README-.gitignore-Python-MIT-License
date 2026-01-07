markdown
# MT5 Discord Trade Bot

Bot Discord untuk notifikasi trade dari MetaTrader 5.

## Features
- Notifikasi entry trade otomatis
- Notifikasi TP/SL check setelah 2 hari
- Running 24/7 di Railway

## Setup
1. Set environment variables di Railway:
   - `DISCORD_TOKEN`: Token bot Discord
   - `DISCORD_CHANNEL_ID`: ID channel Discord
   - `JSON_URL`: URL JSON dari MT5

2. Bot akan auto-deploy ke Railway
