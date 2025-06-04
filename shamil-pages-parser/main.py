import aiohttp
import asyncio
import platform
import re
import os
import aiofiles
from bs4 import BeautifulSoup
import aspose.words as aw
from _yandex_detect.translate_api import Dedector
from _pdf_utils import image_text_collect, images_get
D = Dedector()



async def main():
    url = "https://shamil-alyadin.com/ru/page.php?id=3&book=22&title={title}"
    pattern = re.compile(r'href\s*=\s*["\']download\.php[^"\']+["\']')
    max_books_titles = 219 #219 #перебирать последний аргумент по порядку если ссылки нема то пропускать
    async with aiohttp.ClientSession() as session:
        for i in  range(max_books_titles):
            async with session.get(url.format(title=i)) as response:      
                rs = response.status
                if rs == 200:

                    page = await response.text()
                    soup = await asyncio.to_thread(BeautifulSoup, page, "html.parser")
                    fr = re.findall(pattern, str(soup))

                    if fr != []:
                        fr = fr[0].split('href=')[1]

                        fn = fr.split(";")[1]
                        fn = fn.replace("name=", "").replace('"','')  #имя файла

                        fr= "https://shamil-alyadin.com/ru/"+fr.replace("&amp;", "&").replace('"','')
                        async with session.get(fr) as response:
                            rs = response.status
                            if rs == 200:
                                try:
                                    fp =os.path.join("shamil-pages-parser","files", fn) #путь до файла
                                    async with aiofiles.open(file=fp, mode="wb+") as f:
                                        ds = 0
                                        async for data in response.content.iter_chunked(8192):
                                            await  f.write(data)
                                            ds += len(data)
                                        await f.close()
                                    fe =[]
                                    print("E", fp)
                                    if ".pdf" in fp or ".doc.pdf" in fp:
                                        print("pdf")
                                        fe= str(fp.split(".pdf")[0]) # в том случае если это пдф оно все картинки в один текстовый файл перегоняет
                                        paths = await images_get(fp) 
                                        samples = ""
                                        for path in paths:
                                            samples += str(await image_text_collect(path))
                                        async with aiofiles.open(fp+".txt", "w") as f:
                                            await f.write(samples)
                                            await f.close()
                                    elif ".doc" in fp and ".pdf" not in fp:
                                        fe = str(fp.split(".pdf")[0]) #расшиерние файла
                                        
                                        doc_convert = await asyncio.to_thread(aw.Document, fp)
                                        await asyncio.to_thread(doc_convert.save, fe+".txt")
                                        tmp_f = fe+".txt.tmp" #временный файл

                                        async with aiofiles.open(fe+".txt", mode="r", encoding="utf-8-sig") as s, aiofiles.open(tmp_f, mode="w", encoding="'utf-8-sig") as f: #этот кусок кода нужен для того чтобы убрать марки либы apose
                                            global lines
                                            lines = await s.readlines()
                                            ll = len(lines)                                                                                              
                                            filter =  ["Created with an evaluation copy of Aspose.Words. To remove all limitations, you can use Free Temporary License https://products.aspose.com/words/temporary-license/",
                                                       "Evaluation Only. Created with Aspose.Words. Copyright 2003-2025 Aspose Pty Ltd."]    
                                            if int(ll) != 0:   
                                                filtered = []
                                                for i in lines:
                                                    for y in filter:
                                                        i = i.replace(y, "")
                                                    filtered.append(i)

                                                await f.writelines(filtered)

                                            await f.close()
                                            await s.close()     
                                        print(f"fp: {fp}, ll: {ll}, fe: {fe}, tmp_f: {tmp_f}")
                                        print(f"liness:", lines[7])
                                        if  int(ll) == 0:
                                                print (f"delete_files ll=={ll}")
                                                await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                                                                     asyncio.to_thread(os.remove, fe+".txt"), asyncio.to_thread(os.remove, tmp_f) )
                                        else:
                                            try:
                                                if await  D.detect(lines[7], True) == False:
                                                        print ("delete_files langue not tr")
                                                        await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                                                                        asyncio.to_thread(os.remove, fe+".txt"), asyncio.to_thread(os.remove, tmp_f))                                                 
                                                        ll=0
                                            except Exception as e:
                                                print(e)
                                                await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                                                            asyncio.to_thread(os.remove, fe+".txt"), asyncio.to_thread(os.remove, tmp_f))

                                            if int(ll) !=0:
                                                print("save")
                                                print(tmp_f)
                                                await asyncio.gather(asyncio.to_thread(os.remove, fe+".txt"), asyncio.to_thread(os.rename, tmp_f, fe+".txt"))

                                        
                                                                                     
                                except Exception as e:
                                    print("ex", e)                                           
                            else:
                                print(f"error status code - {rs}")
                else:
                    print(f"error status code - {rs}")
if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())