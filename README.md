# prometheus-fs-exporter
Exposes the following metrics:
* fs_utils_total_space_gigabytes{path='/path', users='user1,user2'}
* fs_utils_avail_space_gigabytes{path='/path', users='user1,user2'}
* fs_utils_used_to_total_ratio{path='/path', users='user1,user2'}

# Requirements
* python >= 3.3
* prometheus_client python library

# Usage
The script reads `fs_util_config.py` in the same directory
* To print the config template:
> python main.py --template

* To verify correctness of fs_util.config.py:
> python main.py --verify

* Normal run
> python main.py

# Docker
TODO

# Notes
* If a path is not available, the values are reported as *0*
* Data is exposed on *19091* or *fs_util_config.py:PROMETHEUS_METRICS_PORT*
* It can be queried on *http://<ip-addr>:$PROMETHEUS_METRICS_PORT/metrics*
* There is a 30sec delay b/n the subsequent checks
