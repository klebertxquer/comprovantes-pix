from flask import Flask, request, render_template, jsonify
from PIL import Image
import pytesseract
import pdfplumber
import os

# Define o caminho do idioma para o Tesseract
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

        # PDF
        if arquivo.filename.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(caminho) as pdf:
                    for pagina in pdf.pages:
                        texto += pagina.extract_text() or ""
            except Exception as e:
                print(f"[Erro PDF] {arquivo.filename}: {e}")
                continue
        else:
            # Imagem (JPEG/PNG) com OCR
            try:
                imagem = Image.open(caminho)
                texto = pytesseract.image_to_string(imagem, lang="por")
                print(f"\n[OCR {arquivo.filename}]\n{texto}\n")
            except Exception as e:
                print(f"[Erro imagem] {arquivo.filename}: {e}")
                continue

        # Extrai campos do texto
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
    linhas = texto.split('\n')
    resultados = [l for l in linhas if chave.lower() in l.lower()]
    if not resultados:
        return ""
    try:
        idx = linhas.index(resultados[pos - 1])
        return linhas[idx + 1].strip()
    except:
        return ""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
