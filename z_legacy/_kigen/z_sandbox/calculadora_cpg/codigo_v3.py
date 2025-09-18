```python
import openai

def calcular_receita_liquida(receita_bruta: float, impostos: float) -> float:
    """
    Calcula a receita líquida subtraindo os impostos da receita bruta.
    
    Parâmetros:
    receita_bruta (float): A receita total antes de impostos.
    impostos (float): O valor total dos impostos a serem subtraídos.

    Retorno:
    float: A receita líquida após a subtração dos impostos.

    Exemplo de uso:
    >>> calcular_receita_liquida(10000, 2000)
    8000.0
    """
    return receita_bruta - impostos

def calcular_cmv(custo_produto: float, frete: float, embalagem: float) -> float:
    """
    Calcula o Custo da Mercadoria Vendida (CMV) somando o custo do produto, frete e embalagem.
    
    Parâmetros:
    custo_produto (float): O custo do produto.
    frete (float): O custo do frete.
    embalagem (float): O custo da embalagem.

    Retorno:
    float: O total do CMV.

    Exemplo de uso:
    >>> calcular_cmv(100, 10, 5)
    115.0
    """
    return custo_produto + frete + embalagem

def calcular_margem_bruta(receita_liquida: float, cmv: float) -> float:
    """
    Calcula a margem bruta subtraindo o CMV da receita líquida.
    
    Parâmetros:
    receita_liquida (float): Receita líquida total.
    cmv (float): Custo da Mercadoria Vendida.

    Retorno:
    float: A margem bruta calculada.

    Exemplo de uso:
    >>> calcular_margem_bruta(8000, 115)
    7885.0
    """
    return receita_liquida - cmv

def calcular_despesas_variaveis(despesas_vendas: float, despesas_marketing: float, despesas_sistemas: float) -> float:
    """
    Soma todas as despesas variáveis.
    
    Parâmetros:
    despesas_vendas (float): Despesas de vendas.
    despesas_marketing (float): Despesas de marketing.
    despesas_sistemas (float): Despesas de sistemas.

    Retorno:
    float: O total das despesas variáveis.

    Exemplo de uso:
    >>> calcular_despesas_variaveis(300, 200, 100)
    600.0
    """
    return despesas_vendas + despesas_marketing + despesas_sistemas

def calcular_margem_contribuicao(margem_bruta: float, despesas_variaveis: float) -> float:
    """
    Calcula a margem de contribuição subtraindo as despesas variáveis da margem bruta.
    
    Parâmetros:
    margem_bruta (float): A margem bruta.
    despesas_variaveis (float): O total das despesas variáveis.

    Retorno:
    float: A margem de contribuição.

    Exemplo de uso:
    >>> calcular_margem_contribuicao(7885, 600)
    7285.0
    """
    return margem_bruta - despesas_variaveis

def classificar_despesa(despesa: str) -> (str, str):
    """
    Classifica a despesa em um grupo e fornece uma justificativa usando LLM.
    
    Parâmetros:
    despesa (str): A descrição da despesa a ser classificada.

    Retorno:
    tuple: O grupo da despesa e a justificativa para a classificação.

    Exemplo de uso:
    >>> classificar_despesa("Compra de papel")
    ('Material de Escritório', 'Classificação baseada em compra de suprimentos.')
    """
    try:
        resultado = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Classifique a despesa: {despesa}"}]
        )
        resposta = resultado.choices[0].message['content'].strip().split('|')
        return resposta[0].strip(), resposta[1].strip() if len(resposta) > 1 else "Sem justificativa"
    except Exception as e:
        raise Exception(f"❌ Erro na função classificar_despesa: {str(e)}")

def interpretar_comando(comando: str) -> str:
    """
    Interpreta comandos em linguagem natural e executa ações correspondentes.
    
    Parâmetros:
    comando (str): O comando a ser interpretado.

    Retorno:
    str: A resposta interpretada.

    Exemplo de uso:
    >>> interpretar_comando("Quero saber minha margem de contribuição")
    'Interpretação: Consulta de margem de contribuição solicitada.'
    """
    try:
        resultado = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Interprete o comando: {comando}"}]
        )
        return resultado.choices[0].message['content']
    except Exception as e:
        raise Exception(f"❌ Erro na função interpretar_comando: {str(e)}")

def main():
    receita_liquida = None
    cmv = None
    margem_bruta = None
    despesas_variaveis = None
    margem_contribuicao = None

    try:
        # Exemplo de uso das funções
        receita_bruta = 10000
        impostos = 2000
        receita_liquida = calcular_receita_liquida(receita_bruta, impostos)
        print(f"Receita Líquida: {receita_liquida}")

    except Exception as e:
        print(f"❌ Erro na função calcular_receita_liquida: {e}")

    try:
        if receita_liquida is not None:
            custo_produto = 100
            frete = 10
            embalagem = 5
            cmv = calcular_cmv(custo_produto, frete, embalagem)
            print(f"CMV: {cmv}")

    except Exception as e:
        print(f"❌ Erro na função calcular_cmv: {e}")

    try:
        if receita_liquida is not None and cmv is not None:
            margem_bruta = calcular_margem_bruta(receita_liquida, cmv)
            print(f"Margem Bruta: {margem_bruta}")

    except Exception as e:
        print(f"❌ Erro na função calcular_margem_bruta: {e}")

    try:
        if margem_bruta is not None:
            despesas_vendas = 300
            despesas_marketing = 200
            despesas_sistemas = 100
            despesas_variaveis = calcular_despesas_variaveis(despesas_vendas, despesas_marketing, despesas_sistemas)
            print(f"Despesas Variáveis: {despesas_variaveis}")

    except Exception as e:
        print(f"❌ Erro na função calcular_despesas_variaveis: {e}")

    try:
        if margem_bruta is not None and despesas_variaveis is not None:
            margem_contribuicao = calcular_margem_contribuicao(margem_bruta, despesas_variaveis)
            print(f"Margem de Contribuição: {margem_contribuicao}")

    except Exception as e:
        print(f"❌ Erro na função calcular_margem_contribuicao: {e}")

    try:
        despesa = "Compra de papel"
        grupo, justificativa = classificar_despesa(despesa)
        print(f"Grupo: {grupo}, Justificativa: {justificativa}")

    except Exception as e:
        print(f"❌ Erro na função classificar_despesa: {e}")

    try:
        comando = "Quero saber minha margem de contribuição"
        resposta = interpretar_comando(comando)
        print(f"Resposta: {resposta}")

    except Exception as e:
        print(f"❌ Erro na função interpretar_comando: {e}")

if __name__ == "__main__":
    main()
```