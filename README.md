# An Alfred Workflow that uses your Ente Exports

> [!WARNING]
> This workflow exports secrets from the Ente Auth CLI. Please exercise caution when using it.

## Setup

1. Install workflow from releases
2. Follow instructions below to create the database

## Instructions

1. Open Alfred
2. Go to Workflows.
3. Click the "Ente Auth" workflow and click the Configure Workflow button.
4. Next, configure the settings (NOTE: the export path is what you configured when adding your ente account).
5. Finally, run the Alfred command `ente import`.

## Local Development

### Install/Update dependencies
poetry install --only=main

### Build alfred workflow file
python3 build.py
