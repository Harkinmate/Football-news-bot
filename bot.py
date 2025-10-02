name: BBC Football Telegram Bot

on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  push:
    branches:
      - main

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install python-telegram-bot feedparser requests beautifulsoup4

      - name: Run Telegram Bot
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
        run: |
          python bot.py
