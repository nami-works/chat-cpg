# _distanciador_

## 🗺️ Problema: descobrir o shopping mais próximo

### 🎯 Objetivo

Solucionar um problema de avaliação da **proximidade entre uma base de CEPs (endereços de clientes)** e uma lista fixa de shoppings, com o objetivo de:

- Converter todos os CEPs em **coordenadas geográficas (latitude, longitude)**;
- Calcular a **distância geodésica** entre cada CEP e todos os shoppings;
- Gerar um **relatório estruturado** com as distâncias para cada shopping, com os CEPs da base em cada linha e os shoppings nas colunas.

---

### 🧾 Entradas

- `ceps_shoppings`: Dicionário com nomes dos shoppings e seus respectivos CEPs (fixo no código)
- `base_ceps`: Arquivo CSV com uma coluna `cep` contendo os CEPs dos clientes

---

### 📤 Saídas

- Arquivo CSV (`ceps_distancias.csv`) contendo:
  - CEP da base
  - Nome do shopping mais próximo (ou `N/A`)
  - Distância calculada (em km, com duas casas decimais)

---

### 🧠 Aplicações

- Logística e roteirização
- Marketing geográfico
- Planejamento de expansão de redes varejistas
- Recomendação personalizada por localização
- Análise territorial urbana

---

