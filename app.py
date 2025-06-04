import streamlit as st
import os
import io
from datetime import datetime
from src import extrair_transformar_carregar_pdf, gerar_pdf
import pytz

fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")
                                    
st.title("Correção de Relatório")
    
    # Campo para digitar o nome do profissional
professor = st.text_input("Digite o nome do profissional:")
    
    # Upload do arquivo PDF
uploaded_file = st.file_uploader("Selecione o arquivo de comissão - PDF", type=["pdf"])
if uploaded_file is not None:
    st.write("Arquivo carregado:", uploaded_file.name)

    # Cria um buffer para múltiplas leituras do arquivo
    pdf_bytes = io.BytesIO(uploaded_file.read())

    # Resetar o ponteiro do arquivo para nova leitura
    pdf_bytes.seek(0)

    # Extração da tabela e transformação dos dados
    arquivo_transformado = extrair_transformar_carregar_pdf(pdf_bytes)

    # Define a data e hora atual formatada
    timestamp = datetime.now(pytz.utc).astimezone(fuso_horario_brasil).strftime("%d-%m-%Y %H:%M")

    # Geração do PDF com os dados transformados
    pdf_buffer = gerar_pdf(arquivo_transformado, professor, timestamp)
    st.success("Relatório feito com sucesso!")

    # Define o nome do arquivo com base no nome do professor e data/hora
    nome_arquivo = f"Relatório {professor if professor else 'SemNome'} {timestamp}.pdf"

    # Botão para download do PDF transformado
    st.download_button(
        label="Download do Relatório",
        data=pdf_buffer,
        file_name=nome_arquivo,
        mime="application/pdf"
    )
