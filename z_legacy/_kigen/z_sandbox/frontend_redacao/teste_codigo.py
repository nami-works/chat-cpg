```python
import unittest
from your_module import inserir_tema, remover_tema, obter_temas, validar_tema, enviar_temas, mensagem_feedback

class TestGerenciamentoTemas(unittest.TestCase):

    def setUp(self):
        """Configura o estado de sessão antes de cada teste."""
        # Estrutura inicial para simular o estado de sessão do Streamlit
        import streamlit as st
        st.session_state.clear()  # Limpa o estado de sessão antes de cada teste
    
    def test_inserir_tema_valido(self):
        """Teste para adicionar um tema válido à lista."""
        inserir_tema("Tema de Teste")
        self.assertIn("Tema de Teste", obter_temas(), msg='O tema deveria estar na lista após inserção.')

    def test_inserir_tema_invalido(self):
        """Teste para tentar adicionar um tema inválido."""
        inserir_tema("Tema com mais de 150 caracteres" * 10)  # Tema muito longo
        self.assertNotIn("Tema com mais de 150 caracteres" * 10, obter_temas(), msg='O tema não deveria ser adicionado.')

    def test_remover_tema_existente(self):
        """Teste para remover um tema que existe na lista."""
        inserir_tema("Tema para Remover")
        self.assertIn("Tema para Remover", obter_temas())
        remover_tema("Tema para Remover")
        self.assertNotIn("Tema para Remover", obter_temas(), msg='O tema deveria ter sido removido.')

    def test_remover_tema_inexistente(self):
        """Teste para remover um tema que não existe."""
        inserir_tema("Tema Existente")
        remover_tema("Tema Inexistente")  # Tentativa de remoção de um tema que não foi adicionado
        self.assertIn("Tema Existente", obter_temas(), msg='O tema existente não deveria ser removido.')

    def test_obter_temas_vazio(self):
        """Teste para obter a lista de temas quando está vazia."""
        temas = obter_temas()
        self.assertEqual(temas, [], msg='A lista de temas deve estar vazia no início.')

    def test_validar_tema_valido(self):
        """Teste para validar um tema com menos de 150 caracteres."""
        self.assertTrue(validar_tema("Tema Válido"), msg='O tema deveria ser considerado válido.')

    def test_validar_tema_invalido(self):
        """Teste para validar um tema com mais de 150 caracteres."""
        self.assertFalse(validar_tema("Tema com mais de 150 caracteres" * 10), 
                         msg='O tema não deveria ser considerado válido.')

    def test_enviar_temas(self):
        """Teste para enviar uma lista de temas e receber um dicionário."""
        temas = ["Tema 1", "Tema 2"]
        resultado = enviar_temas(temas)
        self.assertEqual(resultado, {'temas': temas}, msg='O dicionário de temas criado não está correto.')

    def test_mensagem_feedback(self):
        """Teste para verificar a chamada de feedback para o usuário."""
        import streamlit as st
        
        with st.empty():  # Simula a exibição de mensagem no Streamlit
            mensagem_feedback("Teste de Mensagem")
            output = st.session_state.get('feedback', None)
            self.assertIsNotNone(output, msg='Deveria haver uma mensagem de feedback exibida.')

if __name__ == '__main__':
    unittest.main()
```

### Descrição do Script de Teste
O arquivo `teste_codigo.py` implementa uma série de testes unitários para validar o comportamento das funções desenvolvidas para a aplicação Streamlit que gerencia temas para postagens em blogs. 

#### Estrutura dos Testes:
- **setUp()**: Limpa o estado da sessão do Streamlit antes de cada teste, para garantir que cada teste comece com um estado limpo.
- **test_inserir_tema_valido e test_inserir_tema_invalido**: Validam a inserção de temas válidos e a rejeição de temas inválidos, verificando se os temas foram realmente adicionados ou não.
- **test_remover_tema_existente e test_remover_tema_inexistente**: Testam a remoção de temas, tanto quando existe quanto quando não existe, comprovando se o estado da sessão reflete as operações corretamente.
- **test_obter_temas_vazio**: Confirma que a lista de temas começa vazia.
- **test_validar_tema_valido e test_validar_tema_invalido**: Asseguram que a validação de temas está funcionando como esperado, permitindo apenas temas válidos.
- **test_enviar_temas**: Verifica se a função que envia os temas retorna um dicionário estruturado corretamente.
- **test_mensagem_feedback**: Confirma se a mensagem de feedback é registrada corretamente no estado do Streamlit.

### Execução dos Testes
Os testes podem ser executados usando o comando:
```bash
python -m unittest teste_codigo.py
```

A expectativa é que todos os testes sejam bem-sucedidos, demonstrando que as funções implementadas se comportam conforme o esperado. Isso garante a robustez da aplicação e a confiança nas funcionalidades que foram desenvolvidas.