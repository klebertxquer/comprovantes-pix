import re

def extrair_dados_pix(texto):
    def buscar(regex):
        resultado = re.search(regex, texto, re.IGNORECASE)
        return resultado.group(1).strip() if resultado else ""

    return {
        "data": buscar(r"Data e Hora[:\s]+([^\n]+)"),
        "valor": buscar(r"Valor[:\s]+R?\$?\s?([\d\.,]+)"),
        "pagador": buscar(r"Pagador(?:[:\s]+|[\n])([^\n]+)"),
        "destinatario": buscar(r"Destinat.rio(?:[:\s]+|[\n])([^\n]+)"),
        "instituicao_origem": buscar(r"Instituiç[aã]o de origem[:\s]+([^\n]+)"),
        "instituicao_destino": buscar(r"Instituiç[aã]o de destino[:\s]+([^\n]+)"),
        "id_transacao": buscar(r"ID da transaç[aã]o[:\s]+([A-Z0-9\-]+)")
    }
