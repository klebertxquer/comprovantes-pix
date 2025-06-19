from flask import Flask, request, render_template, jsonify, send_file
from PIL import Image
import pytesseract
import pdfplumber
import os
import openpyxl

os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

RESULTADOS = []

@app.route("/")
def index():
    return render_template("index.html", resultados=RESULTADOS)

@app.route("/extrair-comprovantes", methods=["POST"])
def extrair_comprovantes():
    arquivos = request.files.getlist("file")
    global RESULTADOS
    RESULTADOS = []

    for arquivo in arquivos:
        caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
        arquivo.save(caminho)
        texto = ""

        if arquivo.filename.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(caminho) as pdf:
                    for pagina in pdf.pages:
                        texto += pagina.extract_text() or ""
            except Exception as e:
                print(f"[Erro PDF] {arquivo.filename}: {e}")
                continue
        else:
            try:
                imagem = Image.open(caminho)
                texto = pytesseract.image_to_string(imagem, lang="por")
            except Exception as e:
                print(f"[Erro imagem] {arquivo.filename}: {e}")
                continue

        try:
            data = extrair_valor(texto, "Data e Hora:")
            valor = extrair_valor(texto, "Valor:")
            pagador = extrair_valor(texto, "Nome:", pos=1)
            destinatario = extrair_valor(texto, "Nome:", pos=2)
            inst_origem = extrair_valor(texto, "Instituição:")
            inst_destino = extrair_valor(texto, "Instituição:", pos=2)
            id_tx = extrair_valor(texto, "ID da transação:")

            RESULTADOS.append({
                "data": data,
                "valor": valor,
                "pagador": pagador,
                "destinatario": destinatario,
                "instituicoes": f"{inst_origem} → {inst_destino}",
                "id": id_tx
            })
        except Exception as e:
            print(f"[Erro extração] {arquivo.filename}: {e}")
            continue

    return render_template("index.html", resultados=RESULTADOS)

@app.route("/exportar-excel")
def exportar_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Data", "Valor", "Pagador", "Destinatário", "Instituições", "ID Transação"])
    for item in RESULTADOS:
        ws.append([
            item["data"],
            item["valor"],
            item["pagador"],
            item["destinatario"],
            item["instituicoes"],
            item["id"]
        ])
    caminho = "resultado_pix.xlsx"
    wb.save(caminho)
    return send_file(caminho, as_attachment=True)

@app.route("/limpar", methods=["POST"])
def limpar():
    global RESULTADOS
    RESULTADOS = []
    return render_template("index.html", resultados=RESULTADOS)

from flask import Flask, request, render_template, jsonify, send_file

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
