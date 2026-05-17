import argparse
import json
from agent import run_agent

def main():
    parser = argparse.ArgumentParser(description="PDF Editing Agent Backend")
    parser.add_argument("prompt", type=str, help="The instruction for editing the PDF")
    parser.add_argument("filepath", type=str, help="Path to the PDF file")
    
    args = parser.parse_args()
    
    print(f"User prompt: {args.prompt}")
    result = run_agent(args.prompt, args.filepath)
    
    print("\n" + "="*30)
    print("      AGENT RESPONSE")
    print("="*30)
    print(f"Status:      {result['status'].upper()}")
    print(f"Output File: {result['output_file']}")
    print("-" * 30)
    print(f"Message:\n{result['message']}")
    print("="*30)

if __name__ == "__main__":
    main()
