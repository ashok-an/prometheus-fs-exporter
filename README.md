# prometheus-fs-exporter
Exposes the following metrics:
* fs_utils_total_space_gigabytes{path='/path', users='user1,user2', desc='something'}
* fs_utils_avail_space_gigabytes{path='/path', users='user1,user2', desc='something else'}
* fs_utils_used_to_total_ratio{path='/path', users='user1,user2', desc='even more of something'}

# Requirements
* python >= 3.3
* prometheus_client python library

# Usage
```
> ./main.py -h
usage: main.py [-h] [-a {sample-config,check-config,run}] [-c CONFIG]
               [-mp METRIC_PREFIX]

optional arguments:
  -h, --help            show this help message and exit
  -a {sample-config,check-config,run}, --action {sample-config,check-config,run}
                        action to be taken, default:run
  -c CONFIG, --config CONFIG
                        path to config.json (default: ./config.json)
  -mp METRIC_PREFIX, --metric_prefix METRIC_PREFIX
                        prefix for the published metrics (default: fs_util)
>
```

# Sample output
```
$ python main.py -mp test_du


$ curl localhost:19091/metrics
...
 TYPE process_max_fds gauge
process_max_fds 1024.0
# HELP test_du_total_space_gigabytes Total bytes in the mount-point
# TYPE test_du_total_space_gigabytes gauge
test_du_total_space_gigabytes{desc="store for .node_modules/",path="/home/ashok",users="frontend"} 1664.0
test_du_total_space_gigabytes{desc="store for .node_modules/",path="/ws/ashok",users="frontend"} 32.0
# HELP test_du_avail_space_gigabytes Total available space in the mount-point
# TYPE test_du_avail_space_gigabytes gauge
test_du_avail_space_gigabytes{desc="store for .node_modules/",path="/home/ashok",users="frontend"} 1029.8919677734375
test_du_avail_space_gigabytes{desc="store for .node_modules/",path="/ws/ashok",users="frontend"} 19.597198486328125
# HELP test_du_used_to_total_ratio Ratio of used-up space in mount-point
# TYPE test_du_used_to_total_ratio gauge
test_du_used_to_total_ratio{desc="store for .node_modules/",path="/home/ashok",users="frontend"} 0.3810745385976938
test_du_used_to_total_ratio{desc="store for .node_modules/",path="/ws/ashok",users="frontend"} 0.3875875473022461
```

# Notes
* If an accepted path is not available, it's values are reported as *0*
* Data is exposed on *19091* by default
* It can be queried on *http://<ip-addr>:$PROMETHEUS_METRICS_PORT/metrics*
* There is a 30sec delay b/n the subsequent checks


### Q. Why .json, why not .yaml?
A. Not comfortable with PyYaml
