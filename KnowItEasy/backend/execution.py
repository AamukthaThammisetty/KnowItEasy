import ast
import copy
import time


class ExecutionContext:
    def __init__(self):
        self.variables = {}
        self.steps = []
        self.step_id = 0
        self.depth = 0

    def snapshot(self):
        return copy.deepcopy(self.variables)

    def log(self, step_type, data):
        self.steps.append({
            "id": self.step_id,
            "type": step_type,
            "depth": self.depth,
            "time": time.time(),
            "data": data
        })
        self.step_id += 1


class Evaluator:
    def __init__(self, ctx):
        self.ctx = ctx

    def eval(self, node):

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            return self.ctx.variables.get(node.id, 0)

        if isinstance(node, ast.BinOp):
            l = self.eval(node.left)
            r = self.eval(node.right)

            if isinstance(node.op, ast.Add): return l + r
            if isinstance(node.op, ast.Sub): return l - r
            if isinstance(node.op, ast.Mult): return l * r
            if isinstance(node.op, ast.Div): return l / r
            if isinstance(node.op, ast.Mod): return l % r
            if isinstance(node.op, ast.Pow): return l ** r

        if isinstance(node, ast.Compare):
            l = self.eval(node.left)
            r = self.eval(node.comparators[0])

            op = node.ops[0]
            if isinstance(op, ast.Eq): return l == r
            if isinstance(op, ast.NotEq): return l != r
            if isinstance(op, ast.Lt): return l < r
            if isinstance(op, ast.Gt): return l > r
            if isinstance(op, ast.LtE): return l <= r
            if isinstance(op, ast.GtE): return l >= r

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "range":
                    args = [self.eval(a) for a in node.args]
                    return list(range(*args))
                if node.func.id == "int":
                    return int(self.eval(node.args[0]))

        return 0


class Executor(ast.NodeVisitor):
    def __init__(self, ctx):
        self.ctx = ctx
        self.eval = Evaluator(ctx).eval

    def visit_Assign(self, node):
        var = node.targets[0].id
        value = self.eval(node.value)

        self.ctx.variables[var] = value

        self.ctx.log("assign", {
            "var": var,
            "value": value,
            "snapshot": self.ctx.snapshot()
        })

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.handle_call(node.value)

    def handle_call(self, node):
        if node.func.id == "print":
            val = self.eval(node.args[0])

            self.ctx.log("print", {
                "value": val,
                "snapshot": self.ctx.snapshot()
            })

    def visit_If(self, node):
        cond = self.eval(node.test)

        self.ctx.log("if_start", {
            "condition": ast.unparse(node.test),
            "result": cond,
            "snapshot": self.ctx.snapshot()
        })

        self.ctx.depth += 1

        if cond:
            self.ctx.log("if_true", {"snapshot": self.ctx.snapshot()})
            for stmt in node.body:
                self.visit(stmt)
        else:
            self.ctx.log("if_false", {"snapshot": self.ctx.snapshot()})
            for stmt in node.orelse:
                self.visit(stmt)

        self.ctx.depth -= 1

        self.ctx.log("if_end", {"snapshot": self.ctx.snapshot()})

    def visit_For(self, node):
        iterable = self.eval(node.iter)
        var = node.target.id

        self.ctx.log("loop_start", {
            "var": var,
            "range": str(iterable)
        })

        self.ctx.depth += 1

        for val in iterable:
            self.ctx.variables[var] = val

            self.ctx.log("loop_iter", {
                "var": var,
                "value": val,
                "snapshot": self.ctx.snapshot()
            })

            for stmt in node.body:
                self.visit(stmt)

        self.ctx.depth -= 1

        self.ctx.log("loop_end", {"snapshot": self.ctx.snapshot()})


def execute_code(code: str):
    tree = ast.parse(code)

    ctx = ExecutionContext()
    executor = Executor(ctx)

    for stmt in tree.body:
        executor.visit(stmt)

    return {
        "steps": ctx.steps,
        "final": ctx.variables
    }
