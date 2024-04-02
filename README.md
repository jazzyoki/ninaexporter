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

### Image Path
The image path is useful, if you want to expose the image via an web server that can be then linked into a dashboard container e.g. grafana.
In that case let the imagepath point to the webservers content folder.

## Running the Code

I always prefer to run my python script in virtual environments, but thats up to you
if you like to do the same, set it up first

### create and activate virtual env

Windows:
```shell
cd \path\to\files
python -m venv ninaexporter
.\Scripts\activate
```
Linux:
```sh
cd /path/to/files
python -m venv ninaexporter
source ./bin/activate
```

### running
first make sure you have all the required modules installed
```sh
pip install -r requirements.txt
```

then configure the configure.yaml to your liking or leave it default
and start
```sh
python exporter.py
```

## Configure Prometheus

Edit the '''config/prometheus.yaml''' file and append the following lines
```yaml
  - job_name: 'nina-export'
    scrape_interval: 10s
    static_configs:
      - targets: ['url_to_python_host:9099']
```

Note: a sample docker compose for prometheus and grafana is in this repository
```docker-compose.yml```

# Sample Architecture
![jst_architecture](https://github.com/jazzyoki/ninaexporter/assets/70711565/ea1f877b-ad29-494c-8e8a-eb250aa23f4e)

# Sample Grafana
This is a sample how a dahsboard could look like.

Here are some screenshots of a live session from our JST Observatory.

![jst_dash_preview](https://github.com/jazzyoki/ninaexporter/assets/70711565/d23c5669-5cce-49e3-8955-d45c412be7b8)
![jst_dash2](https://github.com/jazzyoki/ninaexporter/assets/70711565/92d68369-9066-4f7e-aece-2fe143628554)
