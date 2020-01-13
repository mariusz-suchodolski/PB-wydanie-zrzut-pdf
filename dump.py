import base64
import re
import os
from io import BytesIO
import requests
from fpdf import FPDF
import sys
import smtplib

s = requests.Session()
pat = r"<input id=\"csrf_token\" name=\"csrf_token\" type=\"hidden\" value=\"(.{40})\">"
csrftokenget = s.get("https://www.pb.pl/konto/logowanie/").content.decode("utf-8")
csrftoken = re.findall(pat, csrftokenget)[0]
print("Znaleziono token CSRF: " + csrftoken)
s.get("https://www.pb.pl/konto/logowanie/")
s.post("https://www.pb.pl/konto/logowanie/", data={'csrf_token': csrftoken,
                                                   'email': os.environ['PB_LOGIN'],
                                                   'password': os.environ['PB_PASS']})

numer = 0
rok = 0
try:
    print(sys.argv[1])
except IndexError:
    numer = input("Podaj numer wydania: ")
    rok = input("Podaj rok wydania: ")
else:
    if sys.argv[1] == "--latest":
        print("Pobieram najnowsze wydanie")
        pat = r"<p class=\"issue\">Nr (.{6,8})</p>"
        wydanieget = s.get("https://www.pb.pl/konto/e-wydania/").content.decode("utf-8")
        wydanie = re.findall(pat, wydanieget)[0]
        numer = wydanie.split("/")[0]
        rok = wydanie.split("/")[1]
    else:
        quit()

resp = s.get('https://www.pb.pl/konto/e-wydanie/' + str(rok) + '/pb' + numer.zfill(3) + '/1.png')
bites = BytesIO(base64.b64decode(resp.content))
f_name = "okladka pulsbiznesu " + numer.zfill(3) + " " + str(rok) + ".png"
with open(f_name, 'wb') as f:
    f.write(resp.content)

x = 1
eof = 0
while eof == 0:
    resp = s.get('https://www.pb.pl/konto/e-wydanie/' + str(rok) + '/pb' + numer.zfill(3) + '/' + str(x) + '_large.png')
    if resp.status_code == 404:
        eof = 1
    else:
        bites = BytesIO(base64.b64decode(resp.content))
        f_name = str(x) + ".png"
        with open(f_name, 'wb') as f:
            f.write(resp.content)
        x = x + 1

x = x - 1
print("Obecne wydanie ma " + str(x) + " stron. Generuje PDFa")
filelist = list(range(0, x))
for i in range(1, x + 1):
    filelist[i - 1] = str(i) + ".png"

pdf = FPDF()
for image in filelist:
    pdf.add_page()
    pdf.image(image, 0, 0, 210, 297)
pdf.output("pulsbiznesu " + numer.zfill(3) + " " + str(rok) + ".pdf", "F")

for filename in filelist:
    os.remove(filename)
