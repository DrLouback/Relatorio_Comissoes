import pdfplumber
import pandas as pd
from pandas import DataFrame
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io



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
        dataframe = pd.DataFrame(dados[1:-1], columns= dados[0]).reset_index()
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
                # Casas decimais para 2
                dados_tratados['Valor'] = dados_tratados['Valor'].round(2)
                dados_tratados.fillna(0, inplace=True)
                return dados_tratados
        except Exception as e:
            raise Exception(f'Erro ao converter reposições: {e}')

def comissão_total(dados):
    if dados is not None:
        total = dados['Valor'].sum()
        return total
    
def gerar_pdf(arquivo_transformado, professor, timestamp):
    """
    Gera o PDF transformado com a tabela e o cabeçalho.
    O cabeçalho inclui as informações extraídas do PDF, o nome do professor
    e a data/hora da geração do relatório.
    O PDF é criado em memória e retornado em um buffer.
    """
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    style = getSampleStyleSheet()
    
    
    info_professor = f"Professor: {professor}" if professor else ""
    info_data = f"Relatório gerado em: {timestamp}"
    header_text = f"<br/>{info_professor}<br/>{info_data}"
    header = Paragraph(header_text, style=style['Heading2'])
    
    # Junta os dados da tabela: cabeçalho e linhas
    dados_tabela = [arquivo_transformado.columns.tolist()] + arquivo_transformado.values.tolist()
    tabela = Table(dados_tabela)
    total = comissão_total(arquivo_transformado)
    texto = f'Valor total R${total:.2f}'
    texto_valor = Paragraph(texto, style=style['Heading3'])
    # Define a estilização da tabela
    estilo = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.white),  
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),  
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),  
        ("GRID", (0, 0), (-1, -1), 1, colors.gray),
        ("FONTSIZE", (0, 0), (-1, -1), 8), 
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
    ])
    tabela.setStyle(estilo)
    
    elements = [header, Spacer(1, 12), tabela, texto_valor]
    pdf.build(elements)
    
    # Retorna o buffer para download
    buffer.seek(0)
    return buffer

def extrair_transformar_carregar_pdf(arquivo):
        dados = extract_table_from_pdf(arquivo)
        convertido = converter_reposições(dados)
        return convertido

if __name__ == '__main__':
   
    pass