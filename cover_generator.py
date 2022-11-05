from duotone.duotone import Duotone
from PIL import Image, ImageColor, UnidentifiedImageError
import re


import requests
while(True):
    image_url = input("Entrer le lien pour l'image à transformer : ")
    try:
        r = requests.get(image_url)
        cover_image_path = '/tmp/cover_generator'
        with open(cover_image_path, 'wb') as outfile:
            outfile.write(r.content)
            image = Image.open(cover_image_path)
    except UnidentifiedImageError:
        print("Le lien ne renvoie pas à une image, réessayer !")
    except requests.exceptions.MissingSchema:
        print("L'URL n'est pas valide, réessayer !")
    except requests.exceptions.ConnectionError:
        print("Erreur de connection, réessayer !")
    finally:
        break


source = input("Entrer la source de l'image (laisser vide mettra le nom de domaine source de l'image) :\n")
if source == "":
    source = re.split('[/#?]', image_url)[2]

output_pdf_filename = input("Entrer le chemin pour la sortie de la couverture :\n(sans le nom du fichier qui sera hes_background.pdf)\
    \nPar exemple : ./ ou /ceri/images/\n")
output_pdf_filename += 'hes_background.pdf'
logo_filename = "/home/iomys/dev/latex/cover_generator/logo_hei.png"


"""
Traitement de l'image
"""

light_values = ImageColor.getrgb('#cc5254')
dark_values = ImageColor.getrgb('#601947')
image = Duotone.process(image, light_values, dark_values)

result_width = 210  # Largeur de page A4
result_height = 297/2.45  # Tiers de page A4

# Calcul du ratio souhaité dans la page A4
result_ratio = result_width/result_height
# Calcul du ratio actuel de l'image
image_ratio = image.width/image.height

# On déduit le sens de rognage (haut/bas ou gauche/droite)
if image_ratio < result_ratio:
    #print("Coupe haut et bas")
    new_width = image.width
    new_height = new_width/result_ratio
    decalage = (image.height-new_height)/2
    box = (0,decalage,image.width,image.height-decalage)
else:
    #print("Coupe gauche et droite")
    new_height = image.height
    new_width = new_height*result_ratio
    decalage = (image.width-new_width)/2
    box = (decalage,0,image.width-decalage,image.height)
print(decalage)
image = image.crop(box)

image.save('/tmp/cover_result.jpg', 'jpeg')


logo = Image.open(logo_filename)
logo_ratio = logo.width/logo.height


"""
Génération du PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm



myCanvas = canvas.Canvas(output_pdf_filename, pagesize=A4)
PAGE_WIDTH, PAGE_HEIGHT = A4 #keep for later

myCanvas.drawImage('/tmp/cover_result.jpg', 0, 0, result_width*mm, result_height*mm)
logo_height = 1.7*cm
logo_width = logo_ratio * logo_height

myCanvas.drawImage(logo_filename, PAGE_WIDTH-logo_width-1.5*cm,PAGE_HEIGHT-logo_height-1.5*cm,logo_width,logo_height, mask='auto')
myCanvas.setStrokeColorRGB(1,1,1, 0.2)
myCanvas.setFillColorRGB(1,1,1, 0.2)
myCanvas.rotate(90)
myCanvas.drawString(20, -20, f"source de la couverture : {source}", direction=1,)

myCanvas.save()
