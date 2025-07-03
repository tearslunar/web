from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO

def extract_text_with_pdfminer(pdf_path, output_txt_path=None):
    laparams = LAParams()  # 레이아웃 분석 파라미터 (기본값 사용 가능)
    output_string = StringIO()

    with open(pdf_path, 'rb') as f:
        extract_text_to_fp(f, output_string, laparams=laparams, output_type='text', codec=None)

    full_text = output_string.getvalue()

    if output_txt_path:
        with open(output_txt_path, 'w', encoding='utf-8') as out_file:
            out_file.write(full_text)
        print(f"[완료] '{output_txt_path}'에 텍스트 저장 완료.")

    return full_text


if __name__ == "__main__":
    pdf_path = "/Users/differz/Desktop/web/약관.pdf"  # 실제 경로로 변경
    output_path = "/Users/differz/Desktop/web/result/약관.txt"  # 결과 저장 경로
    text = extract_text_with_pdfminer(pdf_path, output_path)
    print("[INFO] PDFMiner로 텍스트 추출 완료.")
