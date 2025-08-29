import os
import pandas as pd
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Carrega a planilha de produtos
produtos_df = pd.read_excel("data/SIGEQ276 - Cadastro de item.xlsx", usecols=[0, 1, 2, 3, 4])
produtos_df.columns = ["Nome", "Cod_Terceiro", "Nome_Marca", "Titulo_Site", "Descricao"]

def gerar_resposta_com_groq(exemplo: str, pergunta: str) -> str:
    client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

    # Detecta produtos relacionados ao tipo de cabelo mencionado
    termos_cabelo = {
        "cacheado": ["cacheado", "cachos", "ondulado", "crespo"],
        "liso": ["liso", "alisar", "alisado", "chapado"],
        "loiro": ["loiro", "descolorido"],
        "danificado": ["danificado", "quebra", "ressecado"],
    }

    # Filtra produtos por palavras-chave
    candidatos = []

    for _, row in produtos_df.iterrows():
        descricao = str(row["Descricao"]).lower()
        if any(termo in pergunta.lower() for termo in descricao.split()):
            candidatos.append(row)

    # Se nenhum candidato por descrição, tenta por tipo de cabelo
    if not candidatos:
        for tipo, palavras in termos_cabelo.items():
            if any(p in pergunta.lower() for p in palavras):
                for _, row in produtos_df.iterrows():
                    if any(p in str(row["Descricao"]).lower() for p in palavras):
                        candidatos.append(row)
                break

    # Se ainda não encontrou, responde que vai ajudar no privado
    if not candidatos:
        return "Oi, miga! 💕 Ainda não achei um produtinho exato aqui, mas me chama no privado que eu te ajudo com todo carinho! 💌✨"

    # Escolhe aleatoriamente um dos candidatos
    produto = random.choice(candidatos)

    contexto_produto = (
        f"Produto: {produto['Nome']}\n"
        f"Marca: {produto['Nome_Marca']}\n"
        f"Código: {produto['Cod_Terceiro']}\n"
        f"Título no site: {produto['Titulo_Site']}\n"
        f"Descrição: {produto['Descricao']}"
    )

    prompt = f"""
Você é um atendente da Salon Line. Responda comentários com simpatia, emojis, proximidade e sempre com base nos dados abaixo:

⚠️ NUNCA cite produtos ou marcas concorrentes.  
⚠️ NUNCA invente produtos que não estão no sistema.  
⚠️ Em caso de reclamação, convide para o privado com carinho.  
⚠️ Consulte apenas os produtos abaixo para responder.

TOM E VOZ:
- Use linguagem amigável, empoderadora e acolhedora
- Use emojis como 💕, ✨, 💁🏾‍♀️, 😍
- Fale com carinho: “miga”, “você arrasa”, “vamos juntas!”

EXEMPLO DE RESPOSTA:
{exemplo}

PERGUNTA DO CLIENTE:
{pergunta}

DADOS DO PRODUTO:
{contexto_produto}

RESPOSTA:
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Poxa, algo deu errado aqui do meu ladinho 😢 Me chama no privado que vou te ajudar rapidinho, miga! 💕"
