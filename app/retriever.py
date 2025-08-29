import pandas as pd

class Retriever:
    def __init__(self, historico_path: str):
        self.df = pd.read_csv(historico_path)

    def buscar_similar(self, pergunta: str):
        for _, row in self.df.iterrows():
            if any(p.lower() in pergunta.lower() for p in row["input"].split()):
                return row["input"], row["output"]
        return self.df.iloc[0]["input"], self.df.iloc[0]["output"]
