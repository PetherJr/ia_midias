from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import Mensagem
from app.retriever import Retriever
from app.groq_responder import gerar_resposta_com_groq

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
retriever = Retriever("data/historico.csv")

@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "resposta": None})

@app.post("/", response_class=HTMLResponse)
async def processar_pergunta(request: Request, texto: str = Form(...)):
    exemplo = retriever.buscar_similar(texto)
    resposta = gerar_resposta_com_groq(exemplo, texto)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pergunta": texto,
        "resposta": resposta
    })

@app.post("/responder")
def responder_mensagem(msg: Mensagem):
    exemplo = retriever.buscar_similar(msg.texto)
    resposta = gerar_resposta_com_groq(exemplo, msg.texto)
    return {"resposta": resposta}
