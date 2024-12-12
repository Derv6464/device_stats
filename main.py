import argparse
import subprocess
import sys

import helpers.config as config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', required=True, choices=['server', 'client'])
    parser.add_argument('-l', '--local', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def run_server():
    try:
        subprocess.run(['gunicorn', '--bind', '0.0.0.0:8000', 'server.server:app'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    agrs = main()
    config = config.Config_Helper('config.json')
    if agrs.local:
        config.set('server.database.host', 'EXTERNAL_URL')
    else:
        config.set('server.database.host', 'INTERNAL_URL')
        
    if agrs.run  == 'server':
        run_server()
    elif agrs.run == 'client':
        import client.client as client
        