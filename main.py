#!/usr/bin/env python

import argparse
import json
import logging
import os
import shutil
import sys
import time
import prometheus_client as PC

logger = logging.getLogger('prom_fs_util')
logging.basicConfig(format='%(asctime)s %(levelname)8s: %(message)s')
logger.setLevel(logging.DEBUG)

DEFAULT_PORT = 19091
SLEEP_INTERVAL_SEC = 30

def die(message, status=1):
	logger.critical('{}; exiting with status={}'.format(message, status))
	sys.exit(status)
# end

def print_template():
	sys.path.append('.')
	try:
		with open('./config.json.sample') as fd:
			data = fd.readlines()
		for line in data:
			sys.stdout.write(line)
	except:
		die('Unable to locate config.json.sample')
	# try
# end

def parse_config_file(filePath):
	data = {}
	try:
		with open(filePath, 'r') as fd:
			data = json.load(fd)
	except:
		die('JSON parsing failed for {}'.format(filePath))
	return data
# end

def validate_config_data(data):
	output = data
	if 'port' not in data:
		logger.error('No value for key:port in input-config; will use {}'.format(DEFAULT_PORT))

	elif 'all_users' not in data:
		die('No value for key:all_users in input-config')
	elif not data.get('all_users', []):
		die('Empty list:all_users in input-config')

	elif 'path_configs' not in data:
		die('No value for key:path_configs in input-config')
	elif not data.get('path_configs', []):
		die('Empty list:path_configs in input-config')

	else:
		validPathConfigs = []
		for i in data.get('path_configs', []):
			errors = []
			try:
				path, users, desc = i['path'], i['users'], i['desc']
				if not os.path.exists(path):
					errors.append('Invalid path:{}'.format(path))
				if not desc:
					error.append('No description for path:{}'.format(path))
				if not users:
					error.append('No users for path:{}'.format(path))
				for u in users:
					if u not in data['all_users']:
						errors.append('Invalid user:{} for path:{}'.format(u, path))
				# for
				if errors:
					logger.error('Found {} errors in path_config:{} - {}'.format(len(errors), path, errors))
				else:
					validPathConfigs.append(i)
				# if
			except:
				logger.error('Unable to parse path_configs[]')
		# for
		output['valid_path_configs'] = validPathConfigs
	# else
	return output
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

def process_valid_configs(data, prefix):
	# setup infra
	totalGauge = PC.Gauge('{}_total_space_gigabytes'.format(prefix), 'Total bytes in the mount-point', ['desc', 'path', 'users'])
	availGauge = PC.Gauge('{}_avail_space_gigabytes'.format(prefix), 'Total available space in the mount-point', ['desc', 'path', 'users'])
	usedGauge  = PC.Gauge('{}_used_to_total_ratio'.format(prefix), 'Ratio of used-up space in mount-point', ['desc', 'path', 'users'])
	PC.start_http_server(int(data.get('port', DEFAULT_PORT)))

	while True:
		for entry in data.get('valid_path_configs', []):
			path, users, desc  = entry['path'], ','.join(sorted(entry['users'])), entry['desc']
			total, used, avail = get_usage(path)
			usedRatio = used / total if total else 1 #to raise alarm

			totalGauge.labels(desc=desc, path=path, users=users).set(total)
			availGauge.labels(desc=desc, path=path, users=users).set(avail)
			usedGauge.labels(desc=desc, path=path, users=users).set(usedRatio)

			logger.info("+ metric<path={}, total={}, avail={}, usedRatio={}>".format(path, total, avail, usedRatio))
		# for
		logger.info("sleep {}".format(SLEEP_INTERVAL_SEC))
		time.sleep(SLEEP_INTERVAL_SEC)
	# while
# end

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--action', help='action to be taken, default:run', choices=['sample-config', 'check-config', 'run'], default='run')
	parser.add_argument('-c', '--config', help='path to config.json (default: ./config.json)', default='config.json')
	parser.add_argument('-mp', '--metric_prefix', help='prefix for the published metrics (default: fs_util)', default='fs_util')
	args = parser.parse_args()

	if args.action == 'sample-config':
		print_template()
		sys.exit(0)

	inputJson = args.config
	logger.info('Input config file:{}'.format(inputJson))
	interim = parse_config_file(inputJson)
	data = validate_config_data(interim)

	if args.action == 'check-config':
		sys.exit(0)

	configPaths = data.get('valid_path_configs', [])
	if not configPaths:
		die('No valid path_configs to monitor', 2)

	logger.info('Template validation completed; found {} path_configs to monitor'.format(len(configPaths)))
	print()
	logger.info('Publishing metrics on http://<host-ip>:{}/metrics ...'.format(data['port']))
	while True:
		process_valid_configs(data, args.metric_prefix)
		logger.info("sleep {}".format(SLEEP_INTERVAL_SEC))
	# while
# end
