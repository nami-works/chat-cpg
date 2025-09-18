import ast
import datetime
import importlib
import subprocess

from pathlib import Path

from crew import Kigen

# Caminhos base
base_dir = Path(__file__).resolve().parent
arquivo_log = base_dir / 'outputs' / 'log_execucao.md'

def limpar_codigo(caminho_codigo: str):
    '''
    Remove texto antes do primeiro import, todas as linhas com crases triplas (```), típicas de Markdown,
    e tudo o que estiver após o bloco: `if __name__ == "__main__":` e sua linha seguinte.
    '''

    with open(caminho_codigo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Remove texto antes do primeiro 'import' ou 'from'
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('import ') or linha.strip().startswith('from '):
            linhas = linhas[i:]
            break

    # Remove linhas contendo apenas ```
    linhas = [linha for linha in linhas if linha.strip() != '```']

    # Mantém até 'if __name__ == "__main__":' e a próxima linha
    nova_linhas = []
    i = 0
    while i < len(linhas):
        nova_linhas.append(linhas[i])
        if 'if __name__ == "__main__":' in linhas[i]:
            if i + 1 < len(linhas):
                nova_linhas.append(linhas[i + 1])  # também adiciona a próxima linha
            break
        i += 1

    with open(caminho_codigo, 'w', encoding='utf-8') as f:
        f.writelines(nova_linhas)

    print('[CLEANUP] ✅ Cabeçalho, blocos Markdown e rodapé removidos do código')

def limpar_requisitos(requirements: str):
    """
    Mantém apenas o bloco entre ```plaintext e ```.

    Remove qualquer outra parte, como explicações e markdown.

    Exemplo de bloco esperado:

    ```plaintext
    pacote1
    pacote2[extra]
    git+https://github.com/autor/repo.git
    ```
    """
    with open(requirements, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    inicio = conteudo.find('```plaintext')
    fim = conteudo.find('```', inicio + len('```plaintext'))

    if inicio != -1 and fim != -1:
        bloco = conteudo[inicio + len('```plaintext'):fim].strip()

        with open(requirements, 'w', encoding='utf-8') as f:
            f.write(bloco + '\n')

        print('[CLEANUP] ✅ Bloco `plaintext` extraído com sucesso para requirements.txt')
    else:
        print('[CLEANUP] ⚠️ Nenhum bloco `plaintext` encontrado. Nenhuma alteração feita.')

def instalar_requisitos(requirements = str):
    if not requirements.exists():
        print('[SETUP] Nenhum requirements.txt encontrado. Pulando instalação.')
        return

    print('[SETUP] Instalando bibliotecas a partir de requirements.txt...')

    resultado = subprocess.run(
        ['pip', 'install', '-r', str(requirements)],
        capture_output=True,
        text=True
    )

    if resultado.returncode == 0:
        print('[SETUP] ✅ Requisitos instalados com sucesso.')
        return

    print('[SETUP] ⚠️ Erros detectados. Tentando recuperar individualmente...')

    with open(requirements, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            continue

        nome_pacote = linha.split('==')[0] if '==' in linha else linha
        try:
            print(f'[SETUP] ➜ Instalando última versão de: {nome_pacote}')
            subprocess.run(['pip', 'install', nome_pacote])
        except Exception as e:
            print(f'[SETUP] ❌ Falha ao instalar {nome_pacote}: {e}')

def executar_codigo(codigo = str):
    log = []
    log.append('# 🧪 Log de Execução Técnica')
    log.append(f'\n📅 Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}')
    log.append(f'🧩 Script executado: {codigo}')
    log.append(f'🔁 Modo de execução: python {codigo}\n')
    log.append('---\n')

    if not codigo.exists():
        log.append('❌ Arquivo de código não encontrado.')
        return salvar_log(log)

    try:
        resultado = subprocess.run(
            ['python', str(codigo)],
            capture_output=True,
            text=True,
            timeout=120
        )

        if resultado.returncode == 0:
            log.append('## ✅ Resultado Geral\n\n✅ A execução foi finalizada com sucesso.\n')
        else:
            log.append('## ✅ Resultado Geral\n\n❌ A execução foi finalizada com erros.\n')
            log.append('## 🔍 Saída de erro (stderr)\n')
            log.append('```\n' + resultado.stderr.strip() + '\n```\n')

        log.append('## 📤 Saída padrão (stdout)\n')
        log.append('```\n' + resultado.stdout.strip() + '\n```\n')

        if resultado.returncode != 0:
            log.append('## ✅ Observações adicionais\n')
            if 'openai' in resultado.stderr and 'Audio' in resultado.stderr:
                log.append('- 💡 Detecção: uso de API de áudio antiga. Use client.audio.transcriptions.create(...)\n')
            if 'No module named' in resultado.stderr:
                log.append('- 💡 Verifique se todas as dependências de docs/requirements.txt estão instaladas.\n')

    except subprocess.TimeoutExpired:
        log.append('❌ Tempo de execução excedido. Verifique loops ou chamadas externas bloqueantes.')
    except Exception as e:
        log.append(f'❌ Erro inesperado: {str(e)}')

    salvar_log(log)

def salvar_log(linhas):
    with open(arquivo_log, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))
    print(f'[LOG] Arquivo salvo com diagnóstico em: {arquivo_log}')

def executar_solucao(codigo = str, requirements = str):
    limpar_codigo(codigo)
    limpar_requisitos(requirements)
    instalar_requisitos(requirements)
    executar_codigo(codigo)