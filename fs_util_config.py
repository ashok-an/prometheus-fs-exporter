#!/usr/bin/env python

# <port> on which usage metrics is exposed
PROMETHEUS_METRICS_PORT = 19091

# List of all users
# note: users could be the names of the tools who depend on the paths
ALL_USERS = []

# Examples
# ALL_USERS = ['frontend', 'businesslogic']

# List of paths to monitor
# Each entry is a dictionary of {'path': <path string>, 'users': ['user1', 'user2' ...] }
PATH_CONFIGS = []

# Examples
# for env settings and NFS backup store
# PATH_CONFIGS.append({'path': '/auto/app-store', 'users': ['frontend', 'businesslogic']})

# for .node_modules
# PATH_CONFIGS.append({'path': '/home/ashok-an', 'users': ['frontend']})
