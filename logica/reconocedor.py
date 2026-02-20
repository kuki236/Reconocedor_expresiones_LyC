class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos_actual = 0
        self.token_actual = self.tokens[self.pos_actual] if self.tokens else None

    def avanzar(self):
        self.pos_actual += 1
        if self.pos_actual < len(self.tokens):
            self.token_actual = self.tokens[self.pos_actual]
        else:
            self.token_actual = None

    def coincidir(self, tipo_esperado):
        if self.token_actual and self.token_actual['tipo'] == tipo_esperado:
            token = self.token_actual
            self.avanzar()
            return token
        else:
            encontrado = self.token_actual['lexema'] if self.token_actual else "Fin de línea"
            raise SyntaxError(f"Se esperaba '{tipo_esperado}', pero se encontró '{encontrado}'")

    def parsear(self):
        if not self.tokens:
            raise SyntaxError("La expresión está vacía.")
        
        arbol_sintactico = self.E()
        
        if self.token_actual is not None:
            raise SyntaxError(f"Token inesperado al final de la expresión: {self.token_actual['lexema']}")
        
        return arbol_sintactico

    # Regla 1: E -> T E'
    def E(self):
        nodo_izq = self.T()
        return self.E_prima(nodo_izq)

    # Regla 2: E' -> + T E' | - T E' | lambda
    def E_prima(self, nodo_izq):
        if self.token_actual and self.token_actual['lexema'] in ('+', '-'):
            operador = self.token_actual['lexema']
            self.coincidir('OPERATOR')
            nodo_der = self.T()
            nuevo_nodo = {'tipo': 'Operacion', 'valor': operador, 'izq': nodo_izq, 'der': nodo_der}
            return self.E_prima(nuevo_nodo)
        return nodo_izq # lambda

    # Regla 3: T -> F T'
    def T(self):
        nodo_izq = self.F()
        return self.T_prima(nodo_izq)

    # Regla 4: T' -> * F T' | / F T' | lambda
    def T_prima(self, nodo_izq):
        if self.token_actual and self.token_actual['lexema'] in ('*', '/'):
            operador = self.token_actual['lexema']
            self.coincidir('OPERATOR')
            nodo_der = self.F()
            nuevo_nodo = {'tipo': 'Operacion', 'valor': operador, 'izq': nodo_izq, 'der': nodo_der}
            return self.T_prima(nuevo_nodo)
        return nodo_izq # lambda

    # Regla 5: F -> ( E ) | num
    def F(self):
        if self.token_actual and self.token_actual['tipo'] == 'NUMBER':
            token = self.coincidir('NUMBER')
            valor = float(token['lexema']) if '.' in token['lexema'] else int(token['lexema'])
            return {'tipo': 'Numero', 'valor': valor}
            
        elif self.token_actual and self.token_actual['tipo'] == 'L_PAREN':
            self.coincidir('L_PAREN')
            nodo = self.E()
            self.coincidir('R_PAREN')
            return nodo
        else:
            encontrado = self.token_actual['lexema'] if self.token_actual else "Fin"
            raise SyntaxError(f"Se esperaba un Número o '(', se encontró '{encontrado}'")


def evaluar_arbol(nodo):
    if nodo['tipo'] == 'Numero':
        return nodo['valor']
    
    izq = evaluar_arbol(nodo['izq'])
    der = evaluar_arbol(nodo['der'])
    
    if nodo['valor'] == '+': return izq + der
    if nodo['valor'] == '-': return izq - der
    if nodo['valor'] == '*': return izq * der
    if nodo['valor'] == '/':
        if der == 0:
            raise ZeroDivisionError("No se puede dividir por cero.")
        return izq / der