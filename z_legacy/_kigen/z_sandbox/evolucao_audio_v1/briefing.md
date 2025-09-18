evolucao_audio

# 📋 Briefing - Módulo de Evolução por Áudio (`evolucao_audio`)

## 🎯 Problema
Criar uma interface em Streamlit que permita que médicos registrem rapidamente, por meio de **mensagem de voz**, os principais pontos discutidos durante uma consulta. O conteúdo deve ser transcrito automaticamente e apresentado de forma limpa, pronta para ser **copiada e colada** em sistemas médicos.

## ⚙️ Requisitos Funcionais
1. **Gravação de Áudio**
   - Usar `streamlit-webrtc` para capturar áudio diretamente no navegador.
   - Desabilitar vídeo (somente áudio).
   - Funcionar apenas em ambiente HTTPS (exibir alerta se for local/inseguro).

2. **Transcrição de Áudio**
   - Utilizar o modelo **Whisper** (open-source ou via API).
   - Suportar idioma **português (BR)**.
   - Permitir tempo máximo de gravação de **60 segundos**.

3. **Exibição**
   - Apresentar a transcrição formatada imediatamente após gravação.
   - Incluir botão “**Copiar texto**”.
   - Apresentar mensagem de erro em caso de falha na transcrição.

## 📥 Entradas Esperadas
- Gravação de áudio do navegador (stream).
- Opção de configuração de idioma (fixo em `pt` inicialmente).

## 📤 Saídas Esperadas
- Texto transcrito da evolução médica.
- Botão para copiar rapidamente para a área de transferência.
- Mensagens visuais de erro ou sucesso.

## 🧰 Bibliotecas Sugeridas
- `streamlit-webrtc` para gravação.
- `whisper` para transcrição.
- `pydub`, `io`, `numpy`, `torch` se necessário para manipulação.
- `streamlit` para interface e cópia.

## 🎯 Objetivo Final
Facilitar o registro da **evolução médica**, reduzindo o atrito do profissional com sistemas de prontuário, mantendo agilidade e precisão com o uso de voz.

## 🧠 Observações Estratégicas
- UX deve ser extremamente leve e sem fricção.
- Interface pronta para ser integrada como iframe ou módulo embutido.
- Armazenamento de áudio opcional (não obrigatório inicialmente).