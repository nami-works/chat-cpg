import os
import tempfile

from langchain_community.document_loaders import (WebBaseLoader,
                                                YoutubeLoader, 
                                                CSVLoader, 
                                                PyPDFLoader, 
                                                TextLoader,
                                                UnstructuredWordDocumentLoader,
                                                UnstructuredPowerPointLoader,
                                                UnstructuredExcelLoader,
                                                JSONLoader,
                                                UnstructuredMarkdownLoader)

def web_reader(url):
    reader = WebBaseLoader(url, raise_for_status=True)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def youtube_reader(video_id):
    reader = YoutubeLoader(video_id, add_video_info = False, language = ['pt'])
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def pdf_reader(pdf_path):
    reader = PyPDFLoader(pdf_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def csv_reader(csv_path):
    reader = CSVLoader(file_path = csv_path, encoding = 'utf-8')
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def text_reader(text_path):
    reader = TextLoader(text_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def word_reader(doc_path):
    reader = UnstructuredWordDocumentLoader(doc_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def powerpoint_reader(ppt_path):
    reader = UnstructuredPowerPointLoader(ppt_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def excel_reader(xlsx_path):
    reader = UnstructuredExcelLoader(xlsx_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def json_reader(json_path):
    reader = JSONLoader(json_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

def markdown_reader(md_path):
    reader = UnstructuredMarkdownLoader(md_path)
    document = reader.load()
    result = '\n\n'.join([content.page_content for content in document])
    return result

valid_inputs = ['site', 'youtube', 'pdf', 'csv', 'txt', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'json', 'md']

import os
import tempfile

def process_temp_file(input_file, suffix, reader_function):
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        temp.write(input_file.read())
        temp_name = temp.name
    return reader_function(temp_name)

def load_input(input_file, filename=None):
    if filename:
        _, extension = os.path.splitext(filename.lower())
    elif hasattr(input_file, 'name'):
        _, extension = os.path.splitext(input_file.name.lower())
    else:
        raise ValueError('Could not identify filename. Please provide "filename" parameter.')

    extension = extension.lstrip('.')  # remove dot, e.g.: '.pdf' -> 'pdf'

    function_map = {
        'pdf': lambda x: process_temp_file(x, '.pdf', pdf_reader),
        'csv': lambda x: process_temp_file(x, '.csv', csv_reader),
        'txt': lambda x: process_temp_file(x, '.txt', text_reader),
        'doc': lambda x: process_temp_file(x, '.doc', word_reader),
        'docx': lambda x: process_temp_file(x, '.docx', word_reader),
        'ppt': lambda x: process_temp_file(x, '.ppt', powerpoint_reader),
        'pptx': lambda x: process_temp_file(x, '.pptx', powerpoint_reader),
        'xls': lambda x: process_temp_file(x, '.xls', excel_reader),
        'xlsx': lambda x: process_temp_file(x, '.xlsx', excel_reader),
        'json': lambda x: process_temp_file(x, '.json', json_reader),
        'md': lambda x: process_temp_file(x, '.md', markdown_reader)
    }

    if extension not in function_map:
        raise ValueError(f'File type ".{extension}" not supported. Use one of: {list(function_map.keys())}')
    
    return function_map[extension](input_file)
