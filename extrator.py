import re

def extrair_dados_pix(texto):
    dados = {
        "data": "",
        "valor": "",
        "pagador": "",
        "destinatario": "",
        "instituicao_origem": "",
        "instituicao_destino": "",
        "id_transacao": ""
    }

    # Expressões regulares para detectar padrões comuns
    data_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    valor_match = re.search(r"R\$ ?([\d\.,]+)", texto)
    pagador_match = re.search(r"Pagador:?\s*(.*)", texto)
    destinatario_match = re.search(r"Favorecido|Destinatário:?\s*(.*)", texto)
    instituicao_match = re.findall(r"Institui.*?:?\s*(.*)", texto)
    id_transacao_match = re.search(r"(E2E|ID Transa[cç][aã]o)[^\w]?([A-Z0-9\-]+)", texto)

    # Preenchimento seguro
    if data_match:
        dados["data"] = data_match.group(1)

    if valor_match:
        dados["valor"] = valor_match.group(1).replace(".", "").replace(",", ".")

    if pagador_match:
        dados["pagador"] = pagador_match.group(1).strip()

    if destinatario_match:
        dados["destinatario"] = destinatario_match.group(1).strip()

    if instituicao_match:
        if len(instituicao_match) >= 2:
            dados["instituicao_origem"] = instituicao_match[0].strip()
            dados["instituicao_destino"] = instituicao_match[1].strip()
        elif len(instituicao_match) == 1:
            dados["instituicao_origem"] = instituicao_match[0].strip()

    if id_transacao_match:
        dados["id_transacao"] = id_transacao_match.group(2)

    return dados
