class KoalascriptError(Exception):
    pass


OPERATORS = {
    "+", "-", "*", "/", "==", "!=", ">=", "<="
}

PRECEDENCE = {
    "*": 2,
    "/": 2,
    "+": 1,
    "-": 1,
    "==": 0,
    "!=": 0,
    ">=": 0,
    "<=": 0,
}


def tokenize(expr):
    tokens = []
    i = 0

    while i < len(expr):

        if expr[i].isspace():
            i += 1
            continue

        # Strings
        if expr[i] == '"':
            j = i + 1
            while j < len(expr):
                if expr[j] == '"' and expr[j - 1] != "\\":
                    break
                j += 1

            if j >= len(expr):
                raise KoalascriptError("Unterminated string")

            tokens.append(expr[i:j + 1])
            i = j + 1
            continue

        # Two-character operators
        if i + 1 < len(expr):
            op = expr[i:i + 2]
            if op in ("==", "!=", ">=", "<="):
                tokens.append(op)
                i += 2
                continue

        # One-character operators
        if expr[i] in "+-*/":
            tokens.append(expr[i])
            i += 1
            continue

        # Integer
        if expr[i].isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue

        # Identifier
        if expr[i].isalpha() or expr[i] == "_":
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue

        raise KoalascriptError(f"Unexpected character '{expr[i]}'")

    return tokens


def evaluate(expr):
    tokens = tokenize(expr)

    values = []
    ops = []

    def apply():
        if len(values) < 2:
            raise KoalascriptError("Invalid expression")

        b = values.pop()
        a = values.pop()
        op = ops.pop()

        if op == "+":
            if not (isinstance(a, int) and isinstance(b, int)):
                raise KoalascriptError("'+' only works on numbers")
            values.append(a + b)

        elif op == "-":
            if not (isinstance(a, int) and isinstance(b, int)):
                raise KoalascriptError("'-' only works on numbers")
            values.append(a - b)

        elif op == "*":
            if not (isinstance(a, int) and isinstance(b, int)):
                raise KoalascriptError("'*' only works on numbers")
            values.append(a * b)

        elif op == "/":
            if not (isinstance(a, int) and isinstance(b, int)):
                raise KoalascriptError("'/' only works on numbers")
            if b == 0:
                raise KoalascriptError("Division by zero")
            values.append(a // b)

        elif op == "==":
            values.append(a == b)

        elif op == "!=":
            values.append(a != b)

        elif op == ">=":
            if not (isinstance(a, int) and isinstance(b, int)):
                raise KoalascriptError("'>=' only works on numbers")
            values.append(a >= b)

        elif op == "<=":
            if not (isinstance(a, int) and isinstance(b, int)):
                raise KoalascriptError("'<=' only works on numbers")
            values.append(a <= b)

    for token in tokens:

        if token in PRECEDENCE:
            while ops and PRECEDENCE[ops[-1]] >= PRECEDENCE[token]:
                apply()
            ops.append(token)

        else:
            if token.startswith('"') and token.endswith('"'):
                values.append(token[1:-1])

            elif token.isdigit():
                values.append(int(token))

            elif token == "true":
                values.append(True)

            elif token == "false":
                values.append(False)

            else:
                raise KoalascriptError(f"Unexpected token '{token}'")

    while ops:
        apply()

    if len(values) != 1:
        raise KoalascriptError("Invalid expression")

    return values[0]
