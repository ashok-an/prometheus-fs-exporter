#!/usr/bin/env python

import argparse
import logging
import os
import shutil
import sys
import time
import prometheus_client as PC

logger = logging.getLogger('prom_fs_util')
logging.basicConfig(format='%(asctime)s %(levelname)8s: %(message)s')
logger.setLevel(logging.DEBUG)

SLEEP_INTERVAL_SEC = 30

sys.path.append('.')
import fs_util_config as FS

def print_template_and_exit():
	if os.path.isfile('./fs_util_config.py.sample'):
		with open('fs_util_config.py.sample') as fd:
			data = fd.readlines()
		# with
		for line in data:
			sys.stdout.write(line)
		# for
	else:
		logger.critical('Unable to locate fs_util_config.py.sample')
	# if
	sys.exit(2)
# end

def is_invalid_path_config(entry):
	isInvalid = False
	if 'path' not in entry:
		logger.error('Missing path in path-config:{}'.format(entry))
		isInvalid = True
	elif 'users' not in entry:
		logger.error('Missing users[] in path-config:{}'.format(entry))
		isInvalid = True
	elif not os.path.exists(entry.get('path', '/invalid-path')):
		logger.error('Unreachable path:{} in path-config:{}'.format(entry.get('path', '/invalid-path'), entry))
		isInvalid = True
	else:
		for u in entry.get('users', []):
			if u not in FS.ALL_USERS:
				logger.error('Invalid user:{} in path-config:{}'.format(u, entry))
				isInvalid = True
				break
			# if
		# for
	# if

	if isInvalid:
		logger.info('Pruning {} from PATH_CONFIGS[]'.format(entry.get('path', '/invalid-path')))
	else:
		logger.info("Config is GOOD: {}".format(entry))
	# if

	return isInvalid
# end

def verify_template():
	isValid = True
	if not FS.PROMETHEUS_METRICS_PORT:
		logger.error('PROMETHEUS_METRICS_PORT not defined')
		isValid = False
	if not FS.ALL_USERS:
		logger.error('ALL_USERS not defined')
		isValid = False
	if not FS.PATH_CONFIGS:
		logger.error('PATH_CONFIGS not defined')
		isValid = False
	if not len(FS.ALL_USERS):
		logger.error('ALL_USERS is empty')
		isValid = False
	if not len(FS.PATH_CONFIGS):
		logger.error('PATH_CONFIGS is empty')
		isValid = False

	configErrors = 0
	validConfigs = []
	for entry in FS.PATH_CONFIGS:
		if is_invalid_path_config(entry):
			configErrors += 1
		else:
			validConfigs.append(entry)
		# if
	# for
	if configErrors:
		logger.error('Found {} path config errors'.format(configErrors))
	# if
	return isValid, validConfigs
# end

def get_usage(inputPath):
	ONE_GB = 1024 * 1024 * 1024
	total, used, avail = 0, 0, 0
	try:
		i = shutil.disk_usage(inputPath)
		total, used, avail = i.total/ONE_GB, i.used/ONE_GB, i.free/ONE_GB
	except:
		pass
	return total, used, avail
# end

def process_valid_configs(inputConfigs):
	# setup infra
	totalGauge = PC.Gauge('fs_utils_total_space_gigabytes', 'Total bytes in the mount-point', ['path', 'users'])
	availGauge = PC.Gauge('fs_utils_avail_space_gigabytes', 'Total available space in the mount-point', ['path', 'users'])
	usedGauge  = PC.Gauge('fs_utils_used_to_total_ratio', 'Ratio of used-up space in mount-point', ['path', 'users'])
	PC.start_http_server(int(FS.PROMETHEUS_METRICS_PORT))

	while True:
		for entry in inputConfigs:
			path, users  = entry['path'], ','.join(sorted(entry['users'])) 
			total, used, avail = get_usage(path)
			usedRatio = used / total if total else 1 #to raise alarm

			totalGauge.labels(path=path, users=users).set(total)
			availGauge.labels(path=path, users=users).set(avail)
			usedGauge.labels(path=path, users=users).set(usedRatio)

			logger.info("metric<path={}, total={}, avail={}, usedRatio={}>".format(path, total, avail, usedRatio))
		# for
		logger.info("sleep {}".format(SLEEP_INTERVAL_SEC))
		time.sleep(SLEEP_INTERVAL_SEC)
	# while
# end

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--template', action='store_true', help='print fs_util_config.py template and exit(2)')
	parser.add_argument('-v', '--verify', action='store_true', help='verify fs_util_config.py and exit(0)')
	args = parser.parse_args()

	if args.template:
		print_template_and_exit()

	isTemplateValid, validConfigs = verify_template()
	if not isTemplateValid:
		logger.critical('Invalid input configuration; exiting with status=1')
		sys.exit(1)
	elif not validConfigs:
		logger.critical('No valid path-configs found to process; exiting with status=1')
		sys.exit(1)
	# if

	logger.info("Verification successful")
	logger.info("+ Metrics can be queried on: 'http://localhost:{}/metrics'".format(FS.PROMETHEUS_METRICS_PORT))
	logger.info("+ User list: {}".format(FS.ALL_USERS))
	logger.info("+ Valid path config count: {}".format(len(validConfigs)))

	if args.verify:
		logger.info("No processing requested (--verify mode); exiting with status=0")
		sys.exit(0)
	# if

	logger.info("Start monitoring ...")
	
	process_valid_configs(validConfigs)
