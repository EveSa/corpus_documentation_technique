import os
import re
from pdfminer.high_level import extract_text
import logging

logging.basicConfig(level = logging.INFO)

pdf_dir = "/people/sauvage/Documents/corpus_document_technique/pdf"
save_dir = "/people/sauvage/Documents/corpus_document_technique/txt"

files = (file for file in os.scandir(pdf_dir) if file.is_file())
for file in files:
    logging.info(f"...Treating file {file}")
    try :
        file_text = extract_text(os.path.join(pdf_dir, file))
    except:
        file_text=None
        print(".....pdf could not be read")
    if file_text is not None:
        lines = file_text.splitlines()
        i=0
        while i < len(lines):
            if len(lines[i]) < 3 :
                lines[i-1] = lines[i-1]+' '+lines[i]
            #re.sub(r"(.)\1{2,}", r"\1", line)
            i += 1
        
        with open(os.path.join(save_dir, file.name.replace(".pdf", ".txt")), "w") as save_file:
            for line in lines:
                save_file.write(line)
    