# -*- coding: utf-8 -*-

"""A command-line DRY Python package builder

This package contains the source code to support the ``pyron`` Python
command-line tool for building and installing packages.

"""

import _ast, sys
# import shutil

def die(message):
    sys.stderr.write('pyron: ' + message + '\n')
    sys.exit(1)

class ASTNotSimpleConstant(Exception):
    pass

def interpret(node):
    if isinstance(node, _ast.Str):
        return node.s
    elif isinstance(node, _ast.Num):
        return node.n
    elif isinstance(node, _ast.Tuple):
        return tuple( interpret(e) for e in node.elts )
    elif isinstance(node, _ast.List):
        return list( interpret(e) for e in node.elts )
    else:
        raise ASTNotSimpleConstant()

def parse_project_init(init_path):
    """Parse a package-wide __init__.py module for information."""
    f = open(init_path)
    code = f.read()
    f.close()

    a = compile(code, init_path, 'exec', _ast.PyCF_ONLY_AST)

    global_constants = {}

    for a2 in a.body:
        if isinstance(a2, _ast.Assign):
            try:
                rhs = interpret(a2.value)
            except ASTNotSimpleConstant:
                continue

            lhs = a2.targets[0] # why is `a2.targets` a list?

            if isinstance(lhs, _ast.Name):
                targets = [ lhs ]
                values = [ rhs ]
            else: # `targets` must be tuple or list lhs
                targets = lhs.elts
                values = rhs

            for target, value in zip(targets, values):
                global_constants[target.id] = value

    for name in '__version__', '__author__': # '__testrunner__'
        if name not in global_constants:
            die('your module does not define %r at the top level' % name)

    return global_constants
