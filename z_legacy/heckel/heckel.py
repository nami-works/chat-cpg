#imports

##módulos completos
import ast
import json
import os
import re
import tempfile
import yaml

##módulos renomeados
import streamlit as st

##funções de módulos
from datetime import datetime
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

##funções internas
from leitor import *

load_dotenv()

llms_disponiveis = {
    'Anthropic': {'Versões': {
        'Claude 3.7 Sonnet': 'claude-3-7-sonnet-20250219',
        'Claude 4 Opus':'claude-opus-4-20250514',
        'Claude 3.5 Haiku': 'claude-3-5-haiku-20241022',
        },
        'api_key': 'ANTHROPIC_API_KEY',
        'Chain': ChatAnthropic},
    'OpenAI': {'Versões': {
        'GPT-4o Mini': 'gpt-4o-mini',
        'GPT-4o': 'gpt-4o',
        'GPT-3.5 Turbo': 'gpt-3.5-turbo',
        'GPT-3.5 Turbo 16K': 'gpt-3.5-turbo-16k',
        'GPT-3.5 Instruct': 'gpt-3.5-turbo-instruct',
        },
        'api_key': 'OPENAI_API_KEY',
        'Chain': ChatOpenAI},
    'Groq':{
        'Versões': {
            'LLaMA 3 70B': 'llama3-groq-70b-8192-tool-use-preview',
            'LLaMA 3 8B': 'llama3-groq-8b-8192-tool-use-preview',
            'LLaMA 3.3 70B': 'llama-3.3-70b-versatile',
            'LLaMA 3.1 8B': 'llama-3.1-8b-instant',
            'Compound Beta': 'compound-beta',
        },
        'Chain': ChatGroq},
}
inputs_validos = [
    'Website',
    'YouTube video',
    'PDF file',
    'csv file',
    'txt file'
]

# marcas_contratantes = {
#     'GE Beauty': 'gebeauty',
# }

# def carregar_arquivos_cliente(nome_marca: str):
#     base_dir = Path(__file__).resolve().parent
#     pasta_marca = base_dir / 'marcas' / nome_marca

#     file_estilo = pasta_marca / 'estilo.md'
#     file_produtos = pasta_marca / 'produtos.md'
#     file_cadastro = pasta_marca / 'cadastro.yaml'

#     if not file_estilo.exists() or not file_produtos.exists() or not file_cadastro.exists():
#         raise FileNotFoundError(f"Arquivos incompletos para a marca '{nome_marca}'")

#     with open(file_estilo, 'r', encoding='utf-8') as f:
#         estilo = f.read()

#     with open(file_produtos, 'r', encoding='utf-8') as f:
#         produtos = f.read()

#     with open(file_cadastro, 'r', encoding='utf-8') as f:
#         cadastro = yaml.safe_load(f)

#     return estilo, produtos, cadastro['marca'], cadastro['blog'], cadastro['benchmarks']

base_dir = Path(__file__).resolve().parent
file_orientacoes = base_dir / 'orientacoes.md'
with open(file_orientacoes, 'r', encoding='utf-8') as file:
    orientacoes = file.read()

def escapar_chaves(texto):
    if isinstance(texto, str):
        return texto.replace("{", "{{").replace("}", "}}")
    return texto

orientacoes = escapar_chaves(orientacoes)

base_dir = Path(__file__).resolve().parent
file_conhecimento = base_dir / 'conhecimento.jsonl'

def carregar_conhecimento():
    conhecimento = []
    with open(file_conhecimento, 'r', encoding='utf-8') as file:
        for linha in file:
            registro = json.loads(linha)
            if registro.get('importancia') in ['alta', 'media']:
                conhecimento.append(registro['conteudo'])
    return '\n'.join(conhecimento)

conhecimento = carregar_conhecimento()



# temas_validos = [
#     'IA',
#     'Negócios',
#     'Economia',
#     'Política',
#     'Marketing de Influência'
# ]

intro = ConversationBufferMemory()

def carregar_input(tipo_input, input):
    if tipo_input == inputs_validos[0]:
        resultado = leitor_sites(input)
    if tipo_input == inputs_validos[1]:
        resultado = leitor_youtube(input)
    if tipo_input == inputs_validos[2]:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete = False) as temp:
            temp.write(input.read())
            nome_temp = temp.name
        resultado = leitor_pdf(nome_temp)
    if tipo_input == inputs_validos[3]:
        with tempfile.NamedTemporaryFile(suffix='.csv', delete = False) as temp:
            temp.write(input.read())
            nome_temp = temp.name
        resultado = leitor_csv(nome_temp)
    if tipo_input == inputs_validos[4]:
        with tempfile.NamedTemporaryFile(suffix='.csv', delete = False) as temp:
            temp.write(input.read())
            nome_temp = temp.name
        resultado = leitor_txt(nome_temp)
    return resultado

def carregar_modelo(provedor_escolhido, id_versao, api_key, tipo_input, input):
    # contexto = st.session_state.get('contexto', {})
    if not input:
        resultado ='No input sent. Interact using existing context'
    else:
        resultado = carregar_input(tipo_input, input)
    # if not video_id:
    #     raise ValueError("O ID do vídeo está vazio.")
    # estilo = contexto.get('estilo', '')
    # produtos = contexto.get('produtos', '')
    # marca = contexto.get('marca', '')
    # blog = contexto.get('blog', '')
    # benchmarks = contexto.get('benchmarks', '')
    # orientacoes = contexto.get('orientacoes', '')
    # conhecimento = contexto.get('conhecimento', '')
    
    # if not all([estilo, produtos, marca, blog, benchmarks]):
    #     st.error("Ops! Ainda falta alguma informação da marca. Verifique seus inputs!")
    #     st.stop()


    orientacao = f'''
    You are a strategic oracle dedicated to identifying product opportunities, actionable insights, and emerging trends in the universe of artificial intelligence.

    Your operation is based on the {orientacoes} received, as well as the information you have already accumulated in your incremental {conhecimento} file,
    built from analyzed content, recorded reflections, previous responses, and tested MVPs.

    Upon receiving a new input (such as a transcript, idea, or question), you should look for patterns, connections, and relevant learnings to help the user decide
    where to invest energy and test prototypes. Your goal is to support the emergence of AI products that have real value, clear purpose, and alignment with current trends.

    You have access to the following information coming from a document of type **{tipo_input}**:

    ####
    {resultado}
    ####

    Use this input as the main basis for your interactions.

    ⚠️ If the document content indicates something like "Just a moment...Enable JavaScript and cookies to continue", advise the user to **reload the Oracle** to correctly access the data.

    '''

    template = ChatPromptTemplate.from_messages([
        ('system', orientacao),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    
    chat = llms_disponiveis[provedor_escolhido]['Chain'](model = id_versao, api_key = api_key)
    chain = template | chat
    st.session_state['Chain'] = chain

def chat_principal():
    st.header('Heckel 👴🧠',divider='orange')

    chain = st.session_state.get('Chain')

    if chain is None:
        st.error('You need to summon Heckel!')
        st.stop()
        # if st.button('Alô, Heckel?! 📳', use_container_width=True):
        #     contexto = st.session_state.get('contexto', {})
        #     tipo_input = st.session_state.get('tipo_input', tipo_input)
        #     input = st.session_state.get('input', input)
        #     provedor_escolhido = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
        #     id_versao = st.session_state.get('id_versao', 'gpt-4o')
        #     api_key = st.session_state.get(f'api_key_{provedor_escolhido}', None)
            

            # if not api_key:
            #     st.warning("⚠️ Nenhuma API Key foi definida.")
            #     st.stop()

        #     carregar_modelo(provedor_escolhido, id_versao, api_key, tipo_input, input)
        #     st.rerun()  # 🔁 Força recarregar a interface com o modelo carregado
        # st.stop()

    memoria = st.session_state.get('memoria', intro)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    # Se os temas ainda não foram definidos, manter o chat ativo
    if 'insights_extraidos' not in st.session_state or st.session_state.get('modo_ajuste', False):
    
    # Criar mensagem de boas vindas
        interacao = st.chat_input("Let's learn!")
        if interacao:
            chat = st.chat_message('human')
            chat.markdown(interacao)

            chat = st.chat_message('ai')
            resposta = chat.write_stream(
                chain.stream({
                    'input': interacao,
                    'chat_history': memoria.buffer_as_messages
                })
            )

            # Regex para capturar objetos JSON válidos
            padrao_json = re.findall(
                r'\{[^{}]*"slug"[^{}]*"source"[^{}]*\}',
                resposta
            )

            if padrao_json:
                entradas_validas = []
                for bloco in padrao_json:
                    try:
                        entrada = json.loads(bloco)
                        if isinstance(entrada, dict):
                            entradas_validas.append(entrada)
                    except json.JSONDecodeError as e:
                        st.warning(f"Error while interpreting the insight: {e}")

                if entradas_validas:
                    st.session_state['insights_extraidos'] = entradas_validas
                    st.session_state['modo_ajuste'] = False  # ✅ desativa modo ajuste
                    st.rerun()

            # Registro da interação
            memoria.chat_memory.add_user_message(interacao)
            memoria.chat_memory.add_ai_message(resposta)
            st.session_state['memoria'] = memoria
            st.rerun()

    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔴🔄 Review insight", use_container_width=True):
                st.session_state['modo_ajuste'] = True
        with col2:
            adicionar_insight = st.button("🟢🧠 Add insight", use_container_width=True)
            # Validação
            if adicionar_insight:
            #     if not email_para:
            #         st.info('💡 Por favor, insira seu e-mail para prosseguir.')
            #     elif not email_ok:
            #         st.warning('⚠️ E-mail inválido. Verifique o formato.')

            # # ⬇️ Lógica de submissão
            # if solicitar and email_ok:
            #     # Recuperar dados da marca e os temas
            #     contexto = st.session_state.get('contexto', {})
            #     temas = st.session_state['temas']
            #     id_marca = contexto.get("id_marca")
            #     if not id_marca:
            #         st.warning("Não foi possível determinar a marca para salvar os temas.")
            #         st.stop()

            #     inputs = {
            #         'estilo': contexto.get('estilo', ''),
            #         'marca': contexto.get('marca', ''),
            #         'produtos': contexto.get('produtos', ''),
            #         'blog': contexto.get('blog', ''),
            #         'benchmarks': contexto.get('benchmarks', ''),
            #         'temas': temas
            #     }
            #     inputs['email_para'] = email_para

                # 🔽 Salvamento seguro dos temas
                try:
                    onde_salvar = 'conhecimento.jsonl'
                    with open(onde_salvar, 'a', encoding='utf-8') as f:
                        for insight in st.session_state['insights_extraidos']:
                            novo_registro = {
                                "timestamp": datetime.utcnow().isoformat() + 'Z',
                                "source": insight.get('source', 'unknown source'),
                                "type": insight.get('type', 'insight'),
                                "content": insight.get('content', ''),
                                "tags": insight.get('tags', []),
                                "origin": insight.get('origin', 'heckel'),
                                "relevance": insight.get('relevance', 'high'),
                                "related_to": insight.get('related_to', [])
                            }
                            f.write(json.dumps(novo_registro, ensure_ascii=False) + '\n')

                    st.success("🧠 Insights succesfully added to Heckel's knowledge base.")

                except Exception as e:
                    st.warning(f"Error while adding insights to Heckel's context: {e}")

                # Envio para produção
                # try:
                #     from main import escrever
                #     escrever(inputs)
                #     st.success('✅ Conteúdos enviados para produção com sucesso!')
                # except Exception as e:
                #     st.error(f"Erro ao iniciar a produção dos conteúdos: {e}")
                #     import traceback
                #     traceback.print_exc()


def menu_lateral():
    abas = st.tabs(['Inputs','LLMs'])
    with abas[0]:
        tipo_input = st.selectbox('Choose the file type', inputs_validos)
        if tipo_input == inputs_validos[0]:
            input = st.text_input('Type the URL')
        if tipo_input == inputs_validos[1]:
            input = st.text_input('Type the video ID')
        if tipo_input == inputs_validos[2]:
            input = st.file_uploader('Upload the file', type=['.pdf'])
        if tipo_input == inputs_validos[3]:
            input = st.file_uploader('Upload the file', type=['.csv'])
        if tipo_input == inputs_validos[4]:
            input = st.file_uploader('Upload the file', type=['.txt'])
    with abas[1]:
        provedor_escolhido = st.selectbox('Choose a LLM', llms_disponiveis.keys())
        versao = st.selectbox('Choose a version',llms_disponiveis[provedor_escolhido]['Versões'])
        id_versao = llms_disponiveis[provedor_escolhido]['Versões'][versao]
        api_key_env = os.getenv(llms_disponiveis[provedor_escolhido]['api_key'])

        api_key = api_key_env

        st.session_state[f'api_key_{provedor_escolhido}'] = api_key
   
    if st.button('Go, Heckel! 🚀', use_container_width=True):
        if not input:
            resultado ='No input sent. Interact using existing context'
        else:
            resultado = carregar_input(tipo_input, input)
        print(resultado)
        carregar_modelo(provedor_escolhido, id_versao, api_key, tipo_input, input)
    
    if st.button('Restart', use_container_width=True):
        st.session_state['memoria'] = intro
        
    # with abas[2]:
    #     tema_escolhido = st.selectbox('Escolha um tema', temas_validos)
    #     if tema_escolhido == temas_validos[0]:
    #         pass
    #     if tema_escolhido == temas_validos[1]:
    #         pass
    #     if tema_escolhido == temas_validos[2]:
    #         pass
    #     if tema_escolhido == temas_validos[3]:
    #         pass
    #     if tema_escolhido == temas_validos[4]:
    #         pass

def main():
    with st.sidebar:
        menu_lateral()
    chat_principal()

if __name__ == "__main__":
    main()


