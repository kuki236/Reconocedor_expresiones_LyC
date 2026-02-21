import tkinter as tk
from tkinter import ttk
import datetime
from logica.scanner import obtener_tokens
from logica.reconocedor import Parser, evaluar_arbol

class AnalizadorApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Analizador Aritmético Visual")
        self.master.geometry("1200x700")
        self.master.configure(bg="#F4F6F8")
        
        self.pasos_evaluacion = []
        self.crear_widgets()
        self.log_consola("Sistema iniciado correctamente.", "success")
        self.log_consola("Cargando lexer, parser y evaluador AST...", "info")

    def crear_widgets(self):
        panel_izq = tk.Frame(self.master, bg="#FFFFFF", width=350, padx=20, pady=20)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(panel_izq, text="Entrada", font=("Arial", 18, "bold"), bg="#FFFFFF", anchor="w").pack(fill=tk.X)
        tk.Label(panel_izq, text="Define la expresión aritmética o usa los botones.", bg="#FFFFFF", fg="#666666", wraplength=300, justify="left").pack(fill=tk.X, pady=(5, 20))

        tk.Label(panel_izq, text="Expresión Aritmética", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w")
        
        self.entrada_var = tk.StringVar()
        self.entry_expresion = ttk.Entry(panel_izq, textvariable=self.entrada_var, font=("Consolas", 12))
        self.entry_expresion.pack(fill=tk.X, pady=(5, 15), ipady=5)

        frame_btns = tk.Frame(panel_izq, bg="#FFFFFF")
        frame_btns.pack(fill=tk.X, pady=(0, 10))
        
        btn_analizar = tk.Button(frame_btns, text="▶ Analizar", bg="#009688", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.ejecutar_analisis)
        btn_analizar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5), ipady=5)
        
        btn_limpiar = tk.Button(frame_btns, text="↺ Limpiar", bg="#E0E0E0", fg="black", font=("Arial", 10), relief="flat", command=self.limpiar_todo)
        btn_limpiar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0), ipady=5)

        tk.Label(panel_izq, text="Calculadora", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
        
        calculadora_frame = tk.Frame(panel_izq, bg="#FFFFFF")
        calculadora_frame.pack(fill=tk.X, pady=(0, 15))
        
        botones = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '(', ')'),
            ('+', '^', '%', '←')
        ]
        
        for fila in botones:
            fila_frame = tk.Frame(calculadora_frame, bg="#FFFFFF")
            fila_frame.pack(fill=tk.X, pady=2)
            for btn_text in fila:
                if btn_text == '←':
                    btn = tk.Button(fila_frame, text=btn_text, font=("Arial", 10, "bold"), width=5, 
                                  command=self.borrar_ultimo, bg="#FF7043", fg="white")
                elif btn_text in ('+', '-', '*', '/', '^', '%'):
                    btn = tk.Button(fila_frame, text=btn_text, font=("Arial", 10, "bold"), width=5,
                                  command=lambda x=btn_text: self.agregar_al_campo(x), bg="#FFB74D", fg="white")
                else:
                    btn = tk.Button(fila_frame, text=btn_text, font=("Arial", 10, "bold"), width=5,
                                  command=lambda x=btn_text: self.agregar_al_campo(x), bg="#E3F2FD", fg="black")
                btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1, ipady=3)

        tk.Label(panel_izq, text="CONSOLA DEL SISTEMA", font=("Arial", 8, "bold"), bg="#FFFFFF", fg="#888888").pack(anchor="w", pady=(10, 5))
        self.consola = tk.Text(panel_izq, height=10, bg="#1E293B", fg="#A6ACCD", font=("Consolas", 8), relief="flat")
        self.consola.pack(fill=tk.BOTH, expand=True)
        self.consola.tag_config("error", foreground="#FF5252")
        self.consola.tag_config("success", foreground="#4CAF50")
        self.consola.tag_config("info", foreground="#03A9F4")

        panel_der = tk.Frame(self.master, bg="#F4F6F8", padx=20, pady=20)
        panel_der.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.notebook = ttk.Notebook(panel_der)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.tab_tokens = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_tokens, text=" [ ] Tokens (Lexer) ")

        columnas = ("id", "type", "lexeme", "position")
        self.tree_tokens = ttk.Treeview(self.tab_tokens, columns=columnas, show="headings", height=15)
        self.tree_tokens.heading("id", text="ID")
        self.tree_tokens.heading("type", text="TOKEN TYPE")
        self.tree_tokens.heading("lexeme", text="LEXEME")
        self.tree_tokens.heading("position", text="POSITION")
        self.tree_tokens.column("id", width=50, anchor="center")
        self.tree_tokens.column("type", width=150, anchor="center")
        self.tree_tokens.column("lexeme", width=150, anchor="center")
        self.tree_tokens.column("position", width=100, anchor="center")
        self.tree_tokens.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.tab_arbol = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_arbol, text=" 🌳 Árbol Sintáctico ")
        
        self.tree_ast = ttk.Treeview(self.tab_arbol)
        self.tree_ast.heading("#0", text="Estructura del Árbol (AST)", anchor="w")
        self.tree_ast.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.tab_pasos = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_pasos, text=" 📋 Pasos de Evaluación ")
        
        self.text_pasos = tk.Text(self.tab_pasos, bg="#FFFFFF", fg="#333333", font=("Consolas", 10), relief="flat")
        self.text_pasos.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.text_pasos.tag_config("paso", foreground="#009688", font=("Consolas", 10, "bold"))
        self.text_pasos.tag_config("numero", foreground="#FF7043", font=("Consolas", 10, "bold"))

        self.tab_gramatica = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_gramatica, text=" 📜 Gramática ")
        
        self.text_gramatica = tk.Text(self.tab_gramatica, bg="#FFFFFF", fg="#333333", font=("Consolas", 9), relief="flat", state="disabled")
        self.text_gramatica.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.cargar_gramatica()

        self.tab_resultado = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_resultado, text=" ∑ Resultado ")
        
        tk.Label(self.tab_resultado, text="Resultado de la Operación:", font=("Arial", 16), bg="#FFFFFF", fg="#555").pack(pady=(50, 10))
        self.lbl_resultado = tk.Label(self.tab_resultado, text="---", font=("Consolas", 48, "bold"), bg="#FFFFFF", fg="#009688")
        self.lbl_resultado.pack()

    def cargar_gramatica(self):
        gramatica_texto = """GRAMÁTICA FORMAL (Análisis Sintáctico Descendente Recursivo)

REGLAS DE PRODUCCIÓN:

E  → T E'
E' → + T E' | - T E' | λ
     (Suma y Resta - Asociatividad IZQUIERDA)

T  → P T'
T' → * P T' | / P T' | % P T' | λ
     (Multiplicación, División, Módulo - Asociatividad IZQUIERDA)

P  → U ^ P | U
     (Potencia - Asociatividad DERECHA)

U  → - U | + U | F
     (Operadores Unarios - Asociatividad DERECHA)

F  → ( E ) | número
     (Factor: Números y Expresiones entre paréntesis)


PRECEDENCIA DE OPERADORES (de menor a mayor):

Nivel 1: Suma (+) y Resta (-)              [Asociatividad IZQUIERDA]
Nivel 2: *, / y %                           [Asociatividad IZQUIERDA]
Nivel 3: Potencia (^)                       [Asociatividad DERECHA]
Nivel 4: Unarios (-, +)                     [Asociatividad DERECHA]
Nivel 5: Números y Paréntesis               [Máxima precedencia]


OPERADORES SOPORTADOS:

• + : Suma (binario y unario positivo)
• - : Resta (binario y unario negativo)
• * : Multiplicación
• / : División (con validación de división por cero)
• ^ : Potencia/Exponencial (asociativa derecha)
• % : Módulo (residuo entero)
• ( ) : Paréntesis para agrupar expresiones


EJEMPLOS DE EVALUACIÓN:

✓ 2 + 3 * 4        = 14      [(2) + (3*4) = 2 + 12 = 14]
✓ (2 + 3) * 4      = 20      [(2+3) * 4 = 5 * 4 = 20]
✓ -5 + 3           = -2      [(-5) + 3 = -2]
✓ 2 ^ 3 + 1        = 9       [(2^3) + 1 = 8 + 1 = 9]
✓ 2 ^ 3 ^ 2        = 512     [2 ^ (3^2) = 2 ^ 9 = 512]
✓ 10 % 3           = 1       [residuo de 10÷3]
✓ -(2 + 3)         = -5      [-(5) = -5]
✓ --5              = 5       [-(-5) = 5]
✓ 10 - 5 - 2       = 3       [(10-5)-2 = 5-2 = 3]
✓ 2 * 3 * 4        = 24      [(2*3)*4 = 6*4 = 24]


NOTAS IMPORTANTES:

• El operador ± se reconoce automáticamente como UNARIO o BINARIO
  según el contexto.
• Los paréntesis desbalanceados causarán error de validación.
• La división por cero es detectada y reportada.
• El módulo con cero también es detectado como error.
• Los números pueden ser enteros o decimales (ej: 3.14, -2.5)
"""
        self.text_gramatica.config(state="normal")
        self.text_gramatica.insert(tk.END, gramatica_texto)
        self.text_gramatica.config(state="disabled")

    def agregar_al_campo(self, valor):
        contenido = self.entrada_var.get()
        self.entrada_var.set(contenido + valor)
        self.entry_expresion.focus()

    def borrar_ultimo(self):
        contenido = self.entrada_var.get()
        if contenido:
            self.entrada_var.set(contenido[:-1])

    def log_consola(self, mensaje, tag="info"):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.consola.insert(tk.END, f"[{hora}] {mensaje}\n", tag)
        self.consola.see(tk.END)

    def dibujar_nodo(self, nodo, parent_id=""):
        if nodo['tipo'] == 'Numero':
            self.tree_ast.insert(parent_id, "end", text=f"Número: {nodo['valor']}")
        elif nodo['tipo'] == 'Unario':
            nodo_id = self.tree_ast.insert(parent_id, "end", text=f"Unario: {nodo['valor']}", open=True)
            self.dibujar_nodo(nodo['operando'], nodo_id)
        elif nodo['tipo'] == 'Operacion':
            nodo_id = self.tree_ast.insert(parent_id, "end", text=f"Operador: [ {nodo['valor']} ]", open=True)
            self.dibujar_nodo(nodo['izq'], nodo_id)
            self.dibujar_nodo(nodo['der'], nodo_id)

    def ejecutar_analisis(self):
        expresion = self.entrada_var.get()
        if not expresion.strip():
            self.log_consola("Error: La entrada está vacía.", "error")
            return

        self.limpiar_datos()
        
        try:
            # Validación de paréntesis
            if expresion.count('(') != expresion.count(')'):
                raise SyntaxError("Paréntesis desbalanceados: cantidad de '(' y ')' no coinciden")
            
            tokens = obtener_tokens(expresion)
            self.log_consola(f"Scanner: {len(tokens)} tokens generados.", "success")
            for t in tokens:
                self.tree_tokens.insert("", tk.END, values=(t["id"], t["tipo"], t["lexema"], t["posicion"]))

            parser = Parser(tokens)
            arbol = parser.parsear()
            self.log_consola("Parser: AST construido correctamente.", "success")
            
            self.dibujar_nodo(arbol)

            resultado, pasos = evaluar_arbol(arbol)
            self.pasos_evaluacion = pasos
            self.mostrar_pasos()
            
            self.lbl_resultado.config(text=f"{resultado}")
            self.log_consola(f"Evaluación: Resultado = {resultado}", "success")
            
            self.notebook.select(self.tab_resultado)

        except RuntimeError as e:
            self.log_consola(f"Error Léxico: {str(e)}", "error")
            self.lbl_resultado.config(text="Error Léxico", fg="#FF5252")
        except SyntaxError as e:
            self.log_consola(f"Error Sintáctico: {str(e)}", "error")
            self.lbl_resultado.config(text="Error Sintáctico", fg="#FF5252")
        except ZeroDivisionError as e:
            self.log_consola(f"Error Matemático: {str(e)}", "error")
            self.lbl_resultado.config(text="Div / 0", fg="#FF5252")
        except Exception as e:
            self.log_consola(f"Error: {str(e)}", "error")
            self.lbl_resultado.config(text="Error", fg="#FF5252")

    def mostrar_pasos(self):
        self.text_pasos.config(state="normal")
        self.text_pasos.delete(1.0, tk.END)
        
        self.text_pasos.insert(tk.END, "PASOS DE EVALUACIÓN\n", "paso")
        self.text_pasos.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, paso in enumerate(self.pasos_evaluacion, 1):
            self.text_pasos.insert(tk.END, f"Paso {i}: ", "numero")
            self.text_pasos.insert(tk.END, f"{paso}\n")
        
        self.text_pasos.config(state="disabled")

    def limpiar_datos(self):
        for item in self.tree_tokens.get_children():
            self.tree_tokens.delete(item)
        for item in self.tree_ast.get_children():
            self.tree_ast.delete(item)
        self.lbl_resultado.config(text="---", fg="#009688")
        self.text_pasos.config(state="normal")
        self.text_pasos.delete(1.0, tk.END)
        self.text_pasos.config(state="disabled")

    def limpiar_todo(self):
        self.entrada_var.set("")
        self.limpiar_datos()
        self.consola.delete(1.0, tk.END)
        self.log_consola("Entorno limpiado.", "info")