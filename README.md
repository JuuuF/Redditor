# Redditor

A Reddit Data Collector for Trend examination.

This project is a means for me in order to get into data engineering and learn about this job's nooks and crannies. The goal of this project is not to create something ground breaking, but for me to learn as much as possible.

## Quick Start

### 1. Reddit Authentication

Echo the reddit API secret into the associated secret file.

```bash
rm -f secrets/reddit_api_secret
echo "$REDDIT_API_SECRET" > secrets/reddit_api_secret
```

### 2. Execution

The system is based upon Docker. To start the system, run:

```bash
docker compose up -d
```
