import requests
import json
from PIL import Image
import threading

nosaukums = "49 - BIOLOĢIJA VIDUSSKOLAI, 4. DAĻA"
url = "jurdcnjxgy2ce/6761095?_=1711300782532" # BOOK ID
threadCount = 12
threads = []
highestPage = 0

cookies = {
    "JSESSIONID": "", # SESSION ID
}

def main():
    res= requests.get('https://cloubi.zvaigzne.lv/o/site-material-api/pages-with-scores/'+url, cookies=cookies)
    if res.status_code == 400:
        return
    response = json.loads(res.content)
    pages = list(response["pages"].values())
    
    for i in range(threadCount):
        t = threading.Thread(target=download_images, args=(pages, i, threadCount,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
        
    img2pdf(highestPage)

def download_images(pages, page, spaced):
    global highestPage
    while page < len(pages):
        if pages[page]['navigation']:
            page += spaced
            continue
        contentUrl = 'https://cloubi.zvaigzne.lv'+pages[page]['contentUrl']
        contentRes = requests.get(contentUrl, cookies=cookies)
        body = contentRes.text
        index = body.find("/o/blob-download")
        imageUrl = 'https://cloubi.zvaigzne.lv'+body[index:body.find("\"", index)]
        imageUrl = imageUrl.replace('\\x3d', '=')
        imageUrl = imageUrl.replace('\\x26', '&')
        r = requests.get(imageUrl)
        open('page'+str(pages[page]['shortTitle'])+'.png', 'wb').write(r.content)
        if int(pages[page]['shortTitle']) > highestPage:
            highestPage = int(pages[page]['shortTitle'])
        page += spaced


pdf_path = nosaukums+".pdf"

def img2pdf(pages):
    imagePaths = []
    for i in range(pages):
        imagePaths.append("page"+str(i+1)+".png")
    images = [
        Image.open(f)
        for f in imagePaths
    ]
    images[0].save(
        pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
    )

if __name__ == '__main__':
    main()