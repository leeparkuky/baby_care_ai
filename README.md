# Baby Care AI

Automated system for collecting, deduplicating, and syncing baby monitor images from Blink cameras to Google Drive.

## Features

- **Automated Collection**: Takes snapshots from Blink cameras every 3 minutes.
- **Intelligent Deduplication**: Removes near-identical images every hour using perceptual hashing.
- **Cloud Sync**: Automatically uploads unique images to Google Drive every hour.
- **Installable Package**: Easy setup using standard Python packaging.

## Prerequisites

- **Conda Environment**: Recommended environment name is `blink`.
- **Blink Account**: Access to Blink Home Security cameras.
- **Google Drive API**: Access to a Google Cloud Project.

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd baby_care_ai
   ```

2. **Activate environment**:
   ```bash
   conda activate blink
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Obtain Credentials**:
   - **Blink**: No file is needed initially. The system will prompt you for your Blink credentials and 2FA code on the first run, then save them to the path defined in your `.env`.
   - **Google Drive**: 
     1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
     2. Create a new project and enable the **Google Drive API**.
     3. Go to **Credentials**, click **Create Credentials** > **OAuth client ID**.
     4. Select **Desktop App** as the application type.
     5. Download the JSON file and save it as your `google_drive_cred.json`.
     6. For detailed steps, refer to the [PyDrive2 Documentation](https://docs.iterative.ai/PyDrive2/quickstart/#authentication).

5. **Configure the environment**:
   Run the setup script to create your `.env` file and point to your credential files:
   ```bash
   python setup_config.py
   ```

## Usage

### Run Automation

Start the background service (3-minute collection, 1-hour sync):

```bash
baby-care-automation
```

Or run the script directly:

```bash
python scripts/automation.py
```

### Manual Controls

- **Collect images**: `python -m baby_care_ai.blink.collect`
- **Deduplicate images**: `python -m baby_care_ai.blink.dedup`
- **Sync to Drive**: `python -m baby_care_ai.gooogle_drive.drive_utils`

## Project Structure

- `baby_care_ai/`: Core package logic.
  - `automation_logic.py`: The main loop orchestrator.
- `scripts/`: Execution wrappers.
- `setup_config.py`: Interactive configuration tool.
- `.env_example`: Template for environment variables.
- `pyproject.toml`: Package configuration.
