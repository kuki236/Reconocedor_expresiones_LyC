import tkinter as tk
from pantallas.interfaz import AnalizadorApp

def main():
    root = tk.Tk()
    style = tk.ttk.Style(root)
    style.theme_use('clam') 
    
    app = AnalizadorApp(master=root)
    root.mainloop()

if __name__ == "__main__":
    main()