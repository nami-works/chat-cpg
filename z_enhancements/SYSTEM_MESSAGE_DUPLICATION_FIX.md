# System Message Duplication Fix

## 🐛 **Issue Identified**

The first message for chat-enabled functions was being displayed twice in the Streamlit interface. This was happening because:

1. **First Display**: The system message was displayed when `not system_message_exists` was true
2. **Second Display**: The same system message was displayed again when looping through all messages in memory

## 🔍 **Root Cause Analysis**

### **Location**: `_nami.py` lines 1730-1750

The issue was in the chat-enabled functions logic:

```python
# First: Display system message if it doesn't exist
if not system_message_exists:
    system_message = st.chat_message('ai', avatar='🦊')
    system_message.markdown(context_info['description'])
    memory.chat_memory.add_ai_message(context_info['description'])

# Second: Display ALL messages from memory (including the one just added)
for message in memory.buffer_as_messages:
    chat = st.chat_message(message.type, avatar='👤' if message.type == 'human' else '🦊')
    chat.markdown(message.content)
```

### **Problem Flow**:
1. System message doesn't exist in memory
2. Display system message and add it to memory
3. Loop through all messages in memory (including the one just added)
4. Display the system message again

## ✅ **Solution Implemented**

### **Approach**: Track when system message is just added

Added a `system_message_just_added` flag to track when we've just added the system message to memory:

```python
# Track if we just added the system message
system_message_just_added = False

# When adding system message
if not system_message_exists:
    system_message = st.chat_message('ai', avatar='🦊')
    system_message.markdown(context_info['description'])
    memory.chat_memory.add_ai_message(context_info['description'])
    system_message_just_added = True  # Set flag

# When displaying messages, skip if we just added it
for message in memory.buffer_as_messages:
    if system_message_just_added and message.content == context_info['description'] and message.type == 'ai':
        continue  # Skip this message
    chat = st.chat_message(message.type, avatar='👤' if message.type == 'human' else '🦊')
    chat.markdown(message.content)
```

## 🎯 **Benefits**

- ✅ **Eliminates Duplication**: System message appears only once
- ✅ **Maintains Functionality**: All other messages still display correctly
- ✅ **Preserves Memory**: System message is still added to memory for future reference
- ✅ **Clean UX**: Users see a clean, non-duplicated interface

## 🧪 **Testing**

The fix ensures that:
1. System message displays once when first loading a chat-enabled function
2. Subsequent messages display normally
3. Memory still contains the system message for context
4. No other functionality is affected

## 📁 **Files Modified**

- **`_nami.py`**: Updated chat-enabled functions logic to prevent system message duplication

This fix resolves the issue shown in the screenshot where the assistant's description was appearing twice in the Streamlit interface. 