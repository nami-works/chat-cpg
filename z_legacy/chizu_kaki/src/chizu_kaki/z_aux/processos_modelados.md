# Documento Estruturado da Crew ChizuKaki

## 🎯 Objetivo
A Crew ChizuKaki foi criada para realizar a avaliação da proximidade entre os endereços dos clientes, identificados por seus CEPs, e uma lista fixa de shoppings. Este processo envolve várias etapas que devem ser cuidadosamente estruturadas e automatizadas para garantir eficiência, precisão e escalabilidade.

---

## 🛠️ Estrutura do Processo

### 1. Coleta de Dados
#### Subprocessos:
- **Input de CEPs dos Shoppings**
  - Criar um dicionário fixo no código com os nomes dos shoppings e seus respectivos CEPs.
  
- **Input de Base de CEPs**
  - Solicitar ao usuário um arquivo CSV contendo uma coluna `cep`.

### 2. Validação de Dados
#### Subprocessos:
- **Validação do Dicionário de Shoppings**
  - Garantir que o dicionário `ceps_shoppings` esteja no formato correto (chave: nome do shopping, valor: CEP) e que os CEPs atendam ao formato esperado (8 dígitos numéricos).

- **Validação do Arquivo CSV**
  - Ler o arquivo CSV e verificar se a coluna `cep` está presente e se todos os CEPs são válidos (string de 8 dígitos).

### 3. Conversão de CEPs para Coordenadas Geográficas
#### Subprocessos:
- **Utilização de API de Geocodificação**
  - Consultar uma API externa (ex: ViaCEP) para converter os CEPs em coordenadas geográficas (latitude, longitude).

### 4. Cálculo de Distâncias
#### Subprocessos:
- **Cálculo de Distâncias Geodésicas**
  - Utilizar a biblioteca `geopy` para calcular a distância entre as coordenadas dos CEPs e dos shoppings.
  
### 5. Identificação do Shopping mais Próximo
#### Subprocessos:
- **Análise de Distâncias**
  - Determinar o shopping mais próximo para cada CEP e verificar se existe um shopping dentro de um raio de 15 km. Caso contrário, a saída será `N/A`.

### 6. Geração de Relatório
#### Subprocessos:
- **Criação do Arquivo CSV de Resultados**
  - Gerar um arquivo CSV (`ceps_distancias.csv`) contendo:
    - CEP da base
    - Nome do shopping mais próximo (ou `N/A`)
    - Distância calculada (em km, com duas casas decimais)

---

## 🤝 Interações e Colaboração
- **Feedback do Usuário**
  - Receber o arquivo CSV com CEPs do usuário e garantir a comunicação clara sobre o formato e conteúdo necessário para a validação.
  
- **Revisão do Processo**
  - Colaborar com a equipe para revisar os resultados e fazer ajustes no dicionário de shoppings e nos parâmetros de geocodificação conforme necessário.

---

## ⚙️ Dependências e Ferramentas Necessárias
- **Bibliotecas Python**
  - `pandas`: Para manipulação e análise de dados.
  - `geopy`: Para cálculos geodésicos e conversão de coordenadas.
  
- **APIs e Documentação**
  - API de Geocodificação (ViaCEP ou outra) - documentação acessada para integração.
  
- **Repositórios e Exemplos**
  - Referências de repositórios do GitHub e StackOverflow para exemplos práticos.

---

## 📈 Oportunidades de Modularização
- **Módulos de Validação**
  - Criar funções de validação reutilizáveis para diferentes tipos de entrada (CEP e dicionário de shoppings).

- **Módulos de Cálculo**
  - Isolar a lógica de cálculo de distâncias em módulos independentes que podem ser testados e atualizados facilmente.

- **Módulos de Exportação**
  - Estruturar a geração de relatórios como um subprocesso independente que pode ser invocado após o cálculo de distâncias.

---

## 📝 Sugestões de Automação
1. **Automação da Coleta de Dados**
   - Implementar uma interface simples para que o usuário carregue o arquivo CSV diretamente em um sistema web ou script python.
   
2. **Automação da Validação**
   - Rotinas automatizadas que assegurem que todos os dados inseridos sejam aprimorados em qualidade antes de prosseguir para as etapas seguintes.

3. **Relatórios Automatizados**
   - Gerar relatórios em intervalos-regulares de acordo com auditorias comerciais ou marketing que podem ser ajustados conforme as necessidades do vendedor.

4. **Integração Contínua**
   - Configurar um pipeline CI/CD para implementar automaticamente testes de validação e geração de relatórios a cada nova versão do código.

---

## 📋 Resumo das Ações Necessárias
1. **Solicitação do CSV de entrada** ao usuário.
2. **Implementar validações** para garantir a integridade dos dados.
3. **Integrar API de geocodificação** e calcular distâncias utilizando a biblioteca `geopy`.
4. **Gerar e armazenar** o relatório de resultados formatado conforme especificado.

---

Com esse modelo estruturado e as etapas bem definidas, a Crew ChizuKaki está pronta para implementar uma solução automatizada que atenda aos objetivos propostos com eficácia e eficiência. Cada etapa do processo foi decomposta em subprocessos e interações claras, permitindo a escalabilidade e manutenção fácil no futuro.