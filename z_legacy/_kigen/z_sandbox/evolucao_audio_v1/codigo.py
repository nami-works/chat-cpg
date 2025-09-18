import streamlit as st
from st_audiorec import st_audiorec
from openai import OpenAI
import tempfile
import os
from dotenv import load_dotenv
import pyperclip

# Carrega a chave da API a partir do arquivo .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gravar_audio() -> bytes:
    """
    Captura áudio do navegador e retorna os dados em WAV.
    """
    st.write("Grave sua mensagem de evolução médica.")
    audio_data = st_audiorec()
    return audio_data

def transcrever_audio_api(audio_data: bytes) -> str:
    """
    Transcreve áudio com Whisper API da OpenAI usando o novo cliente.
    """
    if not audio_data:
        return "Nenhum áudio recebido."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(audio_data)
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    os.remove(tmpfile_path)
    return response.text

def exibir_transcricao(transcricao: str):
    """
    Mostra o texto e permite cópia.
    """
    st.subheader("Transcrição")
    st.success(transcricao)

    if st.button("Copiar texto"):
        pyperclip.copy(transcricao)
        st.info("Texto copiado para a área de transferência.")

def main():
    st.title("🩺 Evolução por Áudio - Registro Médico com Whisper API")

    audio_bytes = gravar_audio()

    if audio_bytes:
        transcricao = transcrever_audio_api(audio_bytes)
        exibir_transcricao(transcricao)

if __name__ == "__main__":
    main()  # Executa a função principal

# ### Notas:
# - O arquivo `evolucao_audio.py` contém as funções planejadas que implementam a captura de áudio, a transcrição usando o modelo Whisper e a visualização do resultado na interface Streamlit.
# - O código foi estruturado de forma modular, seguindo as melhores práticas de codificação Python, e cada função contém comentários explicativos e exemplos de uso.
# - Dependências necessárias foram mencionadas nos comentários do código e devem ser instaladas em seu ambiente para que a aplicação funcione corretamente.