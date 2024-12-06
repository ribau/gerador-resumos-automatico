import os
import spacy
from collections import Counter
import heapq
import PyPDF2
from fpdf import FPDF
from tkinter import Tk, filedialog

# Carregar o modelo do spaCy para português
nlp = spacy.load('pt_core_news_sm')

# Função para identificar palavras-chave
def extract_keywords(text, top_n=10):
    doc = nlp(text)
    # Selecionar apenas palavras substantivas e adjetivas
    keywords = [token.text.lower() for token in doc if token.pos_ in ('NOUN', 'ADJ') and token.is_alpha]
    # Calcular frequência das palavras e selecionar as principais
    keyword_freq = Counter(keywords).most_common(top_n)
    return {word for word, _ in keyword_freq}  # Retorna apenas as palavras-chave

# Resumir texto
def summarize_text(text, num_sentences=3):
    # Processar o texto com spaCy
    doc = nlp(text)
    
    # Identificar palavras-chave
    keywords = extract_keywords(text, top_n=10)
    
    # Tokenizar em sentenças
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
    
    # Calcular pontuação das sentenças com base nas palavras-chave
    sentence_scores = {}
    for sentence in sentences:
        sentence_length = len(sentence.split())
        score = 0
        for word in sentence.split():
            word_lower = word.lower()
            if word_lower in keywords:
                score += 1  # Incrementa o peso para palavras-chave
        # Penalizar sentenças muito longas
        if sentence_length > 20:  # Ajuste conforme necessário
            score *= 0.8
        sentence_scores[sentence] = score

    # Selecionar as melhores sentenças
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

# Ler texto de PDF
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

# Salvar resumo em um arquivo TXT
def save_to_txt(summary, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(summary)

# Salvar resumo em um arquivo PDF
def save_to_pdf(summary, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    pdf.output(output_path)

# Seleção de arquivo
def select_file():
    root = Tk()
    root.withdraw()  # Ocultar janela principal do Tkinter
    file_path = filedialog.askopenfilename(title="Selecione um arquivo", 
                                           filetypes=[("PDF e Texto", "*.pdf *.txt")])
    return file_path

# Função principal
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
    summary = summarize_text(text, num_sentences=3)  # Ajuste o número de sentenças conforme necessário
    print("Resumo gerado com sucesso!")

    # Criar pasta para salvar os arquivos, se não existir
    output_folder = "resumos"
    os.makedirs(output_folder, exist_ok=True)

    # Salvar o resumo em TXT
    txt_path = os.path.join(output_folder, "resumo.txt")
    save_to_txt(summary, txt_path)
    print(f"Resumo salvo em: {txt_path}")

    # Salvar o resumo em PDF
    pdf_path = os.path.join(output_folder, "resumo.pdf")
    save_to_pdf(summary, pdf_path)
    print(f"Resumo salvo em: {pdf_path}")

if __name__ == "__main__":
    main()
