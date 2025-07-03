from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from pathlib import Path

def extract_text_by_page(pdf_path):
    laparams = LAParams()
    resource_manager = PDFResourceManager()
    full_text = ""

    with open(pdf_path, 'rb') as f:
        for i, page in enumerate(PDFPage.get_pages(f)):
            output_string = StringIO()
            device = TextConverter(resource_manager, output_string, laparams=laparams)
            interpreter = PDFPageInterpreter(resource_manager, device)

            interpreter.process_page(page)
            page_text = output_string.getvalue()
            output_string.close()
            device.close()

            full_text += f"\n\n--- Page {i+1} ---\n{page_text.strip()}"

    return full_text

def save_text_with_same_name_as_pdf(pdf_path, text):
    pdf_file = Path(pdf_path)
    txt_filename = pdf_file.stem + ".txt"
    output_path = pdf_file.with_name(txt_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"[완료] '{output_path}'에 텍스트 저장 완료.")

if __name__ == "__main__":
    pdf_path = "/Users/differz/Desktop/web/result/약관.pdf"  # 예시 경로
    extracted_text = extract_text_by_page(pdf_path)
    save_text_with_same_name_as_pdf(pdf_path, extracted_text)
    print("[INFO] PDFMiner로 페이지별 텍스트 추출 및 저장 완료.")
