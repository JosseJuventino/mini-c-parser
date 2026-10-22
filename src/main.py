from lexer import tokenizar

codigo = "int edad = 20;"

tokens = tokenizar(codigo)

for token in tokens:
    print(token)