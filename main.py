import pdfplumber
import pandas as pd
from pandas import DataFrame




def extract_table_from_pdf(pdf):
    """ Extracts a table from a PDF file."""
    dados = []
    try:
        with pdfplumber.open(pdf) as pdf_file:
            for page in pdf_file.pages:
                tables = page.extract_tables()
                if tables:
                    for lines in tables[0]:
                        dados.append(lines)
        dataframe = pd.DataFrame(dados[1:-1], columns= dados[0])
        return dataframe
    except Exception as e:
        raise Exception(f'Erro ao extrair tabela do PDF: {e}')
    
def converter_coluna_valor_para_int(dados):
    if dados is not None:
        try:
            dados['Valor'] = dados['Valor'].str.replace(',','.', regex = True)
            dados['Valor'] = pd.to_numeric(dados['Valor'], errors='coerce')
            return pd.DataFrame(dados)
        except Exception as e:
            raise Exception(f'Erro ao mudar o tipo da coluna Valor: {e}')

    
def converter_reposições(dados: DataFrame):
    """Identifica aulas remarcadas e calcula reposição"""
    if dados is not None:
        try:
            dados_tratados = converter_coluna_valor_para_int(dados)
            if dados_tratados is not None:
                dados_tratados.loc[dados_tratados['Status'].str.contains("Rem", case= False, na= False) & 
                        dados_tratados['Serviço'].str.contains('Pilates', case = False, na = False), 'Valor'] -= 8
                 
                dados_tratados.loc[dados_tratados['Valor'].isnull() &
                dados_tratados['Serviço'].str.contains('Pilates', case = False, na = False) &
                ~dados_tratados['Serviço'].str.contains('Experi', case = False, na = False), 'Valor'] = 8
                return dados_tratados
        except Exception as e:
            raise Exception(f'Erro ao converter reposições: {e}')

def comissão_total(dados):
    if dados is not None:
        total = dados['Valor'].sum()
        return total

if __name__ == '__main__':
    dados = extract_table_from_pdf("arquivo_teste/BRUNO.pdf")
    convertido = converter_reposições(dados)
    print(convertido)
    total = comissão_total(convertido)
    print(f'Total: {total}')