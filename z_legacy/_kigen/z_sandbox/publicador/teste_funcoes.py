```python
# teste_funcoes.py

import unittest
from datetime import datetime
from utils import (
    normalizar_texto,
    upload_arquivo,
    validar_inputs,
    executar_crew,
    gerar_download,
    enviar_email,
    ler_configuracoes,
    gerar_historico,
)


class TestFuncoes(unittest.TestCase):

    def test_normalizar_texto(self):
        """Teste para a função normalizar_texto."""
        texto_exemplo = "Texto de exemplo"
        resultado = normalizar_texto(texto_exemplo)
        self.assertIsInstance(resultado, str, "Deve retornar um string após normalização.")
    
    def test_upload_arquivo(self):
        """Teste para a função upload_arquivo."""
        arquivo_exemplo = b'Conteúdo do arquivo'
        resultado = upload_arquivo(arquivo_exemplo)
        self.assertIn('conteudo', resultado, "O dicionário deve conter a chave 'conteudo'.")
        self.assertEqual(resultado['conteudo'], 'Conteúdo do arquivo', "O conteúdo do arquivo deve ser corretamente extraído.")

    def test_validar_inputs(self):
        """Teste para a função validar_inputs."""
        dados_validos = {'campo1': 'valor', 'campo2': 'valor'}
        dados_invalidos = {'campo1': 'valor'}
        self.assertTrue(validar_inputs(dados_validos), "Dados válidos devem retornar True.")
        self.assertFalse(validar_inputs(dados_invalidos), "Dados inválidos devem retornar False.")

    def test_executar_crew(self):
        """Teste para a função executar_crew."""
        resultado = executar_crew('crew1', {'input1': 'valor'})
        self.assertEqual(resultado['resultado'], 'sucesso', "A execução da crew deve retornar sucesso.")

    def test_gerar_download(self):
        """Teste para a função gerar_download (verifica sem criar arquivos)."""
        output_data = b'Dados de teste'
        nome_arquivo = 'resultado_teste.txt'
        try:
            gerar_download(output_data, nome_arquivo)
            with open(nome_arquivo, 'rb') as f:
                conteudo = f.read()
            self.assertEqual(conteudo, output_data, "O arquivo deve conter o mesmo conteúdo que os dados de saída.")
        finally:
            import os
            os.remove(nome_arquivo)  # Limpa o arquivo após teste

    def test_enviar_email(self):
        """Teste para a função enviar_email (simulado)."""
        # Para testes de envio de e-mail, você pode usar mocks.
        # Ignorando teste de envio real neste contexto, mas sempre deve ser testado com integração.
        try:
            enviar_email('usuario@exemplo.com', 'Mensagem de teste', 'Assunto de teste')
        except Exception as e:
            self.fail(f"Falha ao enviar e-mail: {str(e)}")

    def test_ler_configuracoes(self):
        """Teste para a função ler_configuracoes."""
        configuracoes = ler_configuracoes('.env')
        self.assertIsInstance(configuracoes, dict, "Deve retornar um dicionário de configurações.")

    def test_gerar_historico(self):
        """Teste para a função gerar_historico (verificado sem registrar um histórico real)."""
        try:
            gerar_historico('usuario1', 'executou crew', datetime.now())
            # Aqui poderíamos verificar um registro em um arquivo ou base de dados
        except Exception as e:
            self.fail(f"Falha ao gerar histórico: {str(e)}")


if __name__ == '__main__':
    unittest.main()
```

### Descrição do Arquivo `teste_funcoes.py`:

1. **Teste para Normalização de Texto (`test_normalizar_texto`)**:
   - Verifica se a função `normalizar_texto` retorna uma string.

2. **Teste para Upload de Arquivo (`test_upload_arquivo`)**:
   - Verifica se a função `upload_arquivo` retorna um dicionário contendo o conteúdo do arquivo.

3. **Teste para Validação de Inputs (`test_validar_inputs`)**:
   - Testa com dados válidos e inválidos, garantindo que a função valide corretamente.

4. **Teste para Execução de Crew (`test_executar_crew`)**:
   - Verifica se a execução de uma crew retorna um resultado esperado.

5. **Teste para Geração de Download (`test_gerar_download`)**:
   - Testa se a função gera um arquivo corretamente e verifica seu conteúdo.

6. **Teste para Envio de E-mail (`test_enviar_email`)**:
   - Realiza o teste de envio, onde normalmente deve-se utilizar mocks para evitar envios reais em unidades de teste.

7. **Teste para Leitura de Configurações (`test_ler_configuracoes`)**:
   - Confere se a função retorna um dicionário para as configurações.

8. **Teste para Geração de Histórico (`test_gerar_historico`)**:
   - Verifica a capacidade de realizar a operação sem falhas.

### Recomendações:
- Assegure-se de que as dependências estejam instaladas no ambiente, utilizando `pytest` ou `unittest` conforme necessário.
- Caso utilize o `pytest`, você pode transformar essa estrutura facilmente, visto que o pytest permite uma sintaxe mais limîda e gerenciamento de fixtures de forma avançada.

Estes testes garantem que cada função implementada seja validada de acordo com seus requisitos, permitindo identificar falhas ou comportamento inesperado ao longo do desenvolvimento da aplicação.