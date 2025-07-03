# Dynamic Context Enhancement for ChatCPG

## Overview

The ChatCPG codebase has been enhanced to present dynamic context based on the function selected in the sidebar menu. Instead of showing a generic hardcoded welcome message, the system now displays appropriate context for each specific function.

## What Was Changed

### 1. Added Function-Specific Context Configuration

A new `FUNCTION_CONTEXTS` dictionary was added to `chat_cpg.py` that defines the specific context for each system:

```python
FUNCTION_CONTEXTS = {
    'redacao': {
        'title': '🦊 ChatCPG - Redação',
        'subtitle': 'Bem-vindo ao sistema de Redação da GE Beauty!',
        'description': """
        O ChatCPG Redação é seu assistente especializado para criar conteúdo no tom de voz GE Beauty!
        Aqui você pode:
        • Gerar temas e briefings para blog posts
        • Criar mensagens personalizadas baseadas em RFM
        • Desenvolver campanhas de email marketing
        • Adaptar conteúdo para diferentes canais
        
        Vamos começar? 💛
        """,
        'icon': '✍️'
    },
    'oraculo': {
        'title': '🦊 ChatCPG - Oráculo',
        'subtitle': 'Bem-vindo ao Oráculo da GE Beauty!',
        'description': """
        O ChatCPG Oráculo é seu assistente inteligente para consultar a base de conhecimento!
        Aqui você pode:
        • Pesquisar informações específicas da empresa
        • Obter respostas rápidas e precisas
        • Consultar documentos e políticas
        • Acessar dados históricos e relatórios
        
        Como posso ajudá-lo hoje? 🔍
        """,
        'icon': '🔮'
    }
}
```

### 2. Added Dynamic Context Function

A new `get_function_context()` function was created that returns the appropriate context based on the selected function:

```python
def get_function_context(function_id):
    """
    Get dynamic context based on selected function
    
    Args:
        function_id: The selected function identifier
        
    Returns:
        dict: Context information for the function
    """
    default_context = {
        'title': '🦊 ChatCPG',
        'subtitle': 'Bem-vindo ao ChatCPG da GE Beauty!',
        'description': """
        ChatCPG é seu assistente virtual para trabalhar com a GE Beauty! 
        Selecione uma função na barra lateral para começar. 💛
        """,
        'icon': '🦊'
    }
    
    return FUNCTION_CONTEXTS.get(function_id, default_context)
```

### 3. Modified Main Function

The `chat_cpg()` function was updated to use dynamic context instead of hardcoded text:

```python
def chat_cpg():
    chosen_function = st.session_state.get('chosen_function')
    
    # Get dynamic context based on selected function
    context_info = get_function_context(chosen_function)
    
    # Display dynamic header and content
    st.header(context_info['title'], divider='red')
    st.subheader(context_info['subtitle'])
    st.write(context_info['description'])
    
    # ... rest of the function remains the same
```

## How It Works

1. **Function Selection**: When a user selects a function in the sidebar, it sets `st.session_state['chosen_function']`
2. **Context Retrieval**: The `get_function_context()` function uses this selection to retrieve the appropriate context
3. **Dynamic Display**: The main interface displays the function-specific title, subtitle, and description
4. **Fallback**: If no function is selected or an unknown function is selected, it shows the default generic context

## Benefits

- **Better User Experience**: Users immediately understand what each system does
- **Clear Function Separation**: Each system has its own identity and purpose clearly communicated
- **Maintainability**: Adding new systems is straightforward and follows a consistent pattern
- **Extensibility**: New functions can be easily added without modifying core logic

## How to Add New Systems

To add a new system (e.g., 'analytics'), follow these steps:

### Step 1: Add to Available Functions

In `chat_cpg.py`, add your new function to the `available_functions` dictionary:

```python
available_functions = {
    'Redação CPG': 'redacao',
    'Oráculo CPG': 'oraculo',
    'Analytics CPG': 'analytics',  # New system
}
```

### Step 2: Add Context Configuration

Add the new system's context to the `FUNCTION_CONTEXTS` dictionary:

```python
FUNCTION_CONTEXTS = {
    # ... existing systems ...
    'analytics': {
        'title': '🦊 ChatCPG - Analytics',
        'subtitle': 'Bem-vindo ao sistema de Analytics da GE Beauty!',
        'description': """
        O ChatCPG Analytics é seu assistente para análise de dados e insights!
        Aqui você pode:
        • Analisar dados de vendas e performance
        • Gerar relatórios automatizados
        • Obter insights de comportamento do cliente
        • Criar dashboards personalizados
        
        Que análise você gostaria de fazer? 📊
        """,
        'icon': '📊'
    }
}
```

### Step 3: Create System Directory and Guidelines

1. Create a new directory: `analytics/`
2. Create guidelines file: `analytics/guidelines.md`
3. Implement the system logic: `analytics/analytics.py`

### Step 4: Add Flow Handler

In the main `chat_cpg()` function, add the new flow handler:

```python
def chat_cpg():
    # ... existing code ...
    
    if chosen_function == 'redacao':
        from redacao.redacao import handle_redacao_flow
        handle_redacao_flow(handle_chat_interaction, chain, memory)
    elif chosen_function == 'oraculo':
        from oraculo.oraculo import handle_oraculo_flow
        handle_oraculo_flow(handle_chat_interaction, chain, memory)
    elif chosen_function == 'analytics':  # New system
        from analytics.analytics import handle_analytics_flow
        handle_analytics_flow(handle_chat_interaction, chain, memory)
```

## Example: Current Systems

### Redação System
- **Purpose**: Content creation for GE Beauty
- **Features**: Blog posts, RFM personalization, email marketing
- **Icon**: ✍️
- **Focus**: Creative content generation

### Oráculo System  
- **Purpose**: Knowledge base consultation
- **Features**: Information search, document queries, data retrieval
- **Icon**: 🔮
- **Focus**: Information retrieval and assistance

## Future Considerations

- **Multi-language Support**: The context system can be extended to support multiple languages
- **User-specific Context**: Context could be personalized based on user roles or preferences
- **Dynamic Icons**: Icons could be loaded dynamically or customized per organization
- **Context Validation**: Add validation to ensure all required context fields are present

## Testing

The enhancement has been tested for:
- ✅ Syntax correctness
- ✅ Function selection handling
- ✅ Dynamic context switching
- ✅ Fallback to default context
- ✅ Backward compatibility

## Conclusion

This enhancement makes the ChatCPG system more user-friendly and maintainable while providing a clear framework for adding new systems in the future. The dynamic context immediately communicates the purpose and capabilities of each system to users.