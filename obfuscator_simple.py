import ast

def add_types_to_variable_names(filename):
    with open(filename, "r") as file:
        source_code = file.read()

    tree = ast.parse(source_code, filename=filename)

    class VariableTypeAppender(ast.NodeTransformer):
        def __init__(self):
            self.counter = 1
            self.variables = {}

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if not target.id in self.variables:
                        self.variables[target.id] = f"venom{self.counter}"
                        target.id = f"venom{self.counter}"
                        self.counter+=1
                    else:
                        target.id = self.variables[target.id]
            return node

    transformer = VariableTypeAppender()
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    modified_code = ast.unparse(modified_tree)

    with open(filename.replace('.', '_venom.'), "w") as file:
        file.write(modified_code)

filename = "test.py"
add_types_to_variable_names(filename)
print(f"Venomization complete. Code saved in {filename.replace('.', '_venom.')}.")
