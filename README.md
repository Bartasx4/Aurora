# Aurora Monitoring and Notification System 🌌

This project provides a Python-based solution for monitoring auroral activity (Northern Lights) and geomagnetic disturbances using external data sources. The system fetches real-time data about aurora levels and K-indices via APIs and sends push notifications to your mobile device using the [Pushover](https://pushover.net/) service.

## Features

- **Aurora Monitoring**: Fetches real-time aurora activity data from the [SWPC NOAA Ovation Aurora](https://www.swpc.noaa.gov/) API based on specified latitude and longitude.
- **K-index Monitoring**: Retrieves geomagnetic K-index data to analyze global geomagnetic storm conditions.
- **Automated Notifications**: Sends push notifications to your mobile device when activity thresholds are surpassed.
- **Custom Delays**: Differentiates between daytime and nighttime to reduce unnecessary notifications during specific periods.

---

## Usage

### Prerequisites

1. Python `>=3.13.0`
2. Install the necessary dependencies. Run:

   ```bash
   pip install requests
   ```

3. Register with [Pushover](https://pushover.net/) to obtain the following:
    - **API Token** for your application.
    - **User Key** for the device receiving notifications.

4. [Optional] Adjust latitude, longitude, and language preferences to match your location and notification needs.

---

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/aurora-monitor.git
   cd aurora-monitor
   ```

2. Set environment variables for your Pushover API credentials:
    - `USER_KEY` – Your Pushover user key.
    - `API_KEY` – Your Pushover application token.

   Example:
   ```bash
   export USER_KEY=your-user-key
   export API_KEY=your-api-token
   ```

   Alternatively, hardcode these values in the `example.py` file.

3. Modify the following configuration variables in `example.py` according to your preferences:
    - **LATITUDE**: Latitude of your location (e.g., `60`).
    - **LONGITUDE**: Longitude of your location (e.g., `18`).
    - **LANGUAGE**:
        - `pl` for Polish
        - `en` for English

---

### Running the Program

To execute the program, run:

```bash
python example.py
```

The program will start monitoring auroral and geomagnetic activity continuously. Use `Ctrl+C` to stop the execution.

---

### Example Configuration (`example.py`)
Below is an example of how to configure the program:

```python
USER_KEY = os.getenv('USER_KEY')
API_KEY = os.getenv('API_KEY')

LATITUDE = 60  # Example location
LONGITUDE = 18  # Example location
LANGUAGE = 'en'  # Language

if __name__ == '__main__':
    aurora_monitor = initialize_aurora_monitor(API_KEY, USER_KEY, LATITUDE, LONGITUDE, LANGUAGE)
    aurora_monitor.start_loop()
```

---

## Data Sources 🛰️

- **[SWPC/NOAA Ovation Aurora API](https://www.swpc.noaa.gov/)**:
  Provides data about auroral activity across the globe for a specific area based on your latitude and longitude.

- **[SWPC/NOAA K-Index API](https://www.swpc.noaa.gov/)**:
  Offers real-time geomagnetic index data, which is used to detect geomagnetic storm conditions globally.

---

## Notifications

This project uses [Pushover](https://pushover.net/) to send push notifications to your mobile device. You need to configure your API and User tokens to enable this feature.

Notifications are categorized based on activity levels:
- **Aurora Levels** specific to your location:
    - 90: You have it on your head!
    - 80: Very likely!
    - 70: Significant chances.
    - 50: Might happen, keep an eye out.
    - 30: Very unlikely, but possible under rare conditions.

- **K-index Levels** based on global activity:
    - 9: You must see it!
    - 8: Very likely!
    - 7: High chance today.
    - 6: Moderate chance today.
    - 5: Low chance today.
