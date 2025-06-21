from flask import Flask, request, render_template, send_file, redirect
from PIL import Image
import pytesseract
import pdfplumber
import os

from flask import Flask, request, render_template, send_file, redirect, flash
from PIL import Image, UnidentifiedImageError
import pytesseract
import pdfplumber
import os
import pandas as pd

from extrator import extrair_dados_pix
from database import criar_banco, salvar_no_banco, obter_todos

app = Flask(__name__)
app.secret_key = "segredo-para-flash"  # Necessário para mensagens flash

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

criar_banco()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extrair-comprovantes", methods=["POST"])
def extrair():
    arquivos = request.files.getlist("file")

    if not arquivos or arquivos[0].filename == "":
        flash("Nenhum arquivo enviado.")
        return redirect("/")

    for arquivo in arquivos:
        filename = arquivo.filename
        ext = filename.lower().split('.')[-1]
        caminho = os.path.join(UPLOAD_FOLDER, filename)
        arquivo.save(caminho)

        try:
            texto = ""

            if ext == "pdf":
                with pdfplumber.open(caminho) as pdf:
                    for pagina in pdf.pages:
                        texto += pagina.extract_text() or ""

            elif ext in ["png", "jpg", "jpeg"]:
                imagem = Image.open(caminho)
                texto = pytesseract.image_to_string(imagem, lang="por")

            elif ext == "xlsx":
                df = pd.read_excel(caminho)
                for _, row in df.iterrows():
                    dados = {
                        "data": row.get("Data", ""),
                        "valor": row.get("Valor", ""),
                        "pagador": row.get("Pagador", ""),
                        "destinatario": row.get("Destinatário", ""),
                        "instituicao_origem": row.get("Instituição Origem", ""),
                        "instituicao_destino": row.get("Instituição Destino", ""),
                        "id_transacao": row.get("ID Transação", "")
                    }
                    if any(dados.values()):
                        salvar_no_banco(dados)
                continue

            else:
                flash(f"Formato não suportado: {ext}")
                continue

            dados = extrair_dados_pix(texto)
            if any(dados.values()):
                salvar_no_banco(dados)

        except UnidentifiedImageError:
            flash(f"Erro ao processar imagem: {filename}")
        except Exception as e:
            flash(f"Erro geral ao processar {filename}: {str(e)}")

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
    ws.title = "Comprovantes PIX"
    ws.append(["Data", "Valor", "Pagador", "Destinatário", "Instituição Origem", "Instituição Destino", "ID Transação"])
    
    for row in obter_todos():
        ws.append(row[1:])  # Ignora ID interno (index 0)

    output_path = "resultado_pix.xlsx"
    wb.save(output_path)
    return send_file(output_path, as_attachment=True)
