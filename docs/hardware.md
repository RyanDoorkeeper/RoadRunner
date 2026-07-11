# Hardware Notes

## Vehicle

- 2007 Nissan Pathfinder
- Factory Bose audio system retained initially
- Audio target: reliable AUX or USB-audio feed without replacing the radio

## Platform direction

RoadRunner began on a Microsoft Surface Pro 4 as a proof of concept. The intended long-term platform is the Dell Latitude 7210 Rugged Extreme. Surface-specific work should be preserved as prototype history, while new code and deployment decisions should favor portability to the Latitude.

### Surface Pro 4 prototype

- Debian Trixie with KDE Plasma
- linux-surface kernel and IPTSD touchscreen support
- USB Android Auto through HuDiY validated with a direct cable
- Built-in Marvell Bluetooth is unreliable, especially after suspend/resume
- Baseus USB Bluetooth adapter works more reliably
- High-DPI 3:2 display and fractional scaling require UI testing

### Dell Latitude 7210 Rugged Extreme target

Known or seller-reported details from the unit under consideration:

- Two USB-C ports
- One USB-A port
- Keyboard included
- No power cable included
- Seller-reported battery health near 95%; verify on receipt
- Seller listed 256 GB storage; verify actual drive and health
- Dell configuration information showed Computrace disabled

Reasons for migration:

- Rugged enclosure better suited to vehicle use
- More practical I/O for charging, phone, OBD, GPS, audio, and cameras
- Better mounting and serviceability potential
- Less dependence on Surface-specific kernel components
- Better foundation for a later installation in the camping van

The final operating system remains a deployment decision. Keep the core service portable enough for Linux first, while avoiding unnecessary assumptions that would prevent a Windows build if hardware testing makes it preferable.

## Proposed peripheral layout

A likely arrangement is:

- USB-C 1: automotive USB-C PD power or dock power input
- USB-C 2: phone data, dock, or expansion
- USB-A: OBD-II, GPS, Bluetooth, or a tested hub
- 3.5 mm output or USB audio: factory-radio AUX input

Do not finalize the topology until simultaneous charging, Android Auto, USB tethering, and peripheral behavior are tested on the Latitude.

## OBD-II

Initial development uses a generic ELM327-class adapter. It is suitable for proving the data path but clone quality and protocol behavior vary.

Initial PIDs:

- RPM
- Vehicle speed
- Coolant temperature
- Intake-air temperature
- Throttle position
- Engine load
- Fuel trims
- Control-module voltage when supported
- Diagnostic trouble codes

The software must abstract the adapter and support reconnects, timeouts, malformed responses, configurable endpoints, adapter identity logging, and a simulator. Possible upgrades include OBDLink CX or OBDLink EX.

## GPS

Use a USB GNSS receiver if built-in location hardware is absent or unreliable. On Linux, prefer hardware supported by `gpsd`. Record time, position, speed, heading, altitude, fix type, satellite count, and accuracy when available.

## Audio

Retain the factory Bose radio. Test analog AUX and USB audio for:

- Ground-loop noise
- Volume consistency
- Resume behavior
- Android Auto routing
- Microphone behavior if voice commands are used

## Power

The permanent installation needs an automotive-rated power design:

- Correct USB-C PD profile and adequate wattage for the Latitude
- Input protection for automotive transients
- Stable behavior during engine cranking
- Fusing near the source
- No unacceptable parked battery drain
- Graceful suspend or shutdown after accessory power is removed

## Mounting and thermal requirements

- Do not obstruct airbags, gauges, controls, or sight lines.
- Secure the tablet and cables for hard braking and rough roads.
- Provide airflow and reduce direct-sun heating where practical.
- Add strain relief and keep the tablet removable for maintenance.

## Validation checklist

1. Confirm the Latitude's exact CPU, RAM, storage, BIOS, battery, and Computrace state.
2. Confirm charging wattage and load behavior.
3. Test all USB ports independently and concurrently.
4. Test suspend/resume with OBD, GPS, phone, Bluetooth, and audio attached.
5. Test direct and docked USB Android Auto.
6. Test USB tethering while Android Auto is active.
7. Measure idle, active, suspend, and shutdown power draw.
8. Validate cold-weather startup and battery behavior before permanent installation.
