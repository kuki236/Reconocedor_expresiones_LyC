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
        self.master.geometry("1000x600")
        self.master.configure(bg="#F4F6F8")
        
        self.crear_widgets()
        self.log_consola("Sistema iniciado correctamente.", "success")
        self.log_consola("Cargando lexer y parser AST...", "info")

    def crear_widgets(self):
        panel_izq = tk.Frame(self.master, bg="#FFFFFF", width=300, padx=20, pady=20)
        panel_izq.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(panel_izq, text="Entrada", font=("Arial", 18, "bold"), bg="#FFFFFF", anchor="w").pack(fill=tk.X)
        tk.Label(panel_izq, text="Define la expresión aritmética para analizar sus componentes.", bg="#FFFFFF", fg="#666666", wraplength=250, justify="left").pack(fill=tk.X, pady=(5, 20))

        tk.Label(panel_izq, text="Expresión Aritmética", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w")
        
        self.entrada_var = tk.StringVar()
        self.entry_expresion = ttk.Entry(panel_izq, textvariable=self.entrada_var, font=("Consolas", 12))
        self.entry_expresion.pack(fill=tk.X, pady=(5, 15), ipady=5)

        # Botones
        frame_btns = tk.Frame(panel_izq, bg="#FFFFFF")
        frame_btns.pack(fill=tk.X)
        
        btn_analizar = tk.Button(frame_btns, text="▶ Analizar", bg="#009688", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.ejecutar_analisis)
        btn_analizar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5), ipady=5)
        
        btn_limpiar = tk.Button(frame_btns, text="↺ Limpiar", bg="#E0E0E0", fg="black", font=("Arial", 10), relief="flat", command=self.limpiar_todo)
        btn_limpiar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0), ipady=5)

        # Consola
        tk.Label(panel_izq, text="CONSOLA DEL SISTEMA", font=("Arial", 8, "bold"), bg="#FFFFFF", fg="#888888").pack(anchor="w", pady=(20, 5))
        self.consola = tk.Text(panel_izq, height=15, bg="#1E293B", fg="#A6ACCD", font=("Consolas", 9), relief="flat")
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
        self.tree_tokens = ttk.Treeview(self.tab_tokens, columns=columnas, show="headings")
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

        self.tab_resultado = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_resultado, text=" ∑ Resultado ")
        
        tk.Label(self.tab_resultado, text="Resultado de la Operación:", font=("Arial", 16), bg="#FFFFFF", fg="#555").pack(pady=(50, 10))
        self.lbl_resultado = tk.Label(self.tab_resultado, text="---", font=("Consolas", 48, "bold"), bg="#FFFFFF", fg="#009688")
        self.lbl_resultado.pack()

    def log_consola(self, mensaje, tag="info"):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.consola.insert(tk.END, f"[{hora}] {mensaje}\n", tag)
        self.consola.see(tk.END)

    def dibujar_nodo(self, nodo, parent_id=""):
        if nodo['tipo'] == 'Numero':
            self.tree_ast.insert(parent_id, "end", text=f"Número: {nodo['valor']}")
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
            tokens = obtener_tokens(expresion)
            self.log_consola(f"Scanner: {len(tokens)} tokens generados.", "success")
            for t in tokens:
                self.tree_tokens.insert("", tk.END, values=(t["id"], t["tipo"], t["lexema"], t["posicion"]))

            parser = Parser(tokens)
            arbol = parser.parsear()
            self.log_consola("Parser: AST construido correctamente.", "success")
            
            self.dibujar_nodo(arbol)

            resultado = evaluar_arbol(arbol)
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

    def limpiar_datos(self):
        for item in self.tree_tokens.get_children():
            self.tree_tokens.delete(item)
        for item in self.tree_ast.get_children():
            self.tree_ast.delete(item)
        self.lbl_resultado.config(text="---", fg="#009688")

    def limpiar_todo(self):
        self.entrada_var.set("")
        self.limpiar_datos()
        self.consola.delete(1.0, tk.END)
        self.log_consola("Entorno limpiado.", "info")