#!/usr/bin/bash

# curl https://raw.githubusercontent.com/SanderGodard/todo/refs/heads/main/install.sh | bash



git clone https://github.com/SanderGodard/todo.git
cd todo
sudo ln -s $(pwd)/todo.py /usr/bin/todo