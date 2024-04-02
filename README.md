# Nina Prometheus Exporter

This is an exporter for NINA Astroimaging Software to Prometheus.
It can be used if you want to build your observatory dashboard i.e using Grafana.

Make sure you have the AdvancedAPI 1.0.1.1 plugin from Christan Palm installed and Enabled in NINA.

## Configuration

Configure exporter in config.yaml

```yaml
nina_server: url to ninas without port, e.g. 127.0.0.1
export_port: port to expose for prometheus e.g. 9091
frequency: frequency in sec to poll from Nina e.g 60
frequency_guider: frequency in sec to poll Guider e.g. 10
frequency_idle: frequency to poll if Nina is back up while Nina is offline, e.g. 120
debug: set to 0 for normal mode, set to 1 for generating random reports 
imagepath: path for the image preview to write out (jpg) 
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
| nina_weather_skytemperature | Sky Temperature |
| nina_weather_temperature | Temperature |
| nina_weather_humidity | Humidity |
| nina_weather_dewpoint | Dew Point |
| nina_safety_issafe | Safety Monitor Safe Reporting, -1 not connected, 0 unsafe, 1 safe |
| nina_dome_shutter | Dome Shutter status, -1 not connected, 0 open, 1 closed, 2 opening, 3 closing |

### Labels 
The symbols ```nina_image_hfr```, ```nina_image_stars``` and ```nina_image_mean``` have the following labels
|label|description|
|-----|-----------|
| target_name | the designated target name |
| filter_name | the filter name |

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

# Sample Grafana
This is a sample how a dahsboard could look like.
It's a screenshot of a live session from our JST Observatory.

![jst_dash2](https://github.com/jazzyoki/ninaexporter/assets/70711565/92d68369-9066-4f7e-aece-2fe143628554)
