import os
from dotenv import load_dotenv
import ollama
from tools import (
    get_pdf_metadata, 
    replace_text_in_pdf, 
    merge_pdfs, 
    split_pdf, 
    rotate_pdf_pages, 
    remove_pdf_pages,
    ocr_pdf
)

# Load environment variables from .env file
load_dotenv()

def run_agent(prompt: str, filepath: str) -> str:
    """Runs the ReAct loop using local Gemma via Ollama to edit the PDF."""
    print(f"Starting agent with file: {filepath}")
    
    # Model name - using 'gemma4:e2b' based on your available local models
    MODEL_NAME = "gemma4:e2b" 
    
    messages = [
        {
            'role': 'user', 
            'content': (
                f"Target PDF File: {filepath}\n"
                f"User Request: {prompt}\n\n"
                "RULES:\n"
                "1. You CANNOT change text without knowing the exact existing text currently in the PDF.\n"
                "2. You MUST use 'get_pdf_metadata' FIRST to inspect the PDF and find the exact old text/date/name.\n"
                "3. Once you have the old text, you MUST use 'replace_text_in_pdf' to perform the change.\n"
                "4. Use 'merge_pdfs', 'split_pdf', 'rotate_pdf_pages', 'remove_pdf_pages', or 'ocr_pdf' for specialized operations."
            )
        }
    ]
    
    # Define tools for Ollama
    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'get_pdf_metadata',
                'description': 'Inspects the PDF (page count, text) to understand context before editing.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'The path to the PDF file.'}
                    },
                    'required': ['filepath']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'replace_text_in_pdf',
                'description': 'MANDATORY: You MUST use this tool to change, replace, or update ANY text, names, dates, or numbers in the PDF.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'Path to the PDF file.'},
                        'old_text': {'type': 'string', 'description': 'The exact text to find and replace.'},
                        'new_text': {'type': 'string', 'description': 'The new text to insert.'},
                        'fontname': {'type': 'string', 'description': 'PDF standard font name (default: helv).'},
                        'fontsize': {'type': 'integer', 'description': 'Size of the inserted text (default: 11).'}
                    },
                    'required': ['filepath', 'old_text', 'new_text']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'merge_pdfs',
                'description': 'Merges multiple PDF files into a single PDF.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepaths': {
                            'type': 'array', 
                            'items': {'type': 'string'},
                            'description': 'List of paths to PDF files to merge.'
                        },
                        'output_filename': {'type': 'string', 'description': 'Name for the resulting merged PDF.'}
                    },
                    'required': ['filepaths', 'output_filename']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'split_pdf',
                'description': 'Splits a PDF by extracting specific page ranges into a new file.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'Path to the PDF file.'},
                        'page_ranges': {'type': 'string', 'description': "String representing page ranges (e.g., '1-3, 5, 8-10')."}
                    },
                    'required': ['filepath', 'page_ranges']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'rotate_pdf_pages',
                'description': 'Rotates specific pages in a PDF.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'Path to the PDF file.'},
                        'page_ranges': {'type': 'string', 'description': "String representing page ranges (e.g., '1-3, 5'). Use 'all' for all pages."},
                        'rotation': {'type': 'integer', 'description': 'Degrees to rotate (multiple of 90, e.g., 90, 180, 270).'}
                    },
                    'required': ['filepath', 'page_ranges', 'rotation']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'remove_pdf_pages',
                'description': 'Removes specific pages from a PDF.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'Path to the PDF file.'},
                        'page_ranges': {'type': 'string', 'description': "String representing page ranges to REMOVE (e.g., '2, 4-6')."}
                    },
                    'required': ['filepath', 'page_ranges']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'ocr_pdf',
                'description': 'Performs OCR on an image-based PDF to make it searchable and editable.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'Path to the PDF file.'},
                        'language': {'type': 'string', 'description': "Tesseract language code (default: 'eng')."}
                    },
                    'required': ['filepath']
                }
            }
        }
    ]
    
    available_functions = {
        'get_pdf_metadata': get_pdf_metadata,
        'replace_text_in_pdf': replace_text_in_pdf,
        'merge_pdfs': merge_pdfs,
        'split_pdf': split_pdf,
        'rotate_pdf_pages': rotate_pdf_pages,
        'remove_pdf_pages': remove_pdf_pages,
        'ocr_pdf': ocr_pdf,
    }
    
    try:
        # ReAct loop: Limit to 10 iterations to prevent infinite loops
        for i in range(10):
            response = ollama.chat(
                model=MODEL_NAME, 
                messages=messages, 
                tools=tools,
                options={'temperature': 0}
            )
            
            # Add assistant response to history
            messages.append(response['message'])
            
            # If there's no tool call, we're done
            if not response['message'].get('tool_calls'):
                return response['message'].get('content', 'Agent finished execution.')
            
            # Process tool calls
            for tool in response['message']['tool_calls']:
                function_name = tool['function']['name']
                function_args = tool['function']['arguments']
                
                print(f"Iteration {i+1}: Agent calling tool: {function_name}({function_args})")
                
                if function_name in available_functions:
                    result = available_functions[function_name](**function_args)
                    messages.append({
                        'role': 'tool',
                        'content': str(result)
                    })
                else:
                    messages.append({
                        'role': 'tool',
                        'content': f"Error: Tool '{function_name}' not found."
                    })
        
        return "Agent stopped: Max iterations (10) reached."
                    
    except Exception as e:
        return f"Agent error: {str(e)}"
