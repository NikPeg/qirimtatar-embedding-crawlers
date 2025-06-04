import aspose.pdf as ap
import aspose.pydrawing as drawing

import pytesseract
import cv2
import os
import configparser
import aspose.pdf as pdf



config = configparser.ConfigParser()  # создаём объекта парсера
config.read(".global_config.ini")

async def images_get(pdf_path:str) ->list:
    doc =  ap.Document(pdf_path)
    image_counter = 1
    image_name = "image_{counter}.jpg"
    print("q", doc.file_name)
    os.mkdir(os.path.join(pdf_path, doc.file_name.replace(".pdf", "_images")))
    paths = []
        
    for page in doc.pages:

        for image in page.resources.images: 
            with open(
                os.path.join(pdf_path,  doc.file_name.replace(".pdf", "_images"), image_name.format(counter=image_counter)), "wb") as stream:
                # Сохранить изображение
                image.save(stream, drawing.imaging.ImageFormat.jpeg)
                paths.append(os.path.join(pdf_path,  doc.file_name.replace(".pdf","_images"), image_name.format(counter=image_counter))) 
                image_counter = image_counter + 1
                stream.close()                  

    return paths
    


async def image_text_collect(image_path) -> str:

    pytesseract.pytesseract.tesseract_cmd = config["tess"]["tesseract_path"]
    img_cv = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    try:
        return pytesseract.image_to_string(img_rgb)
    
    except Exception as e:
        print(e)
        return False 

async def pdf_world_count(pdf_path) -> dict:
    pdfFile = pdf.Document(pdf_path)


    textAbsorber = pdf.text.TextAbsorber()


    pdfFile.pages.accept(textAbsorber)
    text = textAbsorber.text
    worlds = text.split(" ")
    return {"worlds_count": len(worlds), "text": text}
