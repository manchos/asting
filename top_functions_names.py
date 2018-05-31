import ast
import os
import collections
import argparse
from nltk import pos_tag
import logging
import git

logging.basicConfig(level=logging.ERROR)



def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def load_file_content(filename):
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        return attempt_handler.read()


def get_files(_path, endswith='.py', max=100, exclude_dirs=['.git']):
    file_list = []
    dirs_tree = os.walk(_path, topdown=True)
    for dirname, dirs, files in dirs_tree:
        # [dirs.remove(d) for d in dirs if d in set(exclude_dirs)]
        # if len(dirs) == 1 and (dirs[0] in dirname):
        if [ _dir for _dir in exclude_dirs if _dir in dirname]:
            continue
        for file in files:
            if file.endswith(endswith) and len(file_list) < max:
                file_list.append(os.path.join(dirname, file))
    return file_list


def get_tree(content):
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(e)
        tree = None
    return tree


def get_tree_list(path, with_filenames=False, with_file_content=False):
    tree_list = []
    filenames = get_files(path)
    logging.info('total {} files in path {}'.format(len(filenames), path))
    for filename in filenames:
        main_file_content = load_file_content(filename)
        tree = get_tree(main_file_content)
        if with_filenames:
            if with_file_content:
                tree_list.append((filename, main_file_content, tree))
            else:
                tree_list.append((filename, tree))
        else:
            tree_list.append(tree)
    return tree_list


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_node_name_list(node_name):
    return [node.name.lower() for node in ast.walk(node_name) if isinstance(node, ast.FunctionDef)]


def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


def get_all_words_in_path(path):
    tree_list = [tree for tree in get_tree_list(path) if tree]
    name_list = [get_all_names(tree) for tree in tree_list]
    function_names_list = [f for f in flat(name_list) if not (f.startswith('__') and f.endswith('__'))]

    def split_snake_case_name_to_words(name):
        return [word for word in name.split('_') if word]

    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names_list])


def get_top_functions_names_in_path(path, top_size=20):
    tree_list = get_tree_list(path)
    trees_node_name_list = [get_node_name_list(node_name) for node_name in tree_list]

    functions_names_list = [func for func in flat(trees_node_name_list)
                            if not (func.startswith('__') and func.endswith('__'))]
    return collections.Counter(functions_names_list).most_common(top_size)


def get_top_functions_name_dict_from_pathes(path_list):
    top_functions_names = collections.Counter()
    for path in path_list:
        top_functions_names += collections.Counter(dict(get_top_functions_names_in_path(path)))
    return dict(top_functions_names)



def directory(raw_path):
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)


def clone_git_repo(
        repo_url='https://github.com/manchos/test-framework.git',
        clone_dir='./tmp'):
    rez = git.Git(clone_dir).clone(repo_url)
    print(rez)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get top functions names in files")
    parser.add_argument("-d", "--dirs", nargs='+', type=directory, dest="dirs", required=True, help='set directories')
    parser.add_argument("-top_size", "--top_size", type=int, dest="top_size", required=False, default=200,
                        help='set top size for functions names')
    args = parser.parse_args()


#     projects = [
#         './django',
#         './flask',
#         './pyramid',
#         './reddit',
#         './requests',
#         './sqlalchemy',
#     ]

    top_functions_names = get_top_functions_name_dict_from_pathes(args.dirs)

    clone_git_repo()

    print('\n Found total {} functions names, {} unique \n'.format(
        len(top_functions_names),
        len([name for name, repeat in dict(top_functions_names).items() if repeat == 1]))
    )

    for word, occurence in collections.Counter(top_functions_names).most_common(args.top_size):
        print(word, occurence)
