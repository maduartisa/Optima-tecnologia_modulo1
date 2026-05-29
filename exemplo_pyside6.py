"""
Exemplo didático: Aplicação PySide6 simples
Demonstra componentes básicos: janela, botão, entrada de texto e label
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel
)
from PySide6.QtCore import Qt

class MeuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # Configurar janela
        self.setWindowTitle("App Didática - PySide6")
        self.setGeometry(100, 100, 400, 200)
        
        # Widget central e layout
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QVBoxLayout()
        
        # Label informativo
        label_titulo = QLabel("Digite seu nome:")
        label_titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(label_titulo)
        
        # Entrada de texto
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Seu nome aqui...")
        layout.addWidget(self.input_nome)
        
        # Botão e label de resultado
        botao = QPushButton("Enviar")
        botao.clicked.connect(self.ao_clicar)
        layout.addWidget(botao)
        
        self.label_resultado = QLabel("")
        self.label_resultado.setStyleSheet("color: blue; font-size: 12px;")
        layout.addWidget(self.label_resultado)
        
        # Aplicar layout
        widget_central.setLayout(layout)
    
    def ao_clicar(self):
        nome = self.input_nome.text()
        if nome:
            self.label_resultado.setText(f"Olá, {nome}! 👋")
            self.input_nome.clear()
        else:
            self.label_resultado.setText("Por favor, digite um nome!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MeuApp()
    janela.show()
    sys.exit(app.exec())
