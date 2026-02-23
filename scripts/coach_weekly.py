import os
import google.generativeai as genai

def main():
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    print("Listing available models...\n")

    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(model.name)

if __name__ == "__main__":
    main()