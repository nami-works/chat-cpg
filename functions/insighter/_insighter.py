import streamlit as st
from pathlib import Path
import sys
import os
from datetime import datetime

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Language-sensitive UI text
UI_TEXT = {
    'en_US': {
        'request_analysis_title': '🔍 **Request Market Analysis**',
        'analysis_topic_label': '**Analysis Topic**',
        'analysis_topic_placeholder': 'e.g., E-commerce market in Brazil, SaaS industry trends, AI market opportunities',
        'analysis_topic_help': 'Specify the market, industry, or topic you want to analyze',
        'additional_context_label': '**Additional Context/Focus Areas**',
        'additional_context_placeholder': 'e.g., Focus on B2B segment, emerging technologies, regulatory environment...',
        'additional_context_help': 'Provide additional context or specific focus areas for the analysis',
        'quick_overview_label': '**Quick Market Overview**',
        'quick_overview_help': 'Enable for faster, simplified analysis with basic insights. Disable for comprehensive deep-dive analysis with detailed reports and strategic recommendations.',
        'include_recommendations_label': '**Include Strategic Recommendations**',
        'include_recommendations_help': 'Include actionable recommendations and next steps',
        'include_visualizations_label': '**Include Data Visualizations**',
        'include_visualizations_help': 'Include charts, graphs, and visual data representations',
        'launch_analysis_button': '🚀 **Launch Analysis**',
        'please_specify_topic': '⚠️ Please specify an analysis topic!',
        'initializing_crew': '🔍 **Initializing analysis crew...**',
        'conducting_research': '📊 **Conducting market research...**',
        'analyzing_competition': '🏆 **Analyzing competition and trends...**',
        'generating_reports': '📋 **Generating final reports...**',
        'analysis_completed': '✅ **Analysis completed successfully!**',
        'analysis_success': '✅ **Analysis completed successfully!**',
        'reports_saved': '📁 Reports saved in:',
        'analysis_summary_title': '📋 **Analysis Summary**',
        'topic_analyzed': '**Topic Analyzed:**',
        'analysis_type': '**Analysis Type:**',
        'depth': '**Depth:**',
        'reports_generated': '**Reports Generated:**',
        'output_location': '**Output Location:**',
        'comprehensive_analysis': 'Comprehensive Market Analysis',
        'quick_overview_analysis': 'Quick Market Overview',
        'deep_dive': 'Deep Dive Analysis',
        'quick_overview': 'Quick Overview',
        'reports_count_comprehensive': '7 comprehensive reports',
        'reports_count_quick': '3 summary reports',
        'missing_dependencies': '❌ **Missing dependencies:**',
        'install_packages': '💡 Please install required packages: `pip install crewai langchain-openai`',
        'analysis_failed': '❌ **Analysis failed:**',
        'try_simplifying': '💡 Try simplifying your request or check your internet connection.',
        'quick_templates_title': '⚡ **Quick Analysis Templates**',
        'ecommerce_market': '🏪 **E-commerce Market**',
        'saas_industry': '💻 **SaaS Industry**',
        'ai_market': '🤖 **AI Market**',
        'quick_analysis_ready': '🚀 **Quick Analysis Ready:**',
        'run_quick_analysis': '✅ **Run Quick Analysis**',
        'quick_analysis_completed': '✅ **Quick analysis completed for:**',
        'cancel': '❌ **Cancel**',
        'chat_title': '💬 **Chat with Insighter**',
        'chat_subtitle': '*Ask me about markets, trends, or get help with your analysis!*',
        'not_loaded_error': 'Insighter is not loaded. Please load the model first.',
        'load_insighter': 'Load Insighter',
        'load_insighter_info': 'Please use the \'Load\' button in the sidebar to initialize Insighter.',
            'download_research': '📥 **Download Research**',
    'download_help': 'Download all generated reports as a ZIP file',
    'running_quick_analysis': '⚡ **Running quick analysis...**',
    'zip_created_success': '✅ ZIP file created successfully!',
    'zip_error': '❌ Error creating ZIP file:'
    },
    'pt_BR': {
        'request_analysis_title': '🔍 **Solicitar Análise de Mercado**',
        'analysis_topic_label': '**Tópico da Análise**',
        'analysis_topic_placeholder': 'ex: Mercado de e-commerce no Brasil, tendências da indústria SaaS, oportunidades no mercado de IA',
        'analysis_topic_help': 'Especifique o mercado, indústria ou tópico que deseja analisar',
        'additional_context_label': '**Contexto Adicional/Áreas de Foco**',
        'additional_context_placeholder': 'ex: Foco no segmento B2B, tecnologias emergentes, ambiente regulatório...',
        'additional_context_help': 'Forneça contexto adicional ou áreas específicas de foco para a análise',
        'quick_overview_label': '**Visão Geral Rápida do Mercado**',
        'quick_overview_help': 'Ative para análise mais rápida e simplificada com insights básicos. Desative para análise abrangente com relatórios detalhados e recomendações estratégicas.',
        'include_recommendations_label': '**Incluir Recomendações Estratégicas**',
        'include_recommendations_help': 'Incluir recomendações acionáveis e próximos passos',
        'include_visualizations_label': '**Incluir Visualizações de Dados**',
        'include_visualizations_help': 'Incluir gráficos, tabelas e representações visuais de dados',
        'launch_analysis_button': '🚀 **Iniciar Análise**',
        'please_specify_topic': '⚠️ Por favor, especifique um tópico de análise!',
        'initializing_crew': '🔍 **Inicializando equipe de análise...**',
        'conducting_research': '📊 **Realizando pesquisa de mercado...**',
        'analyzing_competition': '🏆 **Analisando concorrência e tendências...**',
        'generating_reports': '📋 **Gerando relatórios finais...**',
        'analysis_completed': '✅ **Análise concluída com sucesso!**',
        'analysis_success': '✅ **Análise concluída com sucesso!**',
        'reports_saved': '📁 Relatórios salvos em:',
        'analysis_summary_title': '📋 **Resumo da Análise**',
        'topic_analyzed': '**Tópico Analisado:**',
        'analysis_type': '**Tipo de Análise:**',
        'depth': '**Profundidade:**',
        'reports_generated': '**Relatórios Gerados:**',
        'output_location': '**Local de Saída:**',
        'comprehensive_analysis': 'Análise Abrangente de Mercado',
        'quick_overview_analysis': 'Visão Geral Rápida do Mercado',
        'deep_dive': 'Análise Profunda',
        'quick_overview': 'Visão Geral Rápida',
        'reports_count_comprehensive': '7 relatórios abrangentes',
        'reports_count_quick': '3 relatórios resumidos',
        'missing_dependencies': '❌ **Dependências ausentes:**',
        'install_packages': '💡 Por favor, instale os pacotes necessários: `pip install crewai langchain-openai`',
        'analysis_failed': '❌ **Análise falhou:**',
        'try_simplifying': '💡 Tente simplificar sua solicitação ou verifique sua conexão com a internet.',
        'quick_templates_title': '⚡ **Modelos de Análise Rápida**',
        'ecommerce_market': '🏪 **Mercado E-commerce**',
        'saas_industry': '💻 **Indústria SaaS**',
        'ai_market': '🤖 **Mercado de IA**',
        'quick_analysis_ready': '🚀 **Análise Rápida Pronta:**',
        'run_quick_analysis': '✅ **Executar Análise Rápida**',
        'quick_analysis_completed': '✅ **Análise rápida concluída para:**',
        'cancel': '❌ **Cancelar**',
        'chat_title': '💬 **Conversar com Insighter**',
        'chat_subtitle': '*Pergunte-me sobre mercados, tendências ou obtenha ajuda com sua análise!*',
        'not_loaded_error': 'Insighter não foi carregado. Por favor, carregue o modelo primeiro.',
        'load_insighter': 'Carregar Insighter',
        'load_insighter_info': 'Por favor, use o botão \'Carregar\' na barra lateral para inicializar o Insighter.',
            'download_research': '📥 **Baixar Pesquisa**',
    'download_help': 'Baixar todos os relatórios gerados como arquivo ZIP',
    'running_quick_analysis': '⚡ **Executando análise rápida...**',
    'zip_created_success': '✅ Arquivo ZIP criado com sucesso!',
    'zip_error': '❌ Erro ao criar arquivo ZIP:'
    }
}

# Get system language
import locale
system_lang = locale.getdefaultlocale()[0]
current_lang = 'pt_BR' if system_lang and system_lang.startswith('pt') else 'en_US'
LANG = UI_TEXT[current_lang]

def handle_insighter_flow(chat_interaction, chain, memory):
    """
    Handle the insighter flow in the UI - analysis request interface + chat
    
    Args:
        chat_interaction: Function to handle chat interactions
        chain: The LLM chain
        memory: Conversation memory
    """
    
    # Side by side layout: Context (60%) and Analysis Request (40%)
    col1, col2 = st.columns([60, 40])
    
    with col1:
        # Context section - language sensitive
        from functions.insighter.context import INSIGHTER_CONTEXT
        
        # Get context based on current language
        context_section = INSIGHTER_CONTEXT['context_section'][current_lang]
        st.markdown(f"### {context_section['title']}")
        st.markdown(context_section['content'])
    
    with col2:
        # Analysis Request Interface
        st.markdown(f"### {LANG['request_analysis_title']}")
        
        analysis_topic = st.text_input(
            LANG['analysis_topic_label'],
            placeholder=LANG['analysis_topic_placeholder'],
            help=LANG['analysis_topic_help']
        )
        
        additional_context = st.text_area(
            LANG['additional_context_label'],
            placeholder=LANG['additional_context_placeholder'],
            height=80,
            help=LANG['additional_context_help']
        )
        
        # Quick overview toggle
        quick_overview = st.toggle(
            LANG['quick_overview_label'],
            help=LANG['quick_overview_help']
        )
        
        # Options (only show if not quick overview)
        if not quick_overview:
            include_recommendations = st.checkbox(
                LANG['include_recommendations_label'],
                value=True,
                help=LANG['include_recommendations_help']
            )
            
            include_visualizations = st.checkbox(
                LANG['include_visualizations_label'],
                value=True,
                help=LANG['include_visualizations_help']
            )
        else:
            include_recommendations = False
            include_visualizations = False
        
        # Analysis trigger button
        if st.button(LANG['launch_analysis_button'], type="primary", use_container_width=True):
            if not analysis_topic.strip():
                st.error(LANG['please_specify_topic'])
                return
            
            # Show analysis progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text(LANG['initializing_crew'])
                progress_bar.progress(10)
                
                # Import and run the insighter crew
                from insighter.main import analyze_market, generate_quick_analysis
                
                status_text.text(LANG['conducting_research'])
                progress_bar.progress(30)
                
                # Prepare analysis parameters
                analysis_params = {
                    'topic': analysis_topic,
                    'quick_overview': quick_overview,
                    'include_recommendations': include_recommendations,
                    'include_visualizations': include_visualizations,
                    'additional_context': additional_context,
                    'timestamp': datetime.now().strftime("%Y-%m-%d_%H-%M")
                }
                
                # Create output directory
                output_dir = f"insighter_analysis_{analysis_topic.lower().replace(' ', '_').replace('-', '_')}_{analysis_params['timestamp']}"
                
                status_text.text(LANG['analyzing_competition'])
                progress_bar.progress(50)
                
                # Run the analysis based on type
                if quick_overview:
                    result = generate_quick_analysis(analysis_topic)
                    analysis_type = LANG['quick_overview_analysis']
                    depth = LANG['quick_overview']
                    reports_count = LANG['reports_count_quick']
                else:
                    result = analyze_market(
                        topic=analysis_topic,
                        additional_context=f"Analysis Type: Comprehensive Market Analysis\nDepth: Deep Dive Analysis\nInclude Recommendations: {include_recommendations}\nInclude Visualizations: {include_visualizations}\n\nAdditional Context: {additional_context}",
                        output_dir=output_dir
                    )
                    analysis_type = LANG['comprehensive_analysis']
                    depth = LANG['deep_dive']
                    reports_count = LANG['reports_count_comprehensive']
                
                status_text.text(LANG['generating_reports'])
                progress_bar.progress(90)
                
                # Display success message
                progress_bar.progress(100)
                status_text.text(LANG['analysis_completed'])
                
                st.success(f"{LANG['analysis_success']}\n\n{LANG['reports_saved']} `{output_dir}`")
                
                # Show analysis summary
                st.markdown(f"### {LANG['analysis_summary_title']}")
                st.info(f"""
                {LANG['topic_analyzed']} {analysis_topic}
                {LANG['analysis_type']} {analysis_type}
                {LANG['depth']} {depth}
                {LANG['reports_generated']} {reports_count}
                {LANG['output_location']} {output_dir}
                """)
                
                # Download research button
                if st.button(LANG['download_research'], help=LANG['download_help']):
                    try:
                        import zipfile
                        import tempfile
                        
                        # Create ZIP file
                        zip_filename = f"insighter_research_{analysis_topic.lower().replace(' ', '_')}_{analysis_params['timestamp']}.zip"
                        
                        with zipfile.ZipFile(zip_filename, 'w') as zipf:
                            # Add all files from output directory
                            for root, dirs, files in os.walk(output_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, output_dir)
                                    zipf.write(file_path, arcname)
                        
                        # Provide download link
                        with open(zip_filename, 'rb') as f:
                            st.download_button(
                                label="📥 Download ZIP",
                                data=f.read(),
                                file_name=zip_filename,
                                mime="application/zip"
                            )
                        
                        st.success(LANG['zip_created_success'])
                        
                    except Exception as e:
                        st.error(f"{LANG['zip_error']} {str(e)}")
                
                # Add analysis result to chat memory
                if memory:
                    analysis_summary = f"Market analysis completed for '{analysis_topic}'. Analysis type: {analysis_type}, Depth: {depth}. Reports saved in {output_dir}."
                    memory.chat_memory.add_ai_message(analysis_summary)
                    st.session_state['memory'] = memory
                
            except ImportError as e:
                st.error(f"{LANG['missing_dependencies']} {str(e)}")
                st.info(LANG['install_packages'])
            except Exception as e:
                st.error(f"{LANG['analysis_failed']} {str(e)}")
                st.info(LANG['try_simplifying'])
            finally:
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
    
    # Quick Analysis Templates
    st.markdown(f"### {LANG['quick_templates_title']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(LANG['ecommerce_market'], use_container_width=True):
            st.session_state['quick_analysis'] = "E-commerce market trends and opportunities"
    
    with col2:
        if st.button(LANG['saas_industry'], use_container_width=True):
            st.session_state['quick_analysis'] = "SaaS industry competitive landscape and growth opportunities"
    
    with col3:
        if st.button(LANG['ai_market'], use_container_width=True):
            st.session_state['quick_analysis'] = "Artificial Intelligence market analysis and emerging opportunities"
    
    # Handle quick analysis
    if 'quick_analysis' in st.session_state:
        quick_topic = st.session_state['quick_analysis']
        st.info(f"{LANG['quick_analysis_ready']} {quick_topic}")
        
        if st.button(LANG['run_quick_analysis'], key="run_quick"):
            with st.spinner(LANG['running_quick_analysis']):
                try:
                    from insighter.main import generate_quick_analysis
                    result = generate_quick_analysis(quick_topic)
                    st.success(f"{LANG['quick_analysis_completed']} {quick_topic}")
                    
                    # Add to chat memory
                    if memory:
                        quick_summary = f"Quick analysis completed for '{quick_topic}'. Results available in generated reports."
                        memory.chat_memory.add_ai_message(quick_summary)
                        st.session_state['memory'] = memory
                    
                except Exception as e:
                    st.error(f"{LANG['analysis_failed']} {str(e)}")
        
        if st.button(LANG['cancel'], key="cancel_quick"):
            del st.session_state['quick_analysis']
            st.rerun()
    
    st.divider()
    
    # Chat Interface
    st.markdown(f"### {LANG['chat_title']}")
    st.markdown(f"*{LANG['chat_subtitle']}*")
    
    # Simple chat interface for insighter
    if chain is not None:
        # Handle chat interaction
        response = chat_interaction("", chain, memory, key="insighter_chat")
        
        # No additional UI elements - just pure chat
        return response
    
    else:
        st.error(LANG['not_loaded_error'])
        if st.button(LANG['load_insighter'], key="load_insighter"):
            st.info(LANG['load_insighter_info']) 