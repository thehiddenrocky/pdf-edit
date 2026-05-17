import os
import json
from dotenv import load_dotenv
from llama_cpp import Llama
from model_downloader import get_model_path
from tools import get_pdf_metadata, apply_pdf_edits, replace_text_in_pdf

# Load environment variables from .env file
load_dotenv()

def run_agent(prompt: str, filepath: str) -> str:
    """Runs the ReAct loop using local Gemma via llama-cpp-python to edit the PDF."""
    print(f"Starting agent with file: {filepath}")
    
    # Get local model path (downloads if missing)
    model_path = get_model_path()
    if not model_path:
        return "Agent error: Could not locate or download the AI model."

    # Instantiate Llama with Metal support (n_gpu_layers=-1)
    llm = Llama(
        model_path=model_path,
        n_gpu_layers=-1,
        n_ctx=4096,
        chat_format="chatml-function-calling"
    )
    
    messages = [
        {
            'role': 'user', 
            'content': (
                f"Target PDF File: {filepath}\n"
                f"User Request: {prompt}\n\n"
                "RULES:\n"
                "1. You CANNOT change text without knowing the exact existing text currently in the PDF.\n"
                "2. You MUST use 'get_pdf_metadata' FIRST to inspect the PDF and find the exact old text/date/name.\n"
                "3. Once you receive the tool's response, read it carefully. DO NOT call the same tool again if you already have the answer.\n"
                "4. Once you have the old text from the metadata, you MUST use 'replace_text_in_pdf' to perform the change.\n"
                "5. NEVER use 'apply_pdf_edits' for changing text, names, or dates. It is for page operations only.\n"
                "6. IMPORTANT: Once 'replace_text_in_pdf' returns a 'Success' message, YOUR JOB IS DONE. Do NOT call any more tools. Immediately return a final response to the user containing the path to the new file."
            )
        }
    ]
    
    # Define tools in OpenAI-compatible format
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
                'description': 'MANDATORY: You MUST use this tool to change, replace, or update ANY text, names, dates, or numbers in the PDF. DO NOT use apply_pdf_edits for text changes.',
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
                'name': 'apply_pdf_edits',
                'description': 'Use this ONLY for page-level operations like merging, splitting, or rotating. WARNING: This tool CANNOT change text, dates, or names.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filepath': {'type': 'string', 'description': 'The path to the PDF file to edit.'},
                        'edit_instructions': {'type': 'string', 'description': 'Natural language instructions for what needs to be edited.'}
                    },
                    'required': ['filepath', 'edit_instructions']
                }
            }
        }
    ]
    
    available_functions = {
        'get_pdf_metadata': get_pdf_metadata,
        'replace_text_in_pdf': replace_text_in_pdf,
        'apply_pdf_edits': apply_pdf_edits,
    }
    
    try:
        # ReAct loop: Limit to 10 iterations to prevent infinite loops
        for i in range(10):
            # Debug: print messages
            print(f"\n--- DEBUG: Iteration {i+1}, Message Count: {len(messages)} ---")
            for idx, m in enumerate(messages):
                content_preview = (m.get('content') or '')[:100].replace('\n', ' ')
                tool_calls = m.get('tool_calls', [])
                tc_info = f" [TC: {len(tool_calls)}]" if tool_calls else ""
                print(f"  {idx}: Role: {m['role']}{tc_info}, Content: {content_preview}...")
            
            response = llm.create_chat_completion(
                messages=messages, 
                tools=tools,
                tool_choice="auto",
                temperature=0
            )
            
            if not response or 'choices' not in response or len(response['choices']) == 0:
                print(f"Error: AI returned empty response: {response}")
                return "Agent error: AI returned empty response."

            assistant_message = response['choices'][0]['message']
            
            # Add assistant response to history
            messages.append(assistant_message)
            
            # If there's no tool call, we're done
            if not assistant_message.get('tool_calls'):
                return assistant_message.get('content', 'Agent finished execution.')
            
            # Process tool calls
            for tool in assistant_message['tool_calls']:
                function_name = tool['function']['name']
                # Arguments might be a string (OpenAI format) or dict
                function_args = tool['function']['arguments']
                if isinstance(function_args, str):
                    function_args = json.loads(function_args)
                
                print(f"Iteration {i+1}: Agent calling tool: {function_name}({function_args})")
                
                if function_name in available_functions:
                    result = available_functions[function_name](**function_args)
                    content_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                    # Use 'user' role but wrap in a clear Observation/Thought structure to force the AI to respond.
                    messages.append({
                        'role': 'user',
                        'content': f"OBSERVATION: Tool '{function_name}' returned: {content_str}\n\nTHOUGHT: I have the result. I will now provide the final response to the human user."
                    })
                else:
                    messages.append({
                        'role': 'user',
                        'content': f"Tool Error: Tool '{function_name}' not found."
                    })
        
        return "Agent stopped: Max iterations (10) reached."
                    
    except Exception as e:
        return f"Agent error: {str(e)}"
