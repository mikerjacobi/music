ps aux | grep server.py | awk '{print $2}' | xargs kill -9
