class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos_actual = 0
        self.token_actual = self.tokens[self.pos_actual] if self.tokens else None
        self.pasos_evaluacion = []

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

    def E(self):
        nodo_izq = self.T()
        return self.E_prima(nodo_izq)

    def E_prima(self, nodo_izq):
        if self.token_actual and self.token_actual['lexema'] in ('+', '-') and self.token_actual['tipo'] == 'OPERATOR':
            operador = self.token_actual['lexema']
            self.coincidir('OPERATOR')
            nodo_der = self.T()
            nuevo_nodo = {'tipo': 'Operacion', 'valor': operador, 'izq': nodo_izq, 'der': nodo_der}
            return self.E_prima(nuevo_nodo)
        return nodo_izq

    def T(self):
        nodo_izq = self.P()
        return self.T_prima(nodo_izq)

    def T_prima(self, nodo_izq):
        if self.token_actual and self.token_actual['lexema'] in ('*', '/', '%'):
            operador = self.token_actual['lexema']
            if operador == '*':
                self.coincidir('OPERATOR')
            elif operador == '/':
                self.coincidir('OPERATOR')
            elif operador == '%':
                self.coincidir('MOD_OP')
            nodo_der = self.P()
            nuevo_nodo = {'tipo': 'Operacion', 'valor': operador, 'izq': nodo_izq, 'der': nodo_der}
            return self.T_prima(nuevo_nodo)
        return nodo_izq

    def P(self):
        nodo_izq = self.U()
        if self.token_actual and self.token_actual['tipo'] == 'POW_OP':
            self.coincidir('POW_OP')
            nodo_der = self.P()  # Recursión derecha para asociatividad derecha
            return {'tipo': 'Operacion', 'valor': '^', 'izq': nodo_izq, 'der': nodo_der}
        return nodo_izq

    def U(self):
        if self.token_actual and self.token_actual['tipo'] == 'UNARY_OP':
            operador = self.token_actual['lexema']
            self.coincidir('UNARY_OP')
            nodo = self.U()
            return {'tipo': 'Unario', 'valor': operador, 'operando': nodo}
        return self.F()

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


def evaluar_arbol(nodo, pasos=None):
    if pasos is None:
        pasos = []
    
    if nodo['tipo'] == 'Numero':
        pasos.append(f"Número: {nodo['valor']}")
        return nodo['valor'], pasos
    
    if nodo['tipo'] == 'Unario':
        operando, pasos = evaluar_arbol(nodo['operando'], pasos)
        if nodo['valor'] == '-':
            resultado = -operando
        else:  # '+'
            resultado = operando
        pasos.append(f"Unario {nodo['valor']}: {nodo['valor']}{operando} = {resultado}")
        return resultado, pasos
    
    izq, pasos = evaluar_arbol(nodo['izq'], pasos)
    der, pasos = evaluar_arbol(nodo['der'], pasos)
    
    if nodo['valor'] == '+':
        resultado = izq + der
        operacion = f"Suma"
    elif nodo['valor'] == '-':
        resultado = izq - der
        operacion = f"Resta"
    elif nodo['valor'] == '*':
        resultado = izq * der
        operacion = f"Multiplicación"
    elif nodo['valor'] == '/':
        if der == 0:
            raise ZeroDivisionError("No se puede dividir por cero.")
        resultado = izq / der
        operacion = f"División"
    elif nodo['valor'] == '^':
        resultado = izq ** der
        operacion = f"Potencia"
    elif nodo['valor'] == '%':
        if der == 0:
            raise ZeroDivisionError("No se puede aplicar módulo con cero.")
        resultado = izq % der
        operacion = f"Módulo"
    
    pasos.append(f"{operacion}: {izq} {nodo['valor']} {der} = {resultado}")
    return resultado, pasos