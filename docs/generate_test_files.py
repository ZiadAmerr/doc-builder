import os
import re
import shutil

path_to_generate_in = os.path.abspath(__file__ + "/../at_test")


def t_get_functions_and_classes(module_path):
    # This function finds all classes and functions
    # in a module using 'class' and 'def' keywords
    with open(module_path, errors="replace") as file:
        module_str = file.read()
    all_function_names = [
        item.split("(")[0]
        for item in module_str.split("\ndef ")[1:]
    ]
    public_function_names = [
        n for n in all_function_names if n.split(".")[-1][0] != "_"
    ]
    class_names = re.findall("class .*:", module_str)
    class_names = list(map(lambda x: x[6:min(x.find("("), x.rfind(":"))], class_names))
    return sorted(public_function_names), sorted(class_names)


def t_create_module(root_dir, module_name, dotted_namespace, funcs, classes):
    global path_to_generate_in
    write_to_file = "{}\n{}\n".format(module_name.capitalize(), "=" * len(module_name))
    write_to_file += "\n.. automodule:: {}\n\t:members:\n\t:special-members: " \
                     "__init__\n\t:undoc-members:\n\t:show-inheritance:\n".format(
        dotted_namespace + "." + module_name)
    current_dir = os.path.abspath(path_to_generate_in + f"/{root_dir}")
    module_dir = current_dir + f"/{module_name}"
    os.mkdir(module_dir)
    toc_tree = f"\n.. toctree::\n\t:hidden:\n\t:maxdepth: -1\n\t:caption:" \
               f" {module_name}\n"
    for func in funcs:
        fn_file = "{}\n{}\n".format(func, "=" * len(func))
        fn_file += f"\n.. autofunction:: {dotted_namespace}.{module_name}.{func}"
        toc_tree += f"\n\t{module_name}/{func}.rst"
        with open(module_dir + f"/{func}.rst", mode="w") as f:
            f.write(fn_file)
    for cls_name in classes:
        cls_file = "{}\n{}\n".format(cls_name, "=" * len(cls_name))
        cls_file += f"\n.. autoclass:: {dotted_namespace}.{module_name}.{cls_name}" \
                    "\n\t:members:" \
                    "\n\t:special-members: __init__" \
                    "\n\t:undoc-members:\n\t:show-inheritance:"
        with open(module_dir + f"/{cls_name}.rst", mode="w") as f:
            f.write(cls_file)
        toc_tree += f"\n\t{module_name}/{cls_name}.rst"
    with open(current_dir + f"/{module_name}.rst", mode="w") as file:
        file.write(write_to_file)
        file.write(toc_tree)


def t_create_dir(path, dirname: str, dotted_namespace):
    global path_to_generate_in
    write_to_file = "{}\n{}\n".format(dirname.capitalize(), "=" * len(dirname))
    write_to_file += "\n.. automodule:: {}\n\t:members:\n\t:special-members: " \
                    "__init__\n\t:undoc-members:\n\t:show-inheritance:\n".format(
        dotted_namespace + "." + dirname)

    abs_path = os.path.abspath(path_to_generate_in + path)
    os.mkdir(os.path.abspath(path_to_generate_in + path))
    with open(abs_path + ".rst", mode="w") as file:
        file.write(write_to_file)


def generate_test_rst():
    real_path = os.path.abspath(__file__ + "../../../") + "/ivy_tests/test_ivy/helpers"
    for root, dirs, files in os.walk(real_path):
        if root.endswith("__pycache__"):
            continue
        dotted_namespace = root[root.find("ivy"):].replace("/", ".")
        for name in dirs:
            if name == "__pycache__":
                continue
            t_create_dir(os.path.join(root, name)[len(real_path):], name, dotted_namespace)
        for file in files:
            if file == "__init__.py":
                continue
            funcs, classes = t_get_functions_and_classes(os.path.join(root, file))
            r_path = os.path.join(root)[len(real_path):]
            t_create_module(r_path, file[:-3], dotted_namespace, funcs, classes)


shutil.rmtree(path_to_generate_in, ignore_errors=True)
os.makedirs(path_to_generate_in)
generate_test_rst()
