import ast
import os
import collections

from nltk import pos_tag


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


def get_filenames(_path):
    filenames = []
    for dirname, dirs, files in os.walk(_path, topdown=True):
        for file in files:
            if file.endswith('.py') and len(filenames) < 100:
                filenames.append(os.path.join(dirname, file))
            else:
                break
    return filenames


def get_tree(content):
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(e)
        tree = None
    return tree


def get_tree_list(path, with_filenames=False, with_file_content=False):
    tree_list = []
    filenames = get_filenames(path)
    print('total %s files' % len(filenames))
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
    print('trees generated')
    return tree_list


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


def get_all_words_in_path(path):
    trees = [tree for tree in get_tree_list(path) if tree]
    names = [get_all_names(tree) for tree in trees]
    function_names_list = [f for f in flat(names) if not (f.startswith('__') and f.endswith('__'))]

    def split_snake_case_name_to_words(name):
        return [n for n in name.split('_') if n]

    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names_list])


def get_node_name_list(node_name):
    return [node.name.lower() for node in ast.walk(node_name) if isinstance(node, ast.FunctionDef)]


def get_top_functions_names_in_path(path, top_size=10):
    tree_list = get_tree_list(path)
    trees_node_name_list = [get_node_name_list(node_name) for node_name in tree_list]
    functions_names_list = [func for func in flat(trees_node_name_list)
                            if not (func.startswith('__') and func.endswith('__'))]
    return collections.Counter(functions_names_list).most_common(top_size)


def get_top_verbs_in_path(path, top_size=10):
    global Path
    Path = path
    trees = [t for t in get_trees(None) if t]
    fncs = [f for f in flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if not (f.startswith('__') and f.endswith('__'))]
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)



if __name__ == '__main__':

    wds = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]

    for project in projects:
        path = os.path.join('.', project)
        # wds = get_top_verbs_in_path(path)
        wds.append(get_top_functions_names_in_path(path))


    top_size = 200
    print('total %s words, %s unique' % (len(wds), len(set(wds))))
    for word, occurence in collections.Counter(wds).most_common(top_size):
        print(word, occurence)