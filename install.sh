#!/usr/bin/bash

# curl https://raw.githubusercontent.com/SanderGodard/todo/refs/heads/main/install.sh | bash



git clone git@github.com:SanderGodard/todo.git
sleep 1
cd todo
sudo ln -s $(pwd)/todo.py /usr/bin/todo