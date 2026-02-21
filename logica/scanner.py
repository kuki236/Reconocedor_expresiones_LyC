def obtener_tokens(expresion):
    tokens_generados = []
    pos = 0
    longitud = len(expresion)
    id_contador = 1

    while pos < longitud:
        char_actual = expresion[pos]

        if char_actual in ' \t\n':
            pos += 1
            continue

        elif '0' <= char_actual <= '9':
            numero = ""
            columna_inicio = pos + 1
            
            while pos < longitud and '0' <= expresion[pos] <= '9':
                numero += expresion[pos]
                pos += 1
                
            if pos < longitud and expresion[pos] == '.':
                numero += '.'
                pos += 1
                while pos < longitud and '0' <= expresion[pos] <= '9':
                    numero += expresion[pos]
                    pos += 1

            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": "NUMBER",
                "lexema": numero,
                "posicion": f"Col {columna_inicio}"
            })
            id_contador += 1

        elif char_actual in "+-":
            # Detectar si es operador unario o binario
            es_unario = False
            if not tokens_generados:
                es_unario = True
            else:
                ultimo_token = tokens_generados[-1]
                if ultimo_token['tipo'] in ('OPERATOR', 'UNARY_OP', 'L_PAREN', 'POW_OP', 'MOD_OP'):
                    es_unario = True
            
            tipo = "UNARY_OP" if es_unario else "OPERATOR"
            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": tipo,
                "lexema": char_actual,
                "posicion": f"Col {pos + 1}"
            })
            id_contador += 1
            pos += 1

        elif char_actual in "*/":
            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": "OPERATOR",
                "lexema": char_actual,
                "posicion": f"Col {pos + 1}"
            })
            id_contador += 1
            pos += 1

        elif char_actual == "^":
            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": "POW_OP",
                "lexema": char_actual,
                "posicion": f"Col {pos + 1}"
            })
            id_contador += 1
            pos += 1

        elif char_actual == "%":
            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": "MOD_OP",
                "lexema": char_actual,
                "posicion": f"Col {pos + 1}"
            })
            id_contador += 1
            pos += 1

        elif char_actual == "(":
            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": "L_PAREN",
                "lexema": char_actual,
                "posicion": f"Col {pos + 1}"
            })
            id_contador += 1
            pos += 1

        elif char_actual == ")":
            tokens_generados.append({
                "id": f"{id_contador:02d}",
                "tipo": "R_PAREN",
                "lexema": char_actual,
                "posicion": f"Col {pos + 1}"
            })
            id_contador += 1
            pos += 1

        else:
            raise RuntimeError(f"Carácter no válido '{char_actual}' en la columna {pos + 1}")

    return tokens_generados