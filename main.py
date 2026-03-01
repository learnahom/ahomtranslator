from bs4 import BeautifulSoup
import requests
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon,QTextCursor
import qdarkstyle
import threading
import re 

import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QFontDatabase, QFont

app = QApplication(sys.argv)

font_path = r"NotoSerifAhom-Regular.ttf"

font_id = QFontDatabase.addApplicationFont(font_path)

print("Font ID:", font_id)

if font_id == -1:
    print("Font failed to load")
else:
    families = QFontDatabase.applicationFontFamilies(font_id)
    print("Loaded font:", families)

    font = QFont(families[0], 11)
    areafont = QFont(families[0], 10)


dictionary={}

def toAhomUnicode(x):
    x = re.sub(r'(e)(.)', r'\2e', x)  # bring e afterwards
    x = re.sub(r'(S)(.)', r'\2S', x)  # bring ra-glide afterwards
    x = x.replace('oj', 'jo')  # oi
    x = x.replace('oM', 'Mo')  # om
    x = x.replace('uM', 'Mu')  # um
    x = x.replace('UM', 'MU')  # uum
    x = x.replace(',j', 'j,')  # aai
    
    print(x)
    
    ahom = {
        "k": "\U00011700",
        "x": "\U00011701",
        "n": "\U00011703",
        "[": "\U00011702",
        "t": "\U00011704",
        "p": "\U00011706",
        "f": "\U00011707",
        "b": "\U00011708",
        "m": "\U00011709",
        "y": "\U0001170A",
        "c": "\U0001170B",
        "v": "\U0001170C",
        "r": "\U0001170D",
        "l": "\U0001170E",
        "s": "\U0001170F",
        "N": "\U00011710",
        "h": "\U00011711",
        "A": "\U00011712",
        "d": "\U00011713",
        ";": "𑜠",
        "g": "𑜕",
        "G": "𑜗",
        "Q": "𑜙",
        "D": "𑜔",
        "B": "𑜘",

        "S": "\U0001171E",
        "Y": "\U0001171D",
        "a": "\U00011721",
        ",": "\U00011720",
        "i": "\U00011722",
        "I": "\U00011723",
        "u": "\U00011724",
        "U": "\U00011725",
        "e": "\U00011726",
        "]": "\U00011727",
        "w": "\U0001171A\U0001172B",
        "E": "\U00011722\U00011724",
        "V": "\U00011726\U00011726",
        "C": "\U00011726",
        "o": "\U00011728",
        "j": "\U00011729",
        "M": "\U0001172A",
        "q": "\U0001172B",
        "!": ",",
        "@": ";",
        "#": ":",
        "$": "."
    }
    
    for key, value in ahom.items():
        x = x.replace(key, value)
    
    return x


def toAhomFont(x):
    ahom = {
        "𑜢𑜤": "E",
        "𑜚𑜫": "w",
        "𑜈𑜫": "w",
        "𑜀": "k",
        "𑜁": "x",
        "𑜃": "n",
        "𑜂": "[",
        "𑜄": "t",
        "𑜆": "p",
        "𑜇": "f",
        "𑜈": "b",
        "𑜉": "m",
        "𑜊": "y",
        "𑜋": "c",
        "𑜌": "v",
        "𑜍": "r",
        "𑜎": "l",
        "𑜏": "s",
        "𑜐": "N",
        "𑜑": "h",
        "𑜒": "A",
        "𑜓": "d",
        "𑜞": "S",
        "𑜝": "Y",
        ",": "!",
        ";": "@",
        ":": "#",
        ".": "$",
        "ะ": "%",
        "𑜡": "a",
        "า": ",",
        "𑜢": "i",
        "𑜣": "I",
        "𑜤": "u",
        "𑜥": "U",
        "𑜦": "e",
        "𑜧": "]",
        "𑜦𑜦": "V",
        "𑜨": "o",
        "𑜩": "j",
        "𑜪": "M",
        "𑜫": "q"
    }
    
    for key, value in ahom.items():
        x = x.replace(key, value)
    
    x = re.sub(r'(e)(.)(q)', r'C\2q', x)  # e short vowel
    x = re.sub(r'(.)(e)', r'e\1', x)      # bring e forward
    x = re.sub(r'(.)(S)', r'S\1', x)      # bring ra-glide forward
    x = x.replace('jo', 'oj')  # oi
    x = x.replace('j,', ',j')  # aai
    x = x.replace('Mo', 'oM')  # om
    x = x.replace('Mu', 'uM')  # um
    x = x.replace('MU', 'UM')  # uum
    
    return x


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Ahom Translator')
        self.setWindowIcon(QIcon('icon.png'))
        
        self.rows =[] # to store result
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText("Type any sentence here")
        self.entry.setFont(font)
        self.entry.setMaximumHeight(35)
        btn = QPushButton('Translate',self)
        btn.setStyleSheet('color:rgb(55,54,59);background-color: rgb(68,138,255);')
        self.entry.setMinimumHeight(35)
        btn.setMinimumHeight(35)
        
        self.textArea = QTextEdit(self)
        self.textArea.setFont(areafont)
        self.textArea.setMinimumWidth(600)
        self.textArea.setMinimumHeight(400)

        layout = QGridLayout()
        layout.addWidget(self.entry,0,0,1,3)
        layout.addWidget(btn,0,3)
        layout.addWidget(self.textArea,1,0,1,4)
        layout.addWidget(self.textArea,1,0,1,4)
        self.frame=QFrame()
        self.frame.setLayout(layout)
        self.setCentralWidget(self.frame)
        self.entry.returnPressed.connect(self.fetchAPI)
        btn.clicked.connect(self.fetchAPI)

    def fetchAPI(self):
        url = "http://sealang.net/ahom/search.pl"
        self.textArea.setText("Please Wait...\n")
        words = toAhomFont(self.entry.text()).split(" ")
        output = ""
        for word in words:
            if word in dictionary:
                output += dictionary[word]
            else:
                dictionary[word] = '• '+toAhomUnicode(word)+'\n'
                r = requests.post(url, data={"dict":'ahom',"language": 'ahom',"orth":word})
                soup = BeautifulSoup(r.text, "html.parser")
                if r.status_code==200:
                    for tag in soup.find_all("ahom"):
                        tag.string = toAhomUnicode(tag.string)
                        print("working",tag.string)
                    for sense in soup.find_all("sense"):
                        # print(sense)
                        if sense.find('pos'):
                            dictionary[word] +='\t'+sense.find('pos').getText()+'. '+sense.find('def').getText()+'\n'
                    output += dictionary[word]
                else:
                    output+='\tWORD NOT FOUND\n'
            QApplication.processEvents()
            self.textArea.setText(output+"Please Wait...\n")
        self.textArea.setText(output)
        
if __name__=='__main__':
    app.setStyleSheet(qdarkstyle.load_stylesheet('pyside6'))
    win=MainWindow()
    win.show()
    app.exec()