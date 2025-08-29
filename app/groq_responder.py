import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Inicializa cliente OpenAI com base no Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Carrega planilha de produtos
produtos_df = pd.read_excel("data/SIGEQ276 - Cadastro de item.xlsx", usecols=[0, 1, 2, 3, 4])
produtos_df.columns = ["Nome", "Cod_Terceiro", "Nome_Marca", "Titulo_Site", "Descricao"]

def gerar_resposta_com_groq(exemplo: str, pergunta: str) -> str:
    produto_encontrado = None

    for _, row in produtos_df.iterrows():
        termos_para_buscar = [
            str(row["Nome"]).lower(),
            str(row["Titulo_Site"]).lower(),
            str(row["Nome_Marca"]).lower()
        ]
        if any(termo in pergunta.lower() for termo in termos_para_buscar):
            produto_encontrado = row
            break

    # Prompt base com tom criativo adaptativo
    prompt = f"""
Você é meu assistente de respostas criativas para redes sociais. Sua função é responder
comentários de clientes com criatividade, leveza e empatia, como se fosse uma marca com
personalidade divertida e humana.

Diretrizes:
Analise o comentário recebido e adapte sua resposta ao tom do cliente:
— Se for fofo ou carinhoso, responda de forma doce e acolhedora.
— Se for engraçado ou irônico, acompanhe no mesmo tom, com humor leve e criativo.
— Se for sério, responda com leveza ou acolhimento, mantendo a empatia.
— Se for um pedido fora do esperado (ex: patrocínio ou mimos), desvie com bom humor e
originalidade, sem jamais prometer ou negar diretamente.

Estilo da Resposta:
Gere uma única resposta curta e criativa, estilo Twitter (máximo 2 linhas).
Use emojis com moderação e inteligência.

Quando possível, adicione referências de filmes, séries, músicas ou situações do cotidiano.
Nunca use sarcasmo ofensivo, ironia pesada ou qualquer linguagem negativa. A resposta
deve sempre manter um tom leve, espirituoso ou acolhedor, mesmo diante de críticas.

Inspirações:
Marcas como Duolingo, Netflix e Salon Line.
Sua missão é manter o público engajado, fazer sorrir e fortalecer o vínculo com a marca.

Exemplo de atendimento:
{exemplo}

Comentário do cliente:
{pergunta}
"""

    # Se achou um produto, insere contexto técnico
    if produto_encontrado is not None:
        prompt += f"""

Informações sobre o produto mencionado:
- Nome: {produto_encontrado['Nome']}
- Marca: {produto_encontrado['Nome_Marca']}
- Código: {produto_encontrado['Cod_Terceiro']}
- Título no site: {produto_encontrado['Titulo_Site']}
- Descrição: {produto_encontrado['Descricao']}
"""

    # Final do prompt
    prompt += "\nResposta:"

    # Chamada ao modelo Groq com LLaMA 3
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=250
    )

    return response.choices[0].message.content.strip()
