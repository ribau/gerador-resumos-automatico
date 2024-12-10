import os
import spacy
from collections import Counter
import heapq
import PyPDF2
from fpdf import FPDF
from tkinter import Tk, filedialog


nlp = spacy.load('pt_core_news_sm')


def extract_keywords(text, top_n=10):
    doc = nlp(text)

    keywords = [token.text.lower() for token in doc if token.pos_ in ('NOUN', 'ADJ') and token.is_alpha]

    keyword_freq = Counter(keywords).most_common(top_n)
    return {word for word, _ in keyword_freq}  


def summarize_text(text, num_sentences=3):
    
    doc = nlp(text)
    

    keywords = extract_keywords(text, top_n=10)
    

    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
    

    sentence_scores = {}
    for sentence in sentences:
        sentence_length = len(sentence.split())
        score = 0
        for word in sentence.split():
            word_lower = word.lower()
            if word_lower in keywords:
                score += 1  
        if sentence_length > 20:  
            score *= 0.8
        sentence_scores[sentence] = score

    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
    return text

def save_to_txt(summary, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(summary)

def save_to_pdf(summary, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    pdf.output(output_path)

def select_file():
    root = Tk()
    root.withdraw()  
    file_path = filedialog.askopenfilename(title="Selecione um arquivo", 
                                           filetypes=[("PDF e Texto", "*.pdf *.txt")])
    return file_path

def main():
    print("=== Gerador de Resumos Automático ===")
    print("Abrindo janela para selecionar o arquivo...")
    file_path = select_file()
    
    if not file_path:
        print("Nenhum arquivo selecionado. Encerrando.")
        return

    print(f"Arquivo selecionado: {file_path}")

    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

    print("\nGerando resumo...")
    summary = summarize_text(text, num_sentences=3)  
    print("Resumo gerado com sucesso!")

    
    output_folder = "resumos"
    os.makedirs(output_folder, exist_ok=True)

    
    txt_path = os.path.join(output_folder, "resumo.txt")
    save_to_txt(summary, txt_path)
    print(f"Resumo salvo em: {txt_path}")

    
    pdf_path = os.path.join(output_folder, "resumo.pdf")
    save_to_pdf(summary, pdf_path)
    print(f"Resumo salvo em: {pdf_path}")

if __name__ == "__main__":
    main()
