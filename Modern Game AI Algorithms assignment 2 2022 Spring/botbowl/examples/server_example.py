#!/usr/bin/env python3
from scripted_bot_example import *

import botbowl.web.server as server
from mcts_demo1 import SearchBot

if __name__ == "__main__":
    botbowl.register_bot("demo1_bot", SearchBot)
    server.start_server(debug=True, use_reloader=False, port=1234)
