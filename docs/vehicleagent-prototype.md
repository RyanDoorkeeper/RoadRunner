# VehicleAgent Prototype

This is the first useful RoadRunner vehicle data milestone.

The prototype goal is intentionally small:

```text
ELM327 adapter
  -> VehicleAgent
  -> SQLite
  -> optional terminal output
  -> optional MQTT later
```

No HuDiY, Home Assistant, LubeLogger, Grafana, or UI is required for this milestone.

## Install locally on the Surface

From a clone of the repo:

```bash
python3 -m pip install --user -e .
```

If the `vehicleagent` command is not found after install, run it as a module:

```bash
python3 -m vehicleagent --help
```

## Finding the ELM327 port

### USB ELM327

A USB adapter will usually appear as one of:

```text
/dev/ttyUSB0
/dev/ttyACM0
```

Check with:

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

### Bluetooth ELM327

For a generic Bluetooth ELM327 adapter, pair it first with BlueZ/KDE, then bind it to an RFCOMM serial port.

Example:

```bash
bluetoothctl
scan on
pair AA:BB:CC:DD:EE:FF
trust AA:BB:CC:DD:EE:FF
quit
```

Then bind:

```bash
sudo rfcomm bind rfcomm0 AA:BB:CC:DD:EE:FF 1
```

The port should then be:

```text
/dev/rfcomm0
```

To release it later:

```bash
sudo rfcomm release rfcomm0
```

## First simulator test

Before testing real OBD hardware, verify SQLite logging works:

```bash
python3 -m vehicleagent --simulator --samples 5 --print-json --db data/test.sqlite3
```

Expected result:

- JSON samples print to the terminal.
- `data/test.sqlite3` is created.
- Samples are stored in SQLite.

## First real ELM327 test

Try 38400 baud first:

```bash
python3 -m vehicleagent \
  --elm327-port /dev/rfcomm0 \
  --elm327-baud 38400 \
  --samples 10 \
  --print-json \
  --db data/pathfinder.sqlite3 \
  --verbose
```

If that fails, try common clone speeds:

```bash
--elm327-baud 9600
--elm327-baud 115200
```

## What it currently reads

VehicleAgent currently attempts:

- RPM
- Vehicle speed
- Coolant temperature
- Intake air temperature
- Voltage from `ATRV`
- Throttle position
- Engine load
- Fuel level, if the vehicle reports PID `2F`

Cheap ELM327 adapters and older vehicles may return `null` for some values. That is expected.

## SQLite database

The database contains a `samples` table with structured columns and the original JSON payload.

Important columns:

- `timestamp`
- `rpm`
- `speed_mph`
- `coolant_f`
- `intake_air_f`
- `voltage`
- `throttle_percent`
- `engine_load_percent`
- `fuel_level_percent`
- `payload_json`
- `sent_mqtt`

## Query samples

```bash
sqlite3 data/pathfinder.sqlite3 'select id,timestamp,rpm,speed_mph,coolant_f,voltage from samples order by id desc limit 10;'
```

## MQTT later

MQTT is disabled by default for the prototype so local OBD logging can be tested without Home Assistant or network access.

To enable MQTT:

```bash
python3 -m vehicleagent \
  --elm327-port /dev/rfcomm0 \
  --mqtt-host homeassistant.local \
  --base-topic car/pathfinder
```

For the current milestone, SQLite logging is more important than MQTT.

## Success criteria

This milestone is successful when the Surface can:

1. Connect to the generic ELM327 adapter.
2. Read RPM at least once.
3. Store timestamped samples in SQLite.
4. Keep running for several minutes without corrupting the database.
5. Stop cleanly with Ctrl+C.

After that, MQTT and offline replay can be built on top of the same local data path.
