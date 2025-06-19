from flask import Flask, request, render_template, jsonify, send_file
import os
import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException
import pytesseract
from PIL import Image
import io
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

dados_extraidos = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extrair-comprovantes", methods=["POST"])
def extrair_comprovantes():
    global dados_extraidos
    dados_extraidos = []

    arquivos = request.files.getlist("file")
    for arquivo in arquivos:
        caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
        arquivo.save(caminho)

        texto = ""

        # Verifica extensão
        if caminho.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(caminho) as pdf:
                    for pagina in pdf.pages:
                        texto += pagina.extract_text() or ""
            except PdfminerException as e:
                print(f"[PDF inválido] {arquivo.filename} - {e}")
                continue
        elif caminho.lower().endswith((".png", ".jpg", ".jpeg")):
            try:
                imagem = Image.open(caminho)
                texto = pytesseract.image_to_string(imagem, lang="por")
            except Exception as e:
                print(f"[Imagem inválida] {arquivo.filename} - {e}")
                continue
        else:
            continue  # ignora outros formatos

        # Extração
        data = extrair_valor(texto, "Realizado em:")
        valor = extrair_valor(texto, "Valor:")
        pagador = extrair_valor(texto, "Nome do pagador:")
        destinatario = extrair_valor(texto, "Nome do destinatário:")
        inst_origem = extrair_valor(texto, "Instituição do pagador:")
        inst_destino = extrair_valor(texto, "Instituição do destinatário:")
        id_tx = extrair_valor(texto, "ID da transação:")

        dados_extraidos.append({
            "data": data,
            "valor": valor,
            "pagador": pagador,
            "destinatario": destinatario,
            "instituicoes": f"{inst_origem} → {inst_destino}",
            "id": id_tx
        })

    return jsonify(dados_extraidos)

@app.route("/exportar-excel")
def exportar_excel():
    if not dados_extraidos:
        return "Nenhum dado extraído ainda.", 400

    df = pd.DataFrame(dados_extraidos)
    excel_path = "comprovantes.xlsx"
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

def extrair_valor(texto, chave, pos=1):
    linhas = [l for l in texto.split('\n') if chave in l]
    if not linhas:
        return ""
    return linhas[pos - 1].replace(chave, "").strip()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
