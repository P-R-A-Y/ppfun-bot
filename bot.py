import os, requests, websocket, asyncio, json, threading, time, random
import tkinter
import numpy as np
from PIL import ImageTk, Image
from io import BytesIO
import skia

dir = "C:/Users/qm080/Desktop/ppfun bot/"

headers = {
    "Host": "pixmap.fun","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8","Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive","Upgrade-Insecure-Requests": "1","Sec-Fetch-Dest": "document","Sec-Fetch-Mode": "navigate","Sec-Fetch-Site": "none","Sec-Fetch-User": "?1","TE": "trailers"
}
defaultheaders = {
    "Host": "pixmap.fun","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0","Accept": "*/*","Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive","Referer": "https://pixmap.fun/","Sec-Fetch-Dest": "script","Sec-Fetch-Mode": "no-cors","Sec-Fetch-Site": "same-origin","TE": "trailers"
}
websocketheaders = {
    "Host": "pixmap.fun","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0","Accept": "*/*","Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate, br","Sec-WebSocket-Version": "13","Origin": "https://pixmap.fun","Sec-WebSocket-Extensions": "permessage-deflate","Connection": "keep-alive, Upgrade","Sec-Fetch-Dest": "websocket","Sec-Fetch-Mode": "websocket","Sec-Fetch-Site": "same-origin","Pragma": "no-cache","Cache-Control": "no-cache","Upgrade": "websocket"
}
captchaheaders = {
    "Host": "pixmap.fun","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0","Accept": "*/*","Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate, br","Referer": "https://pixmap.fun/","Content-Type": "application/json","Origin": "https://pixmap.fun","Alt-Used": "pixmap.fun","Connection": "keep-alive","Sec-Fetch-Dest": "empty","Sec-Fetch-Mode": "cors","Sec-Fetch-Site": "same-origin"
}
window = tkinter.Tk()
targetCanvas = 0 #3-corvus 0 - earth
colors = {

}
captchas = []
bots = []
toPlace = []


class Bot():
    def __init__(self,pr,botname):
        self.session = requests.Session()
        self.proxy = pr
        self.captchaSolved = False
        self.botname = botname
        self.cooldownms = 0
        self.ws = None
        self.me = None
        self.chunkdata = []
        self.canvsize = 0
        self.minx = None
        self.miny = None
        self.maxx = None
        self.maxy = None
        self.lastcd = 16
        
    def onPixelChange(self,x,y,color):
        for pixel in toPlace:
            if pixel["x"] == x:
                if pixel["y"] == y:
                    if pixel["color"] == color:
                        try:
                            toPlace.remove(pixel)
                            print(f"nice cock x:{x} y:{y} c:{color}")
                        except:
                            pass

    def getCDInSec(self):
        return self.cooldownms/1000

    def checkforplaced(self):
        i = 0
        for pixel in toPlace:
            for pix in self.chunkdata:
                if pix["x"] == pixel["x"] and pix["y"] == pixel["y"] and pix["color"] == pixel["color"]:
                    try:
                        toPlace.remove(pixel)
                        if (i%10==0):
                            print(f"{i} skiping...")
                        i+=1
                    except:
                        pass
        if i>0:
            print(f'{i} pixel(s) already placed, skiping')

    def nextPixel(self):  
        if len(toPlace) == 0:
            print("no pixels?(")
            return
        pixel = toPlace[0]
        toPlace.remove(pixel)
        for pix in self.chunkdata:
            if pix["x"] == pixel["x"] and pix["y"] == pixel["y"] and pix["color"] == pixel["color"]:
                print(f'x:{pix["x"]}, y:{pix["y"]} already placed')
                self.checkforplaced()
                self.nextPixel()
                return
        self.placePixel(pixel["x"],pixel["y"],pixel["color"])

    def onCaptcha(self):
        if self.proxy is None:
            c = self.session.get("https://pixmap.fun/captcha.svg",headers=defaultheaders)
        else:
            c = self.session.get("https://pixmap.fun/captcha.svg",headers=defaultheaders,proxies=self.proxy)
        print(str(c.headers["captcha-id"]))
        captchas.append({
            "botname": self.botname,
            "request": c.content,
            "captchaid": str(c.headers["captcha-id"])
        })
        print("added")

    def register_chunk(self, x, y):
        data = bytearray(3)
        data[0] = 0xA1
        data[1] = x
        data[2] = y
        self.ws.send_binary(data)

    def getColor(self,x:str,y:str):
        for pixel in self.chunkdata:
            #print("x:"+pixel["x"]+" y:"+pixel["y"])
            if pixel["x"] == x and pixel["y"] == y:
                return pixel["color"]
        print(f"cant get pixel at x:{x} y:{y} chd:{len(self.chunkdata)}")
        return None

    def RGBColorToInt(self, r:int,g:int,b:int):
        if targetCanvas == 0:
            #{'2': [255, 255, 255], '3': [228, 228, 228], '4': [196, 196, 196], '5': [136, 136, 136], '6': [78, 78, 78], '7': [0, 0, 0], '8': [244, 179, 174], '9': [255, 167, 209], '10': [255, 84, 178], '11': [255, 101, 101], '12': [229, 0, 0], '13': [154, 0, 0], '14': [254, 164, 96], '15': [229, 149, 0], '16': [160, 106, 66], '17': [96, 64, 40], '18': [245, 223, 176], '19': [255, 248, 137], '20': [229, 217, 0], '21': [148, 224, 68], '22': [2, 190, 1], '23': [104, 131, 56], '24': [0, 101, 19], '25': [202, 227, 255], '26': [0, 211, 221], '27': [0, 131, 199], '28': [0, 0, 234], '29': [25, 25, 115], '30': [207, 110, 228], '31': [130, 0, 128]}
            i = 2
            while i <= 31:
                rgbarray = colors[str(i)]
                if rgbarray[0] == r:
                    if rgbarray[1] == g:
                        if rgbarray[2] == b:
                            return i
                i+=1
            print(f"unknowncolor e [{r},{g},{b}]")
            return None
        elif targetCanvas == 3:
            
            i = 0
            while i <= 21:
                rgbarray = colors[str(i)]
                if rgbarray[0] == r:
                    if rgbarray[1] == g:
                        if rgbarray[2] == b:
                            return i
                i+=1
            print(f"unknowncolor c [{r},{g},{b}]")
            return None
    
    def sendCaptcha(self, id, text):
        h = captchaheaders
        data = {"text":text,"id":id}
        size = str(len(str(data).replace(' ','')))
        h["Content-Length"] = size
        if self.proxy is None:
            r = self.session.post("https://scb.pixmap.fun/api/captcha",headers=h,json=data)
        else:
            r = self.session.post("https://scb.pixmap.fun/api/captcha",headers=h,json=data,proxies=self.proxy)
        if r.status_code == 200:
            self.captchaSolved = True
            print("zaebis")
            self.nextPixel()
        elif r.status_code == 422:
            self.onCaptcha()
        else:
            print(f"unknown status code: {r.status_code}")
    
    def placePixel(self, x, y, color):
        csz = self.canvsize
        modOffs = (csz // 2) % 256
        offs = (((int(y) + modOffs) % 256) * 256) + ((int(x) + modOffs) % 256)
        i = (int(x) + csz // 2) // 256
        j = (int(y) + csz // 2) // 256
        data = bytearray(7)
        data[0] = 0xC1
        data[1] = i
        data[2] = j
        data[3] = (offs >> 16) & 0xFF
        data[4] = (offs >>  8) & 0xFF
        data[5] = (offs >>  0) & 0xFF
        data[6] = color
        self.ws.send_binary(data)
        print(f"placing at x:{x} y:{y}")

    def get_chunk(self, x, y):
        if self.proxy is None:
            data = self.session.get(f'https://scc.pixmap.fun/chunks/{targetCanvas}/{x}/{y}.bmp',headers=defaultheaders).content
        else:
            data = self.session.get(f'https://scc.pixmap.fun/chunks/{targetCanvas}/{x}/{y}.bmp',headers=defaultheaders, proxies=self.proxy).content
        arr = np.zeros((256, 256), np.uint8)
        if len(data) != 65536:
            return arr
        for i in range(65536):
            c = data[i]
            if c >= 128:
                c = c - 128
            arr[i // 256, i % 256] = c
        return arr

    def render_chunk(self, x, y):
        print(f"render x:{x}, y:{y}")
        data = self.get_chunk(x, y)
        colors = self.me['canvases'][str(targetCanvas)]['colors']
        for cy in range(256):
            for cx in range(256):
                r, g, b = colors[data[cy, cx]]
                c = self.RGBColorToInt(r=r,g=g,b=b)
                originx = ((x-128)*256)+cx
                originy = ((y-128)*256)+cy
                self.chunkdata.append({
                    "x": str(originx),
                    "y": str(originy),
                    "color": c
                })
                #print(f"added pixel x:{originx} y:{originy} color:{c}")

    def get_chunks(self, xs, ys, w, h):
        for y in range(h):
            for x in range(w):
                self.render_chunk(x + xs, y + ys)
        
    
    def loadIRegisterChunks(self):
        c_start_y = ((self.canvsize // 2) + self.maxy) // 256
        c_start_x = ((self.canvsize // 2) + self.minx) // 256
        c_end_y = ((self.canvsize // 2) + self.miny) // 256
        c_end_x = ((self.canvsize // 2) + self.maxx) // 256
        c_occupied_y = c_end_y - c_start_y + 1
        c_occupied_x = c_end_x - c_start_x + 1
        self.get_chunks(c_start_x, c_start_y, c_occupied_x, c_occupied_y)
        for c_y in range(c_occupied_y):
            for c_x in range(c_occupied_x):
                print(f"registering chunk x:{c_x + c_start_x} y:{c_y + c_start_y}")
                self.register_chunk(c_x + c_start_x, c_y + c_start_y)

    def selectCanvas(self, ws, id):
        data = bytearray(2)
        data[0] = 0xA0
        data[1] = id
        ws.send_binary(data)

    def formRawError(self, i:int):
        if i == 0:
            pass#what u problem?
        elif i == 1:
            print("Неверное полотно! Этого полотна не существует")
            exit(0)
        elif i == 2:
            print("Неверные координаты,х вне границы")
            exit(0)
        elif i == 3:
            print("Неверные координаты, y вне границы")
            exit(0)
        elif i == 4:
            print("Неверные координаты, z вне границы")
            exit(0)
        elif i == 5:
            print("Выбран неверный цвет")
            exit(0)
        elif i == 6:
            print("Только для зарегистрированных пользователей")
            exit(0)
        elif i == 7:
            print("Вы еще не можете открыть это полотно. Вам нужно поставить больше пикселей")
            exit(0)
        elif i == 10:
            print("Captcha")
            self.captchaSolved = False
            self.onCaptcha()
        elif i == 11:
            print("Прокси не разрешены :( Вы используете прокси.")
            exit(0)
        elif i == 12:
            print("Not allowed. Just the Top10 of yesterday can place here")
            exit(0)
        elif i == 13:
            print("You are weird. Server got confused by your pixels. Are you playing on multiple devices?")
            exit(0)
        else:
            print("Странно. Невозможно поставить пиксель")
            exit(0)

    def messageReceiver(self):
        a = True
        while True:
            data = self.ws.recv()
            if data is None:
                pass
            else:
                if type(data) == str:
                    pass
                else:
                    opcode = data[0]
                    if opcode == 0xC2:
                        cd = (data[4] << 24) | (data[3] << 16) | (data[2] << 8) | data[1]
                        self.cooldownms = cd
                    elif opcode == 0xC3:
                        rc = data[1]
                        wait = (data[2] << 24) | (data[3] << 16) | (data[4] << 8) | data[5]
                        cd_s = (data[6] << 8) | data[7]
                        self.lastcd = cd_s
                        self.cooldownms = wait
                        if rc == 8:
                            print("Пиксель защищён!")
                            self.nextPixel()
                        elif rc == 9:
                            print(f"unknown code returned, but i placed, need to wait:{cd_s}s (fuck it, wait 7s), maincd:{self.cooldownms}")
                            time.sleep(7)
                            self.nextPixel()
                        elif rc != 0:
                            print("err")
                            time.sleep(7)
                            self.formRawError(rc)
                        else:
                            print(f"placed, waiting:{cd_s}s, maincd:{self.cooldownms}")
                            maxcd = int(self.me["canvases"][str(targetCanvas)]["cds"])/1000
                            if self.getCDInSec() + cd_s > maxcd:
                                time.sleep(cd_s)
                            else:
                                
                                print(f"ignoring cd cause {self.getCDInSec()} + {cd_s} < {maxcd}")
                            self.nextPixel()
                    elif opcode == 0xC1:
                        i = data[1]
                        j = data[2]
                        offs = (data[3] << 16) | (data[4] << 8) | data[5]
                        clr = data[6]
                        csz = self.me["canvases"][str(targetCanvas)]["size"]
                        x = ((i * 256) - (csz // 2)) + (offs & 0xFF)
                        y = ((j * 256) - (csz // 2)) + ((offs >> 8) & 0xFF)
                        print(f'Pixel update at x:({str(x)}, y:{str(y)}, color:{int(clr)})')
                        self.onPixelChange(str(x),str(y),int(clr))
                    elif opcode == 0xA7:
                        if a:
                            a = False
                            time.sleep(1)
                            self.nextPixel()

    def connect(self):
        for pixel in toPlace:
            #print(f'x: {pixel["x"]}, y: {pixel["x"]}')
            if self.minx is None:
                self.minx = int(pixel["x"])
            elif self.minx > int(pixel["x"]):
                self.minx = int(pixel["x"])
            
            if self.miny is None:
                self.miny = int(pixel["y"])
            elif self.miny > int(pixel["y"]):
                self.miny = int(pixel["y"])
            
            if self.maxx is None:
                self.maxx = int(pixel["x"])
            elif self.maxx < int(pixel["x"]):
                self.maxx = int(pixel["x"])

            if self.maxy is None:
                self.maxy = int(pixel["y"])
            elif self.maxy < int(pixel["y"]):
                self.maxy = int(pixel["y"])
        #print(f"minx:{self.minx} miny:{self.miny} maxx:{self.maxx} maxy:{self.maxy}")
        if self.proxy is None:
            ppf = self.session.get("https://pixmap.fun/#d,-177,-19,17", headers = headers)
        else:
            ppf = self.session.get("https://pixmap.fun/#d,-177,-19,17", headers = headers, proxies=self.proxy)
        if ppf.status_code != 200:
            print(ppf.status_code)
            exit(0)
        #lin = str(ppf.content).split("<body>")[1].split("</div>")[1].split("</body>")[0]
        #vnd = lin.split('<script src="')[1].split('"></script>')[0].split('./assets/')[1]
        #clnt = lin.split('vendor')[1].split('<script src="')[1].split('"></script>')[0].split('./assets/')[1]
        #if self.proxy is None:
        #    vendor = self.session.get(f"https://pixmap.fun/assets/{vnd}",headers=defaultheaders)
        #    client = self.session.get(f"https://pixmap.fun/assets/{clnt}",headers=defaultheaders)
        #else:
        #    vendor = self.session.get(f"https://pixmap.fun/assets/{vnd}",headers=defaultheaders,proxies=self.proxy)
        #    client = self.session.get(f"https://pixmap.fun/assets/{clnt}",headers=defaultheaders,proxies=self.proxy)
        #with open(f"{dir}cl.txt", "wb") as f:
        #    f.write(client.content)
        #    f.close()
        if self.proxy is None:
            self.me = self.session.get('https://scb.pixmap.fun/api/me',headers=defaultheaders).json()
        else:
            self.me = self.session.get('https://scb.pixmap.fun/api/me',headers=defaultheaders,proxies=self.proxy).json()
        self.canvsize = self.me["canvases"][str(targetCanvas)]['size']
        canvas = self.me["canvases"][str(targetCanvas)]
        i = 0
        for color in canvas["colors"]:
            colors[str(i)] = color
            i += 1
        
        print(colors)
        #print(f"added colors 2 to {i}")
        if self.proxy is None:
            self.ws = websocket.create_connection("wss://scc.pixmap.fun:443/ws",header = websocketheaders)
        else:
            self.ws = websocket.create_connection("wss://scc.pixmap.fun:443/ws",header = websocketheaders,http_proxy_host=str(self.proxy["http"]).split("//")[1].split(":")[0],http_proxy_port=str(self.proxy["http"]).split("//")[1].split(":")[1])
        if self.ws.status == 101:
            print(f"{self.botname} connected")
            self.selectCanvas(self.ws,targetCanvas)
            self.loadIRegisterChunks()
            threading.Thread(target=self.messageReceiver).start()
            #threading.Thread(target=self.drawWorker).start()

def svgCodeToByteio(svgcode):
    filename = str(random.randint(100,9999))+random.choice("q w e r t y u i".split())+".svg"
    with open(f"{dir}{filename}", 'wb') as f:
        f.write(svgcode)

    skia_stream = skia.Stream.MakeFromFile(f"{dir}{filename}")
    skia_svg = skia.SVGDOM.MakeFromStream(skia_stream)

    svg_width, svg_height = skia_svg.containerSize()
    surface_width = 500
    surface_height = 300

    surface = skia.Surface(surface_width, surface_height)
    with surface as canvas:
        canvas.scale(surface_width / svg_width, surface_height / svg_height)
        skia_svg.render(canvas)
    return BytesIO(surface.makeImageSnapshot().encodeToData())

def captchaWorker():
    while (True):
        if (len(captchas)>0):
            frame = tkinter.Canvas(window, width=500, height=300)
            frame.grid(column=0,row=0)
            svgcode = captchas[0]["request"]
            png = Image.open(svgCodeToByteio(svgcode))
            pimg = ImageTk.PhotoImage(png)
            #frame.pack()
            frame.create_image(0,0,anchor='nw',image=pimg)
            currentC = captchas[0]["botname"]
            sendmsgcontent = tkinter.Entry(window, width=50)
            sendmsgcontent.grid(column=0, row=1)
            def solvecaptchaClick():
                text = sendmsgcontent.get()
                for bot in bots:
                    if bot.botname == captchas[0]["botname"]:
                        bot.sendCaptcha(captchas[0]["captchaid"], text)
                        print("Sended")
                        break
                captchas.pop(0)
            btn = tkinter.Button(window, text="отправить(нахуй))", command=solvecaptchaClick)
            btn.grid(column=0, row=2)
            while True:
                if len(captchas)==0:
                    break
                elif currentC != captchas[0]["botname"]:
                    break
                else:
                    time.sleep(1)
        else:
            time.sleep(2)

pixelExample = {
    "x": "90",
    "y": "90",
    "color": 15
}

def addPixels(fromX,fromY,toX,toY,color):
    x = np.min([fromX,toX])
    pixels = []
    while x <= np.max([fromX,toX]):
        y = np.min([fromY,toY])
        while y <= np.max([fromY,toY]):
            pixels.append({"x":str(x),"y":str(y),"color":color})
            print(f"added: x:{x} y:{y}")
            y+=1
        x+=1
    print(f"succes {len(pixels)}")
    return pixels

def main():
    with open(f"{dir}data.json","r") as raw:
        f = json.load(raw)
        if f["startMode"] == "setup":
            window.geometry('350x100')
            window.event_add('<<Paste>>', '<Control-igrave>')
            window.event_add("<<Copy>>", "<Control-ntilde>")
            minmaxposicolor = tkinter.Entry(window, width=50)
            minmaxposicolor.grid(column=0, row=0)
            def cl():
                t = minmaxposicolor.get().split(" ")
                print(t)
                minx = int(t[0])
                miny = int(t[1])
                maxx = int(t[2])
                maxy = int(t[3])
                color = int(t[4])
                a = addPixels(minx, miny, maxx, maxy, color)
                with open(f"{dir}data.json","w") as d:
                    for o in a:
                        f["toDraw"].append(o)
                    json.dump(f, d, indent=4,ensure_ascii=True)
            btn = tkinter.Button(window, text="set", command=cl)
            btn.grid(column=0, row=1)

            window.mainloop()
        elif f["startMode"] == "boting":
            i = len(f["toDraw"])

            for proxy in f["proxies"]:
                if type(proxy) == dict:
                    b = Bot(proxy,str(random.randint(10000,999999)))
                elif type(proxy) == str:
                    if proxy == "none":
                        b = Bot(None,str(random.randint(10000,999999)))
                    else:
                        p = {
                            "http": f"http://{proxy}"
                        }
                        #print("automatic form proxy(")
                        b = Bot(p,str(random.randint(10000,999999)))
                bots.append(b)

            for pixel in f["toDraw"]:
                toPlace.append(pixel)
            raw.close()

            for bot in bots:
                threading.Thread(target=bot.connect).start()

            print(f"loaded {i} pixels to draw")
            threading.Thread(target=captchaWorker).start()
            window.geometry('500x400')
            window.mainloop()

main()



