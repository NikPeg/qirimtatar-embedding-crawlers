import asyncio
import aiofiles
import os
import zipfile
from pathlib import Path
import aspose.words as aw
import platform
from _yandex_detect.translate_api import Dedector
from _pdf_utils import image_text_collect, images_get, pdf_world_count
from multiprocessing import Process
D = Dedector()

in_path = os.path.join("junior_archives", "in")
out_path = os.path.join("junior_archives", "out") 


files = os.listdir(in_path)
pr_count = len(files)
processes = []

doc_names = ["doc", "docx", "otf", "odt", "rft", ".pdf.docx", ".pdf.doc"]
pdf_names = ["pdf", ".docx.pdf", ".doc.pdf"]
images_names = ["jpg", "png", "jpeg"]
out_count = pr_count

async def convert(out_files):
    for fp in out_files:
        fe = fp.split(".")[-1]
        tmp_f = fp+".txt.tmp"
        print("fe ", fe, " fp ", fp, " tmp_f ", tmp_f)
        if fe in doc_names:
            
            doc_convert = await asyncio.to_thread(aw.Document, fp)
            await asyncio.to_thread(doc_convert.save, fp+".txt")

            async with aiofiles.open(fp+".txt", mode="r+", encoding="utf-8-sig") as s, aiofiles.open(tmp_f, mode="w", encoding="'utf-8-sig") as f: #этот кусок кода нужен для того чтобы убрать марки либы apose
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
            if  int(ll) == 0:
                    print (f"delete_files ll=={ll}")
                    await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                    asyncio.to_thread(os.remove, fp+".txt"), asyncio.to_thread(os.remove, tmp_f) )
            """ else:
                    try:
                        if await  D.detect(lines[7], True) == False:
                                                            print ("delete_files langue not tr")
                                                            await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                                                                            asyncio.to_thread(os.remove, fe+".txt"), asyncio.to_thread(os.remove, tmp_f))                                                 
                                                            ll=0
                    except Exception as e:
                        print(e)
                        await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                        asyncio.to_thread(os.remove, fp+".txt"), asyncio.to_thread(os.remove, tmp_f))"""

            if int(ll) !=0:
                    print("save")
                    print(tmp_f)
                    await asyncio.gather(asyncio.to_thread(os.remove, fp+".txt"), asyncio.to_thread(os.rename, tmp_f, fe+".txt"))

        if fe in pdf_names:
            print("PDF")
            tc = await pdf_world_count(fp)
            if tc["worlds_count"] > 0:
                doc_convert = aw.Document(fp)
                print("Convert", fp)
                doc_convert.save(fp+".txt")
                print("ok")

                async with aiofiles.open(fp+".txt", mode="r+", encoding="utf-8-sig") as s, aiofiles.open(tmp_f, mode="w+", encoding="'utf-8-sig") as f: #этот кусок кода нужен для того чтобы убрать марки либы apose
                    lines = []
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
                if  int(ll) == 0:
                        print (f"delete_files ll=={ll}")
                        await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                        asyncio.to_thread(os.remove, fe+".txt"), asyncio.to_thread(os.remove, tmp_f) )
                else:
                        try:
                            if await  D.detect(lines[7], True) == False:
                                                                print ("delete_files langue not tr")
                                                                await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                                                                                asyncio.to_thread(os.remove, fp+".txt"), asyncio.to_thread(os.remove, tmp_f))                                                 
                                                                ll=0
                        except Exception as e:
                            print(e)
                            await asyncio.gather(asyncio.to_thread(os.remove, fp), 
                            asyncio.to_thread(os.remove, fp+".txt"), asyncio.to_thread(os.remove, tmp_f))

                if int(ll) !=0:
                        print("save")
                        print(tmp_f)
                        await asyncio.gather(asyncio.to_thread(os.remove, fp+".txt"), asyncio.to_thread(os.rename, tmp_f, fp+".txt"))
            elif tc == 0:
                imges = await images_get(fp)
                samples = ""
                for im in imges:
                    samples += await image_text_collect(im)
                s_w = samples.split(" ")
                if D.detect(s_w[4], True) == True:
                    async with aiofiles.open(fp+".txt", "w") as f:
                        f.write(samples)
                        f.close()
                elif D.detect(s_w[4], True) == False:
                    await asyncio.gather(asyncio.to_thread(os.remove, fp))


def ext(arch_path, out):
    documents_list = doc_names+pdf_names+images_names
    with zipfile.ZipFile(arch_path, "r") as arch:
        print("filename: ", arch.filename)
        for file in arch.namelist():
            
                sp = file.split(".")[-1]
                if  sp in documents_list:
                    arch.extract(file, out)
                elif  sp == "zip":

                    inner_arch = arch.open(file)
                    with zipfile.ZipFile(inner_arch) as inner:                   
                        for inner_file in inner.namelist():                          
                            qr = inner_file.split(".")

                            if  qr[-1] in documents_list:
                                inner.extract(inner_file, out)

        arch.close()

def main(arch_path, path_in_out:list):  
    #ext(arch_path, path_in_out)
    async def scan_and_convert():
        print("QUQUQ", path_in_out)
        p = Path(path_in_out)
        fp = []
        for x in p.rglob("*"):           
            #print(x)         
            if x.is_file():             
                fp.append(str(x))
        print("path", fp)        
        await convert(fp)   
    asyncio.get_event_loop().run_until_complete(scan_and_convert())

if __name__ == "__main__":
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


    
    for i in range(0, pr_count):
            path_in_out = os.path.join(out_path, str(i))
            path_check = os.path.exists(path_in_out)
            if path_check == False:
                os.mkdir(path_in_out)
            ft = os.path.join(in_path, files[i])
            print(ft)
            processes.append(Process(target=main, args=(ft, path_in_out)))
            processes[i].start()


#asyncio.run(convert(["junior_archives\\out\\0\\Kırım Akademiyası Telegram kanali\\karadag_qirim_tabiati_foto_1989.pdf"]))
#doc_convert = aw.Document("junior_archives\\out\\0\\Kırım Akademiyası Telegram kanali\\antoloji_qarilgachlar_duasi_2006.pdf ") 
#doc_convert.save("junior_archives\\out\\0\\Kırım Akademiyası Telegram kanali\\antoloji_qarilgachlar_duasi_2006.txt")

