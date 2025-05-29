import pandas as pd

# Criar dados de exemplo
dados = {
    "Cód Epr": [1001, 1002, 1003, 1004, 1005, 1006, 1007],
    "NOME": ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Ferreira", "Lúcia Martins", "Fernando Souza"],
    "ADMISS": ["01/01/2020", "15/03/2019", "22/05/2021", "10/11/2018", "02/07/2022", "30/09/2020", "14/04/2021"],
    "FUNÇÃO": ["Analista", "Gerente", "Técnico", "Assistente", "Coordenador", "Supervisor", "Auxiliar"],
    "21 A 31": ["OK", "", "X", "OK", "X", "", "OK"],
    "01 A 10": ["X", "OK", "OK", "", "X", "OK", ""],
    "11 A 20": ["OK", "X", "", "OK", "OK", "X", "X"]
}

# Criar DataFrame
df = pd.DataFrame(dados)

# Salvar como Excel
arquivo_saida = "funcionarios_exemplo.xlsx"
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Planilha 1", index=False)

print(f"Arquivo Excel de exemplo '{arquivo_saida}' criado com sucesso!") 