from flask import Flask, request, render_template, jsonify
from PIL import Image
import pytesseract
import os
import pdfplumber

# Define o caminho de dados do Tesseract (necessário para lang="por")
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extrair-comprovantes", methods=["POST"])
def extrair_comprovantes():
    arquivos = request.files.getlist("file")
    resultados = []

    for arquivo in arquivos:
        caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
        arquivo.save(caminho)

        texto = ""

        # Processa PDFs
        if arquivo.filename.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(caminho) as pdf:
                    for pagina in pdf.pages:
                        texto += pagina.extract_text() or ""
            except Exception as e:
                print(f"[Erro PDF] {arquivo.filename}: {e}")
                continue

        # Processa imagens (JPEG, PNG, etc.)
        else:
            try:
                imagem = Image.open(caminho)
                texto = pytesseract.image_to_string(imagem, lang="por")
                print(f"\n===== TEXTO EXTRAÍDO DE {arquivo.filename} =====")
                print(texto)
                print("===============================================\n")
            except Exception as e:
                print(f"[Erro imagem] {arquivo.filename}: {e}")
                continue

        # Extração de campos
        try:
            data = extrair_valor(texto, "Data e Hora:")
            valor = extrair_valor(texto, "Valor:")
            pagador = extrair_valor(texto, "Nome:", pos=1)
            destinatario = extrair_valor(texto, "Nome:", pos=2)
            inst_origem = extrair_valor(texto, "Instituição:")
            inst_destino = extrair_valor(texto, "Instituição:", pos=2)
            id_tx = extrair_valor(texto, "ID da transação:")

            resultados.append({
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

    return jsonify(resultados)

def extrair_valor(texto, chave, pos=1):
    linhas = [l for l in texto.split('\n') if chave in l]
    if not linhas:
        return ""
    return linhas[pos - 1].replace(chave, "").strip()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

