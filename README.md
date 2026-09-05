# Discover Energy LYNK Cloud for Home Assistant

Unofficial Home Assistant integration for battery systems shown at
[mylynkcloud.com](https://mylynkcloud.com/lynk/). It discovers all LYNK controllers
and batteries available to an account and polls their current telemetry once per minute.

## Entities

- LYNK controller: state of charge, power, battery/alarm counts, lifetime charge and discharge.
- Each battery: state of charge, terminal voltage, current, battery and BMS temperatures,
  cell average/minimum/maximum/spread, installed capacity, lifetime charge/discharge,
  and a fault-or-warning binary sensor.

## Install with HACS

1. In HACS, open **Integrations**, choose the menu, then **Custom repositories**.
2. Add this GitHub repository as category **Integration**.
3. Download **Discover Energy LYNK Cloud** and restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**, search for
   **Discover Energy LYNK Cloud**, and enter your portal credentials.

For manual installation, copy `custom_components/lynk_cloud` into the
`custom_components` directory under your Home Assistant configuration and restart.

## Notes

- This is a cloud-polling integration and requires Internet access.
- Credentials are stored in the Home Assistant config entry. The short-lived API token is
  kept only in memory.
- This project uses an undocumented web API and is not affiliated with Discover Energy Systems.
  Portal changes may require an integration update.

## Troubleshooting

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.lynk_cloud: debug
```

Do not attach unredacted HAR files or logs to public issues; they may contain credentials,
authorization tokens, account details, and battery serial numbers.

