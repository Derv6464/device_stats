import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', required=True, choices=['server', 'client'])
    args = parser.parse_args()
    return args.run

def run_server():
    try:
        # Modify 'app:app' to point to your WSGI app, e.g., `myapp:app`
        subprocess.run(['gunicorn', '--bind', '0.0.0.0:8000', 'server.server:app'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    running = main()

    if running == 'server':
        run_server()
    elif running == 'client':
        import client.client as client
        client.run()