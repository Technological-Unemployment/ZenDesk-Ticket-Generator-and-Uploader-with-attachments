from PyPDF2 import PdfFileMerger
from pdf2image import convert_from_path
from PIL import Image
import os

def pdf_append(*pdfs):
    # ... (the merging logic)

def convert_pdf_to_png(filename):
    # ... (the conversion logic)

def concatenate_png_files(*png_files):
    # ... (the concatenation logic)

def cleanup_files(*filepaths):
    for path in filepaths:
        os.remove(path)
