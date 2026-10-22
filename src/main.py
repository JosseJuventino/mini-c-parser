from lexer import tokenizar
codigo = "int edad = 20; edad = edad + 5;"
tokens = tokenizar(codigo)

for token in tokens:
    print(token)