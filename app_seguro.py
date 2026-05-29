from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
from datetime import datetime

from cryptography.fernet import Fernet


BASE_DIR = Path(__file__).resolve().parent
AUDITORIA_PATH = BASE_DIR / "auditoria.txt"
CHAVE_PATH = BASE_DIR / "fernet.key"


def registrar_log(mensagem: str) -> None:
    """Registra a ação no arquivo de auditoria local."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with AUDITORIA_PATH.open("a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{timestamp}] {mensagem}\n")


def garantir_chave_fernet() -> Fernet:
    """Cria e reutiliza a chave simétrica local para encriptação."""
    if not CHAVE_PATH.exists():
        CHAVE_PATH.write_bytes(Fernet.generate_key())
    return Fernet(CHAVE_PATH.read_bytes())


class CofreApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cofre de Dados")
        self.root.geometry("980x700")
        self.root.minsize(980, 700)
        self.root.configure(bg="#0f172a")

        self.arquivo_selecionado: Path | None = None
        self.fernet = garantir_chave_fernet()

        self.frame_botoes = tk.Frame(root, bg="#0f172a")
        self.frame_botoes.pack(fill="x", padx=12, pady=(12, 6))

        self.botao_selecionar = tk.Button(
            self.frame_botoes,
            text="Selecionar Arquivo",
            command=self.selecionar_arquivo,
            width=22,
            height=2,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief="flat",
        )
        self.botao_selecionar.pack(side="left", padx=(0, 10))

        self.botao_visualizar = tk.Button(
            self.frame_botoes,
            text="Visualizar Conteúdo",
            command=self.visualizar_conteudo,
            width=22,
            height=2,
            bg="#059669",
            fg="white",
            activebackground="#047857",
            relief="flat",
        )
        self.botao_visualizar.pack(side="left", padx=10)

        self.botao_copiar = tk.Button(
            self.frame_botoes,
            text="Copiar e Criptografar",
            command=self.copiar_e_criptografar,
            width=22,
            height=2,
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            relief="flat",
        )
        self.botao_copiar.pack(side="left", padx=10)

        self.botao_descriptografar = tk.Button(
            self.frame_botoes,
            text="Descriptografar",
            command=self.descriptografar,
            width=22,
            height=2,
            bg="#d97706",
            fg="white",
            activebackground="#b45309",
            relief="flat",
        )
        self.botao_descriptografar.pack(side="left", padx=10)

        self.label_status = tk.Label(
            root,
            text="Nenhum arquivo selecionado.",
            bg="#0f172a",
            fg="#e2e8f0",
            anchor="w",
            padx=12,
            pady=4,
        )
        self.label_status.pack(fill="x")

        self.frame_tabela = tk.Frame(root, bg="#111827")
        self.frame_tabela.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self.tree = ttk.Treeview(self.frame_tabela, show="headings")
        self.tree.pack(fill="both", expand=True)

        self.tree_scroll_y = ttk.Scrollbar(self.frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll_y.set)

        self.tree_scroll_x = ttk.Scrollbar(self.frame_tabela, orient="horizontal", command=self.tree.xview)
        self.tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=self.tree_scroll_x.set)

        registrar_log("Sistema Iniciado")

    def limpar_tabela(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for coluna in self.tree["columns"]:
            self.tree.heading(coluna, text="")
        self.tree["columns"] = ()

    def aplicar_colunas(self, colunas: list[str]) -> None:
        self.tree["columns"] = colunas
        for coluna in colunas:
            self.tree.heading(coluna, text=coluna)
            self.tree.column(coluna, anchor="w", width=200)

    def selecionar_arquivo(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo para auditoria",
            filetypes=[
                ("Arquivos TXT, CSV, XML, JSON", "*.txt *.csv *.xml *.json"),
                ("Todos os Arquivos", "*.*"),
            ],
        )
        if not caminho:
            return

        self.arquivo_selecionado = Path(caminho)
        self.label_status.config(text=f"Arquivo selecionado: {self.arquivo_selecionado.name}")
        self.limpar_tabela()
        messagebox.showinfo("Arquivo Selecionado", f"Arquivo pronto para visualização: {self.arquivo_selecionado.name}")

    def visualizar_conteudo(self) -> None:
        if self.arquivo_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um arquivo antes de visualizar.")
            return

        self.limpar_tabela()
        caminho = self.arquivo_selecionado
        nome = caminho.name
        extensao = caminho.suffix.lower()

        try:
            if extensao == ".csv":
                self._visualizar_csv(caminho)
            elif extensao == ".json":
                self._visualizar_json(caminho)
            elif extensao == ".xml":
                self._visualizar_xml(caminho)
            elif extensao == ".txt":
                self._visualizar_txt(caminho)
            else:
                self._visualizar_generico(caminho)

            registrar_log(f"O arquivo {nome} foi visualizado.")
            self.label_status.config(text=f"Conteúdo visualizado: {nome}")
        except Exception as erro:
            messagebox.showerror("Erro ao visualizar", f"Não foi possível ler o arquivo: {erro}")

    def _visualizar_csv(self, caminho: Path) -> None:
        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.reader(arquivo)
            try:
                cabecalho = next(leitor)
            except StopIteration:
                cabecalho = ["Linha"]
                self.aplicar_colunas(cabecalho)
                return

            colunas = [str(col) for col in cabecalho]
            self.aplicar_colunas(colunas)

            for linha in leitor:
                linha_padronizada = [str(valor) if valor != "" else "" for valor in linha]
                while len(linha_padronizada) < len(colunas):
                    linha_padronizada.append("")
                self.tree.insert("", "end", values=linha_padronizada[: len(colunas)])

    def _visualizar_json(self, caminho: Path) -> None:
        dados = json.loads(caminho.read_text(encoding="utf-8"))

        if isinstance(dados, dict):
            self.aplicar_colunas(["Chave", "Valor"])
            for chave, valor in dados.items():
                self.tree.insert("", "end", values=[str(chave), self._formatar_valor(valor)])
            return

        if isinstance(dados, list) and dados and isinstance(dados[0], dict):
            colunas = list(dados[0].keys())
            self.aplicar_colunas(colunas)
            for item in dados:
                self.tree.insert("", "end", values=[self._formatar_valor(item.get(coluna)) for coluna in colunas])
            return

        self.aplicar_colunas(["Valor"])
        if isinstance(dados, list):
            for item in dados:
                self.tree.insert("", "end", values=[self._formatar_valor(item)])
        else:
            self.tree.insert("", "end", values=[self._formatar_valor(dados)])

    def _visualizar_xml(self, caminho: Path) -> None:
        arvore = ET.parse(caminho)
        raiz = arvore.getroot()

        self.aplicar_colunas(["Elemento", "Valor"])
        for elemento in raiz.iter():
            texto = "".join(elemento.itertext()).strip()
            self.tree.insert("", "end", values=[elemento.tag, texto])

    def _visualizar_txt(self, caminho: Path) -> None:
        self.aplicar_colunas(["Linha", "Conteúdo"])
        with caminho.open("r", encoding="utf-8") as arquivo:
            for numero, linha in enumerate(arquivo, start=1):
                self.tree.insert("", "end", values=[str(numero), linha.rstrip("\n")])

    def _visualizar_generico(self, caminho: Path) -> None:
        conteudo = caminho.read_text(encoding="utf-8", errors="replace")
        self.aplicar_colunas(["Conteúdo"])
        self.tree.insert("", "end", values=[conteudo[:10000]])

    @staticmethod
    def _formatar_valor(valor) -> str:
        if isinstance(valor, (dict, list)):
            return json.dumps(valor, ensure_ascii=False, indent=2)
        return str(valor)

    def copiar_e_criptografar(self) -> None:
        if self.arquivo_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um arquivo antes de copiar e criptografar.")
            return

        destino = filedialog.askdirectory(title="Escolha a pasta para salvar a cópia segura")
        if not destino:
            return

        caminho_origem = self.arquivo_selecionado
        pasta_destino = Path(destino)

        try:
            conteudo = caminho_origem.read_bytes()
            hash_original = hashlib.sha256(conteudo).hexdigest()
            criptografado = self.fernet.encrypt(conteudo)

            arquivo_saida = pasta_destino / f"{caminho_origem.name}.enc"
            arquivo_saida.write_bytes(criptografado)

            hash_saida = pasta_destino / f"{caminho_origem.name}.sha256.txt"
            hash_saida.write_text(f"sha256={hash_original}\narquivo={caminho_origem.name}\n", encoding="utf-8")

            registrar_log(
                f"Arquivo copiado de {caminho_origem} para {pasta_destino} com criptografia. Hash gerado: {hash_original}."
            )
            self.label_status.config(text=f"Cópia segura salva em: {arquivo_saida}")
            messagebox.showinfo(
                "Cópia Segura",
                f"Arquivo criptografado salvo em:\n{arquivo_saida}\n\nHash salvo em:\n{hash_saida}",
            )
        except Exception as erro:
            messagebox.showerror("Erro na cópia segura", f"Não foi possível criar a cópia protegida: {erro}")

    def descriptografar(self) -> None:
        if self.arquivo_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um arquivo antes de descriptografar.")
            return

        caminho_origem = self.arquivo_selecionado
        if caminho_origem.suffix.lower() != ".enc":
            messagebox.showwarning(
                "Arquivo Inválido",
                "Selecione um arquivo com extensão .enc para descriptografar.",
            )
            return

        destino = filedialog.askdirectory(title="Escolha a pasta para salvar o arquivo descriptografado")
        if not destino:
            return

        try:
            conteudo_criptografado = caminho_origem.read_bytes()
            conteudo_descriptografado = self.fernet.decrypt(conteudo_criptografado)

            arquivo_saida = caminho_origem.with_suffix("")
            if arquivo_saida.exists():
                arquivo_saida = Path(destino) / arquivo_saida.name
            else:
                arquivo_saida = Path(destino) / arquivo_saida.name

            arquivo_saida.write_bytes(conteudo_descriptografado)

            registrar_log(f"Arquivo {caminho_origem} descriptografado para {arquivo_saida}.")
            self.label_status.config(text=f"Arquivo descriptografado salvo em: {arquivo_saida}")
            messagebox.showinfo(
                "Descriptografia Concluída",
                f"Arquivo descriptografado salvo em:\n{arquivo_saida}",
            )
        except Exception as erro:
            messagebox.showerror(
                "Erro na descriptografia",
                f"Não foi possível descriptografar o arquivo: {erro}",
            )


if __name__ == "__main__":
    janela = tk.Tk()
    app = CofreApp(janela)
    janela.mainloop()
