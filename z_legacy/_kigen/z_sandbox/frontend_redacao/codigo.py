import streamlit as st
from typing import List, Dict

# Função para adicionar um novo tema à lista de temas.
def inserir_tema(tema: str) -> None:
    """Adiciona um novo tema à lista de temas.

    Args:
        tema (str): O tema a ser adicionado.

    Returns:
        None: Esta função não retorna valor.
    """
    if 'temas' not in st.session_state:
        st.session_state.temas = []
        
    if validar_tema(tema):
        st.session_state.temas.append(tema)
        mensagem_feedback(f'Tema "{tema}" adicionado com sucesso!')
    else:
        mensagem_feedback('Tema inválido! O tema deve ter menos de 150 caracteres.')

# Função para remover um tema específico da lista.
def remover_tema(tema: str) -> None:
    """Remove um tema específico da lista.

    Args:
        tema (str): O tema a ser removido.

    Returns:
        None: Esta função não retorna valor.
    """
    if 'temas' in st.session_state and tema in st.session_state.temas:
        st.session_state.temas.remove(tema)
        mensagem_feedback(f'Tema "{tema}" removido com sucesso!')

# Função para obter a lista atual de temas.
def obter_temas() -> List[str]:
    """Retorna a lista atual de temas.

    Returns:
        List[str]: Lista de temas armazenados.
    """
    return st.session_state.get('temas', [])

# Função para validar se o tema possui menos de 150 caracteres.
def validar_tema(tema: str) -> bool:
    """Valida se o tema tem menos de 150 caracteres.

    Args:
        tema (str): O tema a ser validado.

    Returns:
        bool: Retorna True se o tema é válido, False caso contrário.
    """
    return len(tema) <= 150

# Função para construir um dicionário a partir dos temas inseridos.
def enviar_temas(temas: List[str]) -> Dict[str, List[str]]:
    """Constrói um dicionário de temas e inicia a crew de Redação.

    Args:
        temas (List[str]): Lista de temas a serem enviados.

    Returns:
        Dict[str, List[str]]: Dicionário estruturado de temas.
    """
    # Aqui você pode montar a estrutura adequada antes de enviar.
    return {'temas': temas}

# Função para exibir mensagens de feedback ao usuário.
def mensagem_feedback(mensagem: str) -> None:
    """Exibe uma mensagem de feedback para o usuário.

    Args:
        mensagem (str): Mensagem a ser exibida.

    Returns:
        None: Esta função não retorna valor.
    """
    st.write(mensagem)

# Estrutura básica da aplicação Streamlit
def main():
    st.header("Produza seus Blog Posts", divider = 'green')

    # Entrada para inserir tema
    novo_tema = st.text_input("Inclua um tema:")
    if st.button("Incluir"):
        inserir_tema(novo_tema)
        st.rerun()

    # Botão para visualizar os temas
    # if st.button("Visualizar Temas"):
    temas = obter_temas()
    st.write("Temas atuais:", temas)

    # Entrada para remover tema
    tema_remover = st.text_input("Copie e cole o tema para remover:")
    if st.button("Remover Tema"):
        remover_tema(tema_remover)
        st.rerun()

# Executa a aplicação
if __name__ == "__main__":
    main()