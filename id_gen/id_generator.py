from PIL import Image, ImageDraw, ImageFont
import requests
import os
from pysondb import db

dbe=db.getDb("db.json")

#download file
def download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

def upload_telegraph(img):
    url="https://telegra.ph/upload"
    files={'file':open(img,'rb')}
    r=requests.post(url,files=files)
    if not r.ok:
        return None
    try:
        data=r.json()[0]
        
        if "src" in data.keys():
            return f"https://telegra.ph{data['src']}"
        else:
            return None
    except:
        return None


def generate_id(name,regd,branch,validity,blood_group,image_url):
    local_data=dbe.getByQuery({"regd":regd})
    if local_data:
        return local_data[0]["link"]
    file_name = download_file(image_url)
    image = Image.open('id_gen/bg.jpg')
    pic = Image.open(file_name)
    pic=pic.resize((80,112))
    blood = Image.open('id_gen/b.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('id_gen/Gandhi Sans.ttf', size=16)
    color = 'rgb(0, 0, 0)'

    draw.text((200, 133), 'Name', fill=color, font=font)
    draw.text((200, 158), 'Branch', fill=color, font=font)
    draw.text((200, 183), 'Regd No', fill=color, font=font)
    draw.text((200, 208), 'Validity', fill=color, font=font)

    draw.text((280, 133), ':', fill=color, font=font)
    draw.text((280, 158), ':', fill=color, font=font)
    draw.text((280, 183), ':', fill=color, font=font)
    draw.text((280, 208), ':', fill=color, font=font)

    draw.text((290, 133), name, fill=color, font=font)
    draw.text((290, 158), branch, fill=color, font=font)
    draw.text((290, 183), regd, fill=color, font=font)
    draw.text((290, 208), validity, fill=color, font=font)

    Image.Image.paste(image, pic, (65, 125))
    Image.Image.paste(image, blood, (16, 170))

    draw.text((25, 183), blood_group, fill='#ffffff', font=font)
    image.save(f"{regd}.png")
    link=upload_telegraph(f"{regd}.png")
    ok=dbe.add({"regd":regd,"link":link})
    try:
        os.remove(file_name)
        os.remove(f"{regd}.png")
    except:
        pass
    return link
