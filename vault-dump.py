#! /usr/bin/env python
#
# Dumps a HashiCorp Vault database to write statements.
# Useful for backing up in-memory vault data
# and later restoring from the generated script.
#
# Requires: an already-authenticated session
#
# Reads env vars:
# - VAULT_ADDR  which points to desired Hashicorp Vault instance, default http://localhost:8200
# - TOP_VAULT_PREFIX to specify path to dump, for partial backups, default /secret/
# - MOUNT_POINT to vault mount point, default /
#
# Use custom encoding:
#   PYTHONIOENCODING=utf-8 python vault-dump.py
#
# Copyright (c) 2017 Shane Ramey <shane.ramey@gmail.com> updated by Steven Clarkson <sclarkso@gmail.com>
# Licensed under the Apache License, Version 2.0
from __future__ import print_function
import sys
import subprocess
import os
import pwd
import hvac
import datetime

def print_header():
    user = pwd.getpwuid(os.getuid()).pw_name
    date = "{} UTC".format(datetime.datetime.utcnow())
    vault_address = os.environ.get('VAULT_ADDR')
    top_vault_prefix = os.environ.get('TOP_VAULT_PREFIX','/secret/')
    mount_point = os.environ.get('MOUNT_POINT', '/')

    print ('#')
    print ('# vault-dump.py backup')
    print ("# dump made by {}".format(user))
    print ("# backup date: {}".format(date))
    print ("# VAULT_ADDR env variable: {}".format(vault_address))
    print ("# TOP_VAULT_PREFIX env variable: {}".format(top_vault_prefix))
    print ("# MOUNT_POINT env variable: {}".format(mount_point))
    print ('# STDIN encoding: {}'.format(sys.stdin.encoding))
    print ('# STDOUT encoding: {}'.format(sys.stdout.encoding))
    print ('#')
    print ('# WARNING: not guaranteed to be consistent!')
    print ('#')

# looks at an argument for a value and prints the key
#  if a value exists
def recurse_for_values(path_prefix, candidate_key):
    candidate_values = candidate_key['data']['keys']
    for candidate_value in candidate_values:
        next_index = path_prefix + candidate_value
        if candidate_value.endswith('/'):
            next_value = client.secrets.kv.v2.list_secrets(next_index, mount_point=m1ount_point)
            recurse_for_values(next_index, next_value)
        else:
            stripped_prefix=path_prefix[:-1]
            final_dict = client.secrets.kv.v2.read_secret_version(next_index, mount_point=m1ount_point)['data']
            print ("\nvault write {}".format(next_index), end='')

            sorted_final_keys = sorted(final_dict.keys())
            for final_key in sorted_final_keys:
                final_value = final_dict[final_key]
                try:
                    final_value = final_value.encode("utf-8")
                except AttributeError:
                    final_value = final_value
                print (" {0}={1}".format(final_key, repr(final_value)), end='')


env_vars = os.environ.copy()
hvac_token = subprocess.check_output(
    "vault read -field id auth/token/lookup-self",
    shell=True,
    env=env_vars)

hvac_url = os.environ.get('VAULT_ADDR','http://localhost:8200')
hvac_client = {
    'url': hvac_url,
    'token': hvac_token,
}
client = hvac.Client(**hvac_client)
assert client.is_authenticated()

top_vault_prefix = os.environ.get('TOP_VAULT_PREFIX','/secret/')
m1ount_point = os.environ.get('MOUNT_POINT','/')

print_header()
top_level_keys = client.secrets.kv.v2.list_secrets(top_vault_prefix, mount_point=m1ount_point) 
recurse_for_values(top_vault_prefix, top_level_keys)
