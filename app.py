from flask import Flask, request, render_template, jsonify
import os
import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException

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

        try:
            with pdfplumber.open(caminho) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text() or ""
                    if texto.strip() == "":
                        continue

                    data = extrair_valor(texto, "Data", pos=1)
                    valor = extrair_valor(texto, "Valor", pos=1)
                    pagador = extrair_valor(texto, "Nome", pos=1)
                    destinatario = extrair_valor(texto, "Nome", pos=2)
                    inst_origem = extrair_valor(texto, "Instituição", pos=1)
                    inst_destino = extrair_valor(texto, "Instituição", pos=2)
                    id_tx = extrair_valor(texto, "Autenticação", pos=1)

                    resultados.append({
                        "data": data,
                        "valor": valor,
                        "pagador": pagador,
                        "destinatario": destinatario,
                        "instituicoes": f"{inst_origem} → {inst_destino}",
                        "id": id_tx
                    })
        except PdfminerException as e:
            print(f"Erro ao abrir {arquivo.filename}: {e}")
            continue

    return jsonify(resultados)

def extrair_valor(texto, chave, pos=1):
    linhas = [l for l in texto.split('\n') if chave in l]
    if not linhas or len(linhas) < pos:
        return ""
    return linhas[pos - 1].replace(chave, "").strip()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

