# UI Text Translation Guidelines

## 🚨 CRITICAL RULE: ALL UI TEXT MUST BE TRANSLATED

**NEVER** add hardcoded strings to the code. **ALWAYS** use the translation system.

## ✅ Required Process for Adding UI Text

### 1. **FIRST**: Add to `translations.py`
- Add the new key to both `'en_US'` and `'pt_BR'` sections
- Use descriptive, hierarchical key names
- Include emojis and formatting in the translation values

### 2. **SECOND**: Use `LANG[key]` in code
- Replace all hardcoded strings with `LANG['key_name']`
- Use the exact key name from translations.py

### 3. **THIRD**: Test both languages
- Verify the text appears correctly in both English and Portuguese
- Check that the translation key exists and is used properly

## 📋 Translation Key Naming Convention

### Format: `category_specific_description`
Examples:
- `next_step_button` ✅
- `moving_to_dictionary_generation` ✅
- `has_refined_themes` ✅
- `dictionaries_generated_success_debug` ✅

### Categories:
- `next_step_*` - Next button related
- `moving_to_*` - Phase transitions
- `has_*` - State indicators
- `*_debug` - Debug messages
- `*_error` - Error messages
- `*_success` - Success messages

## 🔍 Checklist Before Committing

### ✅ Translation File Updated
- [ ] New keys added to `translations.py`
- [ ] Both `'en_US'` and `'pt_BR'` sections updated
- [ ] Keys follow naming convention
- [ ] Values include proper formatting (emojis, etc.)

### ✅ Code Updated
- [ ] All hardcoded strings replaced with `LANG['key']`
- [ ] No hardcoded strings remain in the code
- [ ] Translation keys match exactly

### ✅ Testing
- [ ] Text appears correctly in English
- [ ] Text appears correctly in Portuguese
- [ ] No missing translation errors

## 🚫 Common Mistakes to Avoid

### ❌ DON'T:
```python
# WRONG - Hardcoded string
st.info("🔄 Next button clicked! Processing next step...")

# WRONG - Inconsistent key naming
st.info(LANG['next_button_clicked'])  # If key doesn't exist
```

### ✅ DO:
```python
# RIGHT - Use translation system
st.info(LANG['next_button_clicked'])
```

## 📝 Example of Proper Implementation

### 1. Add to `translations.py`:
```python
'en_US': {
    'next_button_clicked': '🔄 Next button clicked! Processing next step...',
    'moving_to_dictionary_generation': '📝 Moving to dictionary generation phase...',
},
'pt_BR': {
    'next_button_clicked': '🔄 Botão Avançar clicado! Processando próximo passo...',
    'moving_to_dictionary_generation': '📝 Movendo para fase de geração de dicionários...',
}
```

### 2. Use in code:
```python
st.info(LANG['next_button_clicked'])
st.info(LANG['moving_to_dictionary_generation'])
```

## 🔧 Quick Fix Commands

If you accidentally add hardcoded strings:

1. **Find hardcoded strings:**
   ```bash
   grep -r "st\." --include="*.py" | grep -E "info|success|error|warning"
   ```

2. **Add missing translations:**
   - Add keys to `translations.py`
   - Replace hardcoded strings with `LANG['key']`

3. **Verify all strings are translated:**
   ```bash
   grep -r "st\." --include="*.py" | grep -v "LANG\["
   ```

## 📚 Reference

- **Translation file**: `translations.py`
- **Import statement**: `from translations import LANG`
- **Usage**: `LANG['key_name']`

**Remember: Every UI text must be translatable!** 🌍 