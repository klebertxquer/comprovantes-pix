from flask import Flask, request, render_template, jsonify
import os
import pdfplumber

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

        with pdfplumber.open(caminho) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text()

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
        except:
            continue

    return jsonify(resultados)

def extrair_valor(texto, chave, pos=1):
    linhas = [l for l in texto.split('\n') if chave in l]
    if not linhas:
        return ""
    return linhas[pos - 1].replace(chave, "").strip()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

