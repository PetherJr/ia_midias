import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Cliente OpenAI para Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Carrega planilha
produtos_df = pd.read_excel("data/SIGEQ276 - Cadastro de item.xlsx", usecols=[0, 1, 2, 3, 4])
produtos_df.columns = ["Nome", "Cod_Terceiro", "Nome_Marca", "Titulo_Site", "Descricao"]

# Palavras que indicam intenção de recomendação
PALAVRAS_CHAVE_INDICACAO = [
    "indica", "indicar", "recomenda", "recomendaria", "usar", "serve", "qual produto", 
    "o que usar", "bom pra", "pode usar", "qual é bom", "melhor produto", "sugere", "dica"
]

def gerar_resposta_com_groq(exemplo: str, pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    deseja_indicacao = any(p in pergunta_lower for p in PALAVRAS_CHAVE_INDICACAO)

    produto_relevante = None

    if deseja_indicacao:
        for _, row in produtos_df.iterrows():
            descricao = str(row["Descricao"]).lower()
            if any(p in descricao for p in pergunta_lower.split()):
                produto_relevante = row
                break

    # Prompt principal
    prompt = f"""
(resposta única, tom adaptativo, nunca negativa)

Você é meu assistente de respostas criativas para redes sociais. Sua função é responder
comentários de clientes com criatividade, leveza e empatia, igual a Salon Line, com
personalidade divertida e humana.

Diretrizes:
— Se for fofo ou carinhoso, responda de forma doce e acolhedora.
— Se for engraçado ou irônico, acompanhe no mesmo tom, com humor leve e criativo.
— Se for uma reclamação sensível ou grave (como queda de cabelo, alergia, irritação), nunca brinque. Use tom sério e acolhedor. Demonstre empatia, peça desculpas pelo ocorrido e oriente o cliente a nos chamar no direct ou SAC para tratarmos com prioridade e cuidado.
— Se for um pedido fora do esperado (ex: patrocínio ou mimos), desvie com bom humor e
originalidade, sem jamais prometer ou negar diretamente.
— Se for indicação de produto, indique as marcas mais famosas da Salon Line, (Obviamente no mesmo contexto de curvautura ou necessidade que o cliente pediu.)

Estilo da Resposta:
— Gere uma única resposta curta e criativa, estilo Twitter (máximo 2 linhas).
— Use emojis com moderação e inteligência.
— Quando possível, adicione referências de filmes, séries, músicas ou situações do cotidiano.
— Nunca use sarcasmo ofensivo, ironia pesada ou qualquer linguagem negativa.
— A resposta deve sempre manter um tom leve, espirituoso ou acolhedor, mesmo diante de críticas.

Inspirações:
Salon Line


Comentário do cliente:
"{pergunta}"
"""

    # Adiciona produto se for uma indicação válida E compatível
    if deseja_indicacao and produto_relevante is not None:
        prompt += f"""

Produto encontrado:
- Nome: {produto_relevante['Nome']}
- Marca: {produto_relevante['Nome_Marca']}
- Código: {produto_relevante['Cod_Terceiro']}
- Título no site: {produto_relevante['Titulo_Site']}
- Descrição: {produto_relevante['Descricao']}
"""
    elif deseja_indicacao:
        # Cliente quer recomendação, mas nenhum produto casa
        prompt += """
⚠️ Nenhum produto da base é compatível com essa necessidade.  
⚠️ Responda com empatia ou leveza, sem citar produto.
"""
    else:
        # Não é uma pergunta de indicação
        prompt += """
⚠️ O comentário não é uma pergunta de indicação.  
⚠️ Responda com criatividade, bom humor ou carinho — sem sugerir produto.
"""

    prompt += "\nResposta:"

    # Envia para Groq (LLaMA3)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=250
    )

    return response.choices[0].message.content.strip()
