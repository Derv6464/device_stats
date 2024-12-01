import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', required=True, choices=['server', 'client'])
    args = parser.parse_args()
    return args.run

if __name__ == '__main__':
    running = main()

    if running == 'server':
        from server.server import app
        app.run()
    elif running == 'client':
        import client.client as client
        client.run()