# Top names functions

Script search and display functions names in python files in the specified directories.

Script get folder in which you want to remove duplicates and display all duplicate files with file path.

# Using

Run the script note the directories path
```#!bash
$ python top_functions_names.py -d/--dir <path to files> <path to files>

optional arguments:
  -h, --help            show this help message and exit
  -d --dirs DIR_PATH DIR_PATH DIR_PATH            set directories (directory)
  -top_size TOP_SIZE    set top size for functions names (integer)

```
and get functions_names like this:
```#!bash
Found total 39 functions names, 32 unique :

load_data 4
set_cli_argument_parse 4
build 2
main 2
get_repositories_base_info_list 2
output_repositories 2
```

# Requirement

Python >=3.5

# Project Goals

The code is written for educational purposes. Training course for OTUS.RU
