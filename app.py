from flask import Flask, request, render_template, send_file, redirect
from PIL import Image
import pytesseract
import pdfplumber
import os

from extrator import extrair_dados_pix
from database import criar_banco, salvar_no_banco, obter_todos

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
criar_banco()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extrair-comprovantes", methods=["POST"])
def extrair():
    arquivos = request.files.getlist("file")

    for arquivo in arquivos:
        caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
        arquivo.save(caminho)

        texto = ""
        if arquivo.filename.lower().endswith(".pdf"):
            with pdfplumber.open(caminho) as pdf:
                for pagina in pdf.pages:
                    texto += pagina.extract_text() or ""
        else:
            imagem = Image.open(caminho)
            texto = pytesseract.image_to_string(imagem, lang="por")

        dados = extrair_dados_pix(texto)
        if any(dados.values()):
            salvar_no_banco(dados)

    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    dados = obter_todos()
    return render_template("dashboard.html", dados=dados)

@app.route("/exportar-excel")
def exportar_excel():
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Data", "Valor", "Pagador", "Destinatário", "Instituição Origem", "Instituição Destino", "ID Transação"])
    for row in obter_todos():
        ws.append(row[1:])
    wb.save("resultado_pix.xlsx")
    return send_file("resultado_pix.xlsx", as_attachment=True)

