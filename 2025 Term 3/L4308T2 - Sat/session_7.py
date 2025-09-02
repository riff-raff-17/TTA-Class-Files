import ollama
from pypdf import PdfReader

# Step 1: Load PDF
def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Step 2: Chunk text (so it's not too long)
def chunk_text(text, chunk_size=1000):
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

# Step 3: Ask Ollama a question about the text
def ask_ollama(context_chunks, question):
    # Combine chunks into one string for simplicity
    context = "\n".join(context_chunks)
    prompt = f"""
    You are a helpful assistant. Use the following text to answer the question.

    Text:
    {context}

    Question:
    {question}
    Answer in a short, clear sentence.
    """

    response = ollama.chat(model="llama3.2", messages=[
        {"role": "user", "content": prompt}
    ])

    return response["message"]["content"]

def main():
    pdf_text = load_pdf_text("sheetresume.pdf")
    chunks = chunk_text(pdf_text)

    print("PDF loaded. Ask me anything! Type 'quit' to quit.\n")

    while True:
        question = input("Your question: ")
        if question.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        print("Thinking...")
        answer = ask_ollama(chunks, question)
        print("Bot: ", answer)
        print()

if __name__ == "__main__":
    main()