# Todo

Small todo list program written in python 3 using the curses library
## Install

```sh
curl https://raw.githubusercontent.com/SanderGodard/todo/refs/heads/main/install.sh | bash
```

## Details

Written in python, uses json to store and work with the data

### Locations

storage filename `storage.json`

storage in `~/.todo/`
OR
in cwd


### Funcitonality
|Your File/Directory|Standard Role      |Function in your app                                                                                            |Maintenance Benefits                                                                     |
|-------------------|-------------------|----------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
|lib/Entry.py       |Model (Data)       |Defines what a single task is (text, flair, time).                                                              |If you change how an entry is stored (e.g., adding a due date), you only touch this file.|
|lib/EntryList.py   |Model (Data)       |Defines the container for tasks and list-level logic (name, collection of Entry objects).                       |Isolates list management features (rename, add entry) from the app's UI.                 |
|lib/DataStore.py   |Model (Persistence)|Handles all loading/saving (I/O) with storage.json.                                                             |If you switch from JSON to a database, you only touch this file.                         |
|lib/Rendering.py   |View (UI)          |Handles the low-level drawing of items to the ncurses window.                                                   |If you change the UI look (symbols, colors, layout), you only touch this file.           |
|lib/App.py         |Controller         |Manages application state (cursor_y, currentScreen), interprets user input, and tells the View/Model what to do.|This is the "brain" that coordinates everything without handling I/O or drawing itself.  |
|lib/Constants.py   |Utility            |Holds keybindings, flair definitions, and color IDs.                                                            |Provides a single source of truth for configuration.                                     |
|Todo.py            |Bootstrap/Runner   |The entry point that sets up the curses environment and starts the main loop.                                   |Keeps setup logic clean and separate.                                                    |


### Make symlink

`$ cd todo; sudo ln -s $(pwd)/todo.py /usr/bin/todo`

## NOTICE

Found in dotfiles under terminalapps

Use `todo.py` for current working, `Todo.py` is under development.