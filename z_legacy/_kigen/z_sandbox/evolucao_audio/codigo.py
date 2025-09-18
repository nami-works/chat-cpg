```python
# evolucao_audio.py

import streamlit as st  # Para a construção da interface web
import numpy as np  # Para operações com arrays
import torch  # Necessário para a execução do modelo Whisper
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase  # Para captura de áudio do navegador
import whisper  # Para transcrição de áudio

class AudioProcessor(AudioProcessorBase):
    """
    Processador de Áudio para Streamlit WebRTC.

    A classe processa e armazena o áudio gravado pelo usuário.
    """

    def __init__(self):
        self.audio_data = None

    def recv(self, frame):
        self.audio_data = frame.to_ndarray()  # Converte o quadro de áudio em um array numpy
        return frame

def capturar_audio(duration: int = 60) -> bytes:
    """
    Captura áudio do navegador usando streamlit-webrtc.

    Parâmetros:
    duration (int): Duração máxima da captura em segundos. (default é 60)

    Retorna:
    bytes: Dados do áudio gravado.
    """
    audio_processor = AudioProcessor()  # Cria um processador de áudio
    
    st.write("Gravando áudio...")
    webrtc_streamer(key="example", audio_processor_factory=lambda: audio_processor)
    st.button("Parar Gravação")  # Botão para parar a gravação

    # O áudio gravado pode ser acessado agora via audio_processor.audio_data
    st.write("Gravação concluída.")
    return audio_processor.audio_data.tobytes()  # Retorna os bytes do áudio


def transcrever_audio(audio_bytes: bytes) -> str:
    """
    Transcreve o áudio utilizando o modelo Whisper.

    Parâmetros:
    audio_bytes (bytes): Áudio gravado em formato de bytes.

    Retorna:
    str: Texto resultante da transcrição do áudio.
    """
    model = whisper.load_model("base")  # Carrega o modelo Whisper (base)
    audio = whisper.load_audio(audio_bytes)  # Carrega os dados do áudio
    audio = whisper.pad_or_trim(audio)  # Ajusta o tamanho do áudio
    mel = whisper.log_mel_spectrogram(audio).to(model.device)  # Gera espectrograma mel

    # Realiza a transcrição
    options = whisper.DecodingOptions(language="pt")  # Define a opção de língua
    transcription = whisper.decode(model, mel, options)  # Transcreve o áudio
    return transcription.text  # Retorna o texto transcrito


def exibir_transcricao(transcricao: str) -> None:
    """
    Exibe a transcrição na interface do Streamlit.

    Parâmetros:
    transcricao (str): Texto da transcrição a ser exibido.
    """
    st.write("Transcrição:")
    st.text(transcricao)  # Exibe a transcrição


def copiar_texto(texto: str) -> None:
    """
    Copia o texto da transcrição para a área de transferência.

    Parâmetros:
    texto (str): Texto que será copiado.
    """
    st.button("Copiar Texto", on_click=lambda: st.session_state.clipboard := texto)  # Copia o texto


def lidar_erro(mensagem: str) -> None:
    """
    Exibe mensagem de erro na interface.

    Parâmetros:
    mensagem (str): Mensagem de erro a ser exibida.
    """
    st.error(mensagem)  # Exibe mensagem de erro no Streamlit


# Estrutura principal da aplicação
def main() -> None:
    """
    Executa o fluxo principal do módulo evolucao_audio.
    """
    st.title("Módulo de Evolução por Áudio")
    st.sidebar.header("Configurações")

    # Menu lateral para configurações
    duration = st.sidebar.slider("Duração da gravação (segundos)", 1, 60, 10)
    if st.sidebar.button("Iniciar Gravação"):
        try:
            audio_bytes = capturar_audio(duration)  # Captura áudio
            transcricao = transcrever_audio(audio_bytes)  # Transcreve áudio
            exibir_transcricao(transcricao)  # Exibe transcrição
            copiar_texto(transcricao)  # Permite copiar a transcrição
        except Exception as e:
            lidar_erro(f"Ocorreu um erro: {str(e)}")  # Lida com erros

if __name__ == "__main__":
    main()  # Executa o fluxo principal
``` 

### Notas sobre o código:
- O código é modular e segue as diretrizes do PEP 257, incluindo documentação clara para cada função.
- As funções são projetadas para serem reutilizáveis e facilmente testáveis.
- O uso de `streamlit`, `streamlit-webrtc`, e `whisper` é bem integrado ao fluxo da aplicação, evitando dependências desnecessárias.
- A estrutura do programa garante fácil manutenção e futura expansão.
- A função de copiar texto utiliza uma abordagem do Streamlit, mantendo a usabilidade fácil para o usuário.