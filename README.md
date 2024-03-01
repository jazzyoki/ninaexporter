# Nina Prometheus Exporter

This is an exporter for NINA Astroimaging Software to Prometheus.
It can be used if you want to build your observatory dashboard i.e using Grafana.

Make sure you have the AdvancedAPI plugin from Christan Palm installed and Enabled in NINA.

## Configuration

Configure exporter in config.yaml

```yaml
ninaserver: url to ninas without port, e.g. 127.0.0.1
exportport: port to expose for prometheus e.g. 9091
frequency: frequency in sec to poll from Nina e.g 60
frequency_guider: frequency in sec to poll Guider e.g. 10
frequency_idle: frequency to poll if Nina is back up while Nina is offline, e.g. 120
debug: set to 0 for normal mode, set to 1 for generating random reports 
```

## Exported Symbols

|name|description|
|----|-----------|
| nina_guider_rms_total_pixel | Total RMS error guiding in pixel |
| nina_guider_rms_total_arc | Total RMS error guiding in arcsec |
| nina_guider_dec_arc | Declination error in arcsec |
| nina_guider_ra_arc | Rectascension error in arcsec |
| nina_image_hfr | last Image HFR |
| nina_image_stars | bNumber of stars detected in current image |
| nina_image_mean | Mean value of the current image |
| nina_up | nina up and running [0,1] |

## Running the Code

I always prefer to run my python script in virtual environments, but thats up to you
if you like to do the same, set it up first

### create and activate virtual env

Windows:
```
cd \path\to\files
python -m venv ninaexporter
.\Scripts\activate
```
Linux:
```
cd /path/to/files
python -m venv ninaexporter
source ./bin/activate
```

### running
first make sure you have all the required modules installed
```console
pip install -r requirements.txt
```

then configure the configure.yaml to your liking or leave it default
and start
```
python exporter.py
```
