# Nami SEO Lab Shopify App - Rules & Memories

## Project Rules

### File Management
- **All log files should be saved into the @z_enhancements folder** each time to keep the file structure clean
- **Whenever a new .py file is created to test a function, it must be erased after completing the test**
- **All UI text must go through translations.py**; avoid adding UI flows or animations unless explicitly requested
- **In editor phases, hide chat and keep only essential controls visible**

### UI/UX Guidelines
- **User prefers a minimal chat-based interface**; during editing phases, chat UI should be hidden entirely and only the editor be visible, with no animations
- **Ensure _nami.py skips rendering chat history when st.session_state['editor_phase_active'] is True**; only the editor appears
- **The project requires UI texts to be translated to English for English-speaking users**, in addition to Portuguese. These translations must be stored into translations.py on the root folder, and then imported to the files handling UI text

### Development Environment
- **The user always runs their projects in virtual environments** and expects Cursor to use the corresponding virtual environment for testing and to prevent installing additional packages to the system Python

## Key Memories

### Translation System
- All UI text must go through translations.py
- Avoid adding UI flows or animations unless explicitly requested
- In editor phases, hide chat and keep only essential controls visible
- UI texts must be translated to English for English-speaking users, in addition to Portuguese
- Translations must be stored in translations.py on the root folder

### File Organization
- All log files should be saved into the @z_enhancements folder each time to keep the file structure clean
- Test files (.py) must be erased after completing the test
- Maintain clean file structure and organization

### User Interface Preferences
- User prefers a minimal chat-based interface
- During editing phases, chat UI should be hidden entirely
- Only the editor should be visible during editing phases
- No animations unless explicitly requested
- Keep interface clean and focused

### Development Practices
- Always use virtual environments for Python projects
- Prevent installing additional packages to system Python
- Use corresponding virtual environment for testing
- Maintain clean development environment

## Project-Specific Rules

### Shopify App Development
- Use Shopify Polaris for UI consistency and accessibility
- Integrate Shopify App Bridge for smooth embedding within the Shopify admin
- Support custom actions and blocks at relevant points in the admin
- Adhere to Shopify's app design guidelines for performance, responsiveness, and user experience
- Include localization support
- Support customizable chat UI components if applicable
- Maintain persistent context for user interactions

### Content Generation
- Embed interaction with custom GPT model (via OpenAI API) directly in the UI
- Automate the processing of GPT-generated outputs to trigger the background CrewAI system internally
- Eliminate the need for manual copy-pasting
- Replace product injection from manual files with Shopify API calls to read the store's products
- Use Shopify's Admin API to inject blog post content based on the background system's output

### Testing and Deployment
- Test thoroughly in a development store
- Prepare the app for submission following Shopify's app structure and extension requirements
- Ensure the app supports custom actions and blocks at relevant points in the admin
- Maintain persistent context for user interactions

## Implementation Notes

### For Frontend Development
- All UI text must go through the translations system
- Use Shopify Polaris components for consistency
- Implement minimal, clean interfaces
- Hide chat UI during editing phases
- Support multi-language (English/Portuguese)

### For Backend Development
- Use virtual environments for all Python dependencies
- Implement proper error handling and logging
- Save logs to @z_enhancements folder
- Clean up test files after completion
- Maintain clean file structure

### For Integration
- Use Shopify Admin API for all store data
- Integrate OpenAI API for content generation
- Implement CrewAI system for background processing
- Ensure seamless admin embedding with App Bridge
- Support custom actions and blocks

---

**Note**: These rules and memories should be followed throughout the development process to maintain consistency and meet user preferences.



