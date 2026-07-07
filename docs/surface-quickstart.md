# Surface Quickstart

## Install prerequisites

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip sqlite3 bluez rfkill
```

## Clone and install

```bash
cd ~
git clone https://github.com/RyanDoorkeeper/RoadRunner.git
cd RoadRunner
chmod +x install.sh
./install.sh
source .venv/bin/activate
```

## Test simulator mode

```bash
vehicleagent --simulator --samples 10 --print-json --db data/test.sqlite3
```

## Test ELM327 mode

Pair the ELM327 adapter first, then create a serial port such as `/dev/rfcomm0`.

Then test:

```bash
vehicleagent --elm327-port /dev/rfcomm0 --elm327-baud 38400 --samples 10 --print-json --db data/pathfinder.sqlite3 --verbose
```

If 38400 does not work, try 9600 or 115200.

## Check SQLite samples

```bash
sqlite3 data/pathfinder.sqlite3 'select id,timestamp,rpm,speed_mph,coolant_f,voltage from samples order by id desc limit 10;'
```

## Updating later

```bash
cd ~/RoadRunner
git pull
./install.sh
```
