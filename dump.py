import base64
import re
import os
from io import BytesIO
import requests
import img2pdf

s = requests.Session()
pat = r"<input id=\"csrf_token\" name=\"csrf_token\" type=\"hidden\" value=\"(.{40})\">"
csrftokenget = s.get("https://www.pb.pl/konto/logowanie/").content
csrftoken = re.findall(pat, csrftokenget)[0]
print "Znaleziono token CSRF: " + csrftoken
s.get("https://www.pb.pl/konto/logowanie/")
s.post("https://www.pb.pl/konto/logowanie/", data={'csrf_token': csrftoken,
                                                   'email': '',
                                                   'password': ''})

numer = input("Podaj numer wydania: ")
rok = input("Podaj rok wydania: ")

x = 1
eof = 0
while eof == 0:
    resp = s.get('https://www.pb.pl/konto/e-wydanie/'+str(rok)+'/pb'+str(numer)+'/' + str(x) + '_large.png')
    if resp.status_code == 404:
        eof = 1
    else:
        bites = BytesIO(base64.b64decode(resp.content))
        f_name = str(x) + ".png"
        with open(f_name, 'wb') as f:
            f.write(resp.content)
        x = x + 1

x = x - 1
print "Obecne wydanie ma " + str(x) + " stron. Generuje PDFa"
filelist = list(range(0, x))
for i in range(1, x+1):
    filelist[i-1] = str(i) + ".png"

with open("pulsbiznesu "+str(numer)+" "+str(rok)+".pdf", "wb") as f:
    f.write(img2pdf.convert(filelist))

for filename in filelist:
    os.remove(filename)