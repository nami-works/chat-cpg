import os
import locale
import yaml
import sys
from pathlib import Path

import streamlit as st

from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Import centralized translations
from translations import LANG

# Import CRM Lab context
from chats.crm_lab.context import CRM_LAB_CONTEXT

load_dotenv()

def handle_crm_lab_flow(chat_interaction, chain, memory):
    """
    Main CRM Lab flow handler - uses default chat interface.
    """
    # Use default chat interface - no manual context display needed
    # The AI will handle the welcome message and conversation naturally
    # Users can ask about RFM personalization, email briefings, or any CRM topics
    # and the system will respond based on the CRM Lab guidelines 