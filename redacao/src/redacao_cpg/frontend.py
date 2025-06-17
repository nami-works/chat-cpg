#imports

##módulos completos
import ast
import os
import re
import yaml

##módulos renomeados
import streamlit as st

##funções de módulos
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

##funções internas
from leitor import *
from tools.extrator_seo import extrair_seo

load_dotenv()

marcas_contratantes = {
    'GE Beauty': 'gebeauty',
}

funcoes_disponiveis = {
    'ChatCPG': 'chat_cpg',
    'ChatCPG [Modo de ajuste]': 'chat_cpg_ajuste'
}

def carregar_arquivos_marca(nome_marca: str):
    base_dir = Path(__file__).resolve().parent
    pasta_marca = base_dir / 'marcas' / nome_marca

    file_estilo = pasta_marca / 'estilo.md'
    file_produtos = pasta_marca / 'produtos.md'
    file_cadastro = pasta_marca / 'cadastro.yaml'
    file_recomendacoes_formato = pasta_marca / 'recomendacoes_formato.md'

    if not file_estilo.exists() or not file_produtos.exists() or not file_cadastro.exists():
        raise FileNotFoundError(f"Arquivos incompletos para a marca '{nome_marca}'")

    with open(file_estilo, 'r', encoding='utf-8') as f:
        estilo = f.read()

    with open(file_produtos, 'r', encoding='utf-8') as f:
        produtos = f.read()

    with open(file_cadastro, 'r', encoding='utf-8') as f:
        cadastro = yaml.safe_load(f)

    with open(file_recomendacoes_formato, 'r', encoding='utf-8') as f:
        recomendacoes_formato = f.read()

    return estilo, produtos, recomendacoes_formato, cadastro['marca'], cadastro['blog'], cadastro['benchmarks']

base_dir = Path(__file__).resolve().parent
file_orientacoes = base_dir / 'orientacoes.md'
with open(file_orientacoes, 'r', encoding='utf-8') as file:
    orientacoes = file.read()

file_ryb = base_dir / 'conhecimento/ryb.md'
with open(file_ryb, 'r', encoding='utf-8') as file:
    ryb = file.read()

def escapar_chaves(texto):
    if isinstance(texto, str):
        return texto.replace("{", "{{").replace("}", "}}")
    return texto

orientacoes = escapar_chaves(orientacoes)

llms_disponiveis = {
    'OpenAI': {'Versões': {
        'GPT-4o Mini': 'gpt-4o-mini',
        'GPT-4o': 'gpt-4o',
        'GPT-3.5 Turbo': 'gpt-3.5-turbo',
        'GPT-3.5 Turbo 16K': 'gpt-3.5-turbo-16k',
        'GPT-3.5 Instruct': 'gpt-3.5-turbo-instruct',
        },
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

intro = ConversationBufferMemory()

def carregar_modelo(provedor_escolhido, id_versao, api_key):
    contexto = st.session_state.get('context', {})

    estilo = contexto.get('style', '')
    produtos = contexto.get('products', '')
    marca = contexto.get('brand', '')
    blog = contexto.get('blog', '')
    benchmarks = contexto.get('benchmarks', '')
    
    if not all([estilo, produtos, marca, blog, benchmarks]):
        st.error("Ops! Ainda falta alguma informação da marca. Verifique seus inputs!")
        st.stop()

    orientacao = f'''
    Você é um oráculo para geração de temas de blog posts.
    
    Você domina amplamente conceitos e melhores práticas para escalar marcas premium de
    bens de consumo, baseado em benchmarks de mercado, além dos conceitos que aprendeu ao
    ler detalhamente o livro {ryb}. Você aplica esse conhecimento para executar todas as
    atividades que lhe são demandadas.

    Você usa como base as {orientacoes} que recebeu, e também as informações que já tem
    sobre seu cliente (a {marca}, seus {produtos}, seu {estilo} de comunicação, os conteúdos
    disponíveis em seu {blog}, além de seus {benchmarks}.

    ####
    {resultado}
    ####

    Use essas informações como base principal para suas interações.

    ⚠️ Se o conteúdo do documento indicar algo como "Just a moment...Enable JavaScript and cookies to continue",
    oriente o usuário a **recarregar o Oráculo** para acessar corretamente os dados.
    '''

    template = ChatPromptTemplate.from_messages([
        ('system', orientacao),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    
    chat = llms_disponiveis[provedor_escolhido]['Chain'](model = id_versao, api_key = api_key)
    chain = template | chat
    st.session_state['Chain'] = chain

def menu_lateral():
    abas = st.tabs(['Brands', 'Functions', 'LLMs'])

    with abas[0]:
        marca_escolhida = st.selectbox('Choose a brand', marcas_contratantes.keys())
        id_marca = marcas_contratantes[marca_escolhida]
        try:
            estilo, produtos, recomendacoes_formato, marca, blog, benchmarks = carregar_arquivos_marca(id_marca)
        except FileNotFoundError as e:
            st.error(str(e))
            st.stop()

        # 3. Store in session_state
        st.session_state['context'] = {
            'style': estilo,
            'products': produtos,
            'format_recommendations': recomendacoes_formato,
            'brand': marca,
            'blog': blog,
            'benchmarks': benchmarks,
            'brand_id': id_marca,
        }

    with abas[1]:
        funcao_selecionada = st.selectbox('Choose a function', funcoes_disponiveis.keys())
        id_funcao_selecionada = funcoes_disponiveis[funcao_selecionada]
        st.session_state['selected_function'] = id_funcao_selecionada

    with abas[2]:
        provedor_escolhido = st.selectbox('Escolha um LLM', llms_disponiveis.keys())
        versao = st.selectbox('Selecione a versão',llms_disponiveis[provedor_escolhido]['Versões'])
        id_versao = llms_disponiveis[provedor_escolhido]['Versões'][versao]
        api_key_env = os.getenv('OPENAI_API_KEY')

        api_key = api_key_env or st.text_input(
            f'Insira a API Key da {provedor_escolhido}',
            value=st.session_state.get(f'api_key_{provedor_escolhido}', '')
        )

        st.session_state[f'api_key_{provedor_escolhido}'] = api_key

    if st.button('Reiniciar', use_container_width=True):
        st.session_state['memory'] = intro

def chat_cpg():
    st.header('📝 ChatCPG',divider='green')

    # Verifica se o modelo ainda não foi carregado
    if 'Chain' not in st.session_state:
        contexto = st.session_state.get('context', {})
        provedor_escolhido = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
        id_versao = st.session_state.get('id_versao')
        api_key = st.session_state.get(f'api_key_{provedor_escolhido}', None)

    chain = st.session_state.get('Chain')

    if chain is None:
        st.error('Toque a sineta e chame a redação! 🛎️')
        if st.button('🛎️ Iniciar reunião de pauta', use_container_width=True):
            contexto = st.session_state.get('context', {})
            provedor_escolhido = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
            id_versao = st.session_state.get('id_versao', 'gpt-4o')
            api_key = st.session_state.get(f'api_key_{provedor_escolhido}', None)

            if not api_key:
                st.warning("⚠️ Nenhuma API Key foi definida.")
                st.stop()

            carregar_modelo(provedor_escolhido, id_versao, api_key)
            st.rerun()  # 🔁 Força recarregar a interface com o modelo carregado
        st.stop()

    memoria = st.session_state.get('memory', intro)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    # If themes haven't been defined yet, keep chat active
    if ('themes' not in st.session_state or 
        'seo_themes' not in st.session_state or 
        st.session_state.get('adjustment_mode', False)):
        
        # Create welcome message
        interacao = st.chat_input('What is today\'s agenda?')
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

            # Try to extract themes dictionary
            padrao_temas = re.search(r'themes\s*=\s*\{.*?\}', resposta, re.DOTALL)
            if padrao_temas:
                try:
                    dict_temas = ast.literal_eval(padrao_temas.group(0).split('=')[1].strip())
                    if isinstance(dict_temas, dict):
                        st.session_state['themes'] = dict_temas
                        st.session_state['adjustment_mode'] = False
                except Exception as e:
                    st.warning(f"Error interpreting themes: {e}")

            # Try to extract seo_themes dictionary
            padrao_temas_seo = re.search(r'seo_themes\s*=\s*\{.*?\}', resposta, re.DOTALL)
            if padrao_temas_seo:
                try:
                    dict_temas_seo = ast.literal_eval(padrao_temas_seo.group(0).split('=')[1].strip())
                    if isinstance(dict_temas_seo, dict):
                        st.session_state['seo_themes'] = dict_temas_seo
                        st.session_state['adjustment_mode'] = False
                except Exception as e:
                    st.warning(f"Error interpreting seo_themes: {e}")

            # Try to extract macro_name
            padrao_nome_macro = re.search(r'macro_name\s*=\s*["\'].*?["\']', resposta)
            if padrao_nome_macro:
                try:
                    nome_macro = padrao_nome_macro.group(0).split('=')[1].strip().strip('"').strip("'")
                    st.session_state['macro_name'] = nome_macro
                    st.session_state['adjustment_mode'] = False
                except Exception as e:
                    st.warning(f"Error interpreting macro_name: {e}")
            
            # ➡️ Store complete response in memory
            memoria.chat_memory.add_user_message(interacao)
            memoria.chat_memory.add_ai_message(resposta)
            st.session_state['memory'] = memoria
            st.rerun()

    else:
        col1, col2 = st.columns(2)
        with col2:
            solicitar = st.button("🟢 Request content", use_container_width=True)

            if solicitar:
                # Retrieve brand data and themes
                context = st.session_state.get('context', {})
                themes = st.session_state['themes']
                brand_id = context.get("brand_id")
                if not brand_id:
                    st.warning("Could not determine brand to save themes.")
                    st.stop()

                inputs = {
                    'style': context.get('style', ''),
                    'brand': context.get('brand', ''),
                    'products': context.get('products', ''),
                    'blog': context.get('blog', ''),
                    'benchmarks': context.get('benchmarks', ''),
                    'format_recommendations': context.get('format_recommendations', ''),
                    'themes': themes,
                    'macro_name': st.session_state.get('macro_name')
                }

                # 🔽 Safe theme saving
                try:
                    brand_folder = base_dir / 'brands' / brand_id

                    # Save themes.py
                    themes_path = brand_folder / 'posts' / 'themes.py'
                    with open(themes_path, 'w', encoding='utf-8') as f:
                        f.write("themes = {\n")
                        for k, v in themes.items():
                            f.write(f'    \"{k}\": \"{v}\",\n')
                        f.write("}\n")

                    # Save seo_themes.py
                    seo_themes = st.session_state.get('seo_themes', {})
                    seo_themes_path = brand_folder / 'posts' / 'seo_themes.py'
                    with open(seo_themes_path, 'w', encoding='utf-8') as f:
                        f.write("seo_themes = {\n")
                        for k, v in seo_themes.items():
                            f.write(f'    \"{k}\": \"{v}\",\n')
                        f.write("}\n")

                    st.success('🔄 Content being developed.\nYou will receive the results by email. 📪')
                    inputs['brand_folder'] = brand_folder

                except Exception as e:
                    st.warning(f"Error saving theme files: {e}")

                # Save semantic fields for all themes
                try:
                    semantic_fields = {}
                    with open(brand_folder / 'posts' / 'semantic_fields.md', 'w', encoding='utf-8') as f:
                        for title, short_name in seo_themes.items():
                            # Extract for complete title
                            title_semantics = extrair_seo(title)
                            # Extract for short name
                            name_semantics = extrair_seo(short_name)
                            combined_theme = f"{title}: {short_name}"
                            combined_semantics = extrair_seo(combined_theme)

                            semantic_fields[title] = {
                                'short': title_semantics,
                                'complete': name_semantics,
                                'combined': combined_semantics
                            }

                            f.write(f"# {title}: {short_name}\n\n")
                            f.write("## Related keywords\n")
                            for item in title_semantics['relacionadas_google']:
                                f.write(f"- {item}\n")
                            for item in name_semantics['relacionadas_google']:
                                f.write(f"- {item}\n")
                            f.write("\n## Intent\n")
                            f.write(f"- {title_semantics['intencao_busca']}\n")
                            f.write("\n## Suggested titles\n")
                            for item in combined_semantics['titulos_sugeridos']:
                                f.write(f"- {item}\n")
                            f.write("\n## Headers\n")
                            f.write(f"**H1:** {title_semantics['h1']}\n")
                            f.write(f"**H1:** {name_semantics['h1']}\n")
                            for h2 in title_semantics['h2']:
                                f.write(f"- H2: {h2}\n")
                            for h2 in name_semantics['h2']:
                                f.write(f"- H2: {h2}\n")
                            f.write("\n---\n\n")

                    inputs['semantic_fields'] = semantic_fields  # ⬅️ inclui no dicionário que será enviado
                except Exception as e:
                    st.warning(f"Error saving semantic fields: {e}")

                # Envio para produção
                try:
                    from main import escrever
                    escrever(inputs)
                    st.success('✅ Conteúdos produzidos com sucesso!')
                except Exception as e:
                    st.error(f"Erro ao iniciar a produção dos conteúdos: {e}")
                    import traceback
                    traceback.print_exc()
        with col1:
            if st.button("🔴 Fazer ajustes", use_container_width=True):
                st.session_state['adjustment_mode'] = True

def chat_cpg_ajuste():
    st.header('⚠️🛠️ ChatCPG | Modo de ajustes',divider='orange')

def main():
    funcao_escolhida = st.session_state.get('selected_function')
    with st.sidebar:
        menu_lateral()
    if funcao_escolhida == list(funcoes_disponiveis.values())[0]:
        chat_cpg()
    if funcao_escolhida == list(funcoes_disponiveis.values())[1]:
        chat_cpg_ajuste()

if __name__ == "__main__":
    main()