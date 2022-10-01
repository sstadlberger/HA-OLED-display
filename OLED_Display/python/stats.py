import json
import subprocess
import schedule
import time
import locale
import requests
from board import SCL, SDA
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont, ImageOps
import re
import random
import argparse
import os

locale.setlocale(locale.LC_ALL, "de_DE.utf8")

print("START-----")
print("Hello World")
print("----------")
print(locale.LC_ALL)
print("----------")
print(234687234682734.133)
print("----------")
print(locale.format_string("%f.2", 234687234682734.133, grouping=True))
print("----------")
f = open("/data/options.json", "r")
print(f.read())
print("END-------")



displayWidth = 128
displayHeight = 64

basepath = os.path.dirname(os.path.abspath(__file__))

font16 = ImageFont.truetype(basepath + "/pixel_operator/PixelOperator.ttf", 16)
font16B = ImageFont.truetype(basepath + "/pixel_operator/PixelOperator-Bold.ttf", 16)
font12 = ImageFont.truetype(basepath + "/pixel_operator/PixelOperator8.ttf", 8)

iconCPU = Image.open(basepath + "/icons/memory.png")
iconNet = Image.open(basepath + "/icons/lan.png")
iconRAM = Image.open(basepath + "/icons/view-module-outline.png")
iconSD = Image.open(basepath + "/icons/sd.png")
iconPiHole = Image.open(basepath + "/icons/pi-hole.png")

i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(displayWidth, displayHeight, i2c)
disp.fill(0)
disp.show()


image = Image.new("1", (displayWidth, displayHeight))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, displayWidth, displayHeight), outline=0, fill=0)

parser = argparse.ArgumentParser(description="Display info on front OLED display.")
parser.add_argument("--mode", type=str, required=True)
args = parser.parse_args()


def shell_cmd(cmd):
    return str(subprocess.check_output(cmd, shell=True).decode("utf-8")).strip()


def hassos_get_info(type):
    config_file = open("/data/options.json", "r")
    config_data = json.load(config_file)
    print(config_data)
    token = config_data['SUPERVISOR_TOKEN']
    print("Token: " + token)
    print('curl -sSL -H "Authorization: Bearer ' + token + '" http://supervisor/' + type)
    info = shell_cmd('curl -sSL -H "Authorization: Bearer ' + token + '" http://supervisor/' + type)
    print("START--hassos_get_info--")
    print(info)
    print("END----hassos_get_info--")
    token = "HCVJHAGVDJHGVASJHVASHGDVHJASGD"
    print("Token: " + token)
    print('curl -sSL -H "Authorization: Bearer ' + token + '" http://supervisor/' + type)
    info = shell_cmd('curl -sSL -H "Authorization: Bearer ' + token + '" http://supervisor/' + type)
    print("START--hassos_get_info--")
    print(info)
    print("END----hassos_get_info--")
    print("Token: " + token)
    print('curl -sSL -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/' + type)
    info = shell_cmd('curl -sSL -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/' + type)
    print("START--hassos_get_info--")
    print(info)
    print("END----hassos_get_info--")
    return json.loads(info)


def getBaseData():
    baseData = {
        "ip": "",
        "host": "",
        "mac": "",
        "cpu": "",
        "memoryUsed": "",
        "memoryTotal": "",
        "memoryPct": "",
        "diskTotal": "",
        "diskUsed": "",
        "diskPct": "",
        "temperature": "",
        "uptime": "",
        "load": ["", "", ""],
        "link": "",
    }
    print(baseData)

    cmd = "hostname -I | cut -d\' \' -f1 | tr -d \'\\n\'"
    baseData["ip"] = shell_cmd(cmd)
    print("ip---------------")
    print(baseData)
    cmd = "hostname | tr -d \'\\n\'"
    baseData["host"] = shell_cmd(cmd)
    print("host-------------")
    print(baseData)
    
    cmd = "cat /sys/class/net/eth0/address"
    baseData["mac"] = shell_cmd(cmd)
    print("mac--------------")
    print(baseData)

    if args.mode == "pi-hole":
        cmd = "dmesg | grep eth0 | grep Up | grep -o -E '\- (.*?) -' | tail -1 | grep -o -E '[^ -]*'"
        baseData["link"] = shell_cmd(cmd)
    elif args.mode == "hassio":
        hassos_get_info("host/info")
        hassos_get_info("network/info")
        cmd = "dmesg"
        tmp = shell_cmd(cmd)
        print(tmp)
    print("link-------------")
    print(baseData)

    cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
    baseData["cpu"] = shell_cmd(cmd)
    print("-----------------")
    print(baseData)

    cmd = "free -m | awk 'NR==2{printf \"%s/%s\", $3,$2 }'"
    data = str(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    parts = data.split("/")
    baseData["memoryPct"] = locale.format_string("%d", float(parts[0]) / float(parts[1]) * 100, grouping=True) + "%"
    print("-----------------")
    print(baseData)
    baseData["memoryUsed"] = locale.format_string("%d", float(parts[0]), grouping=True) + "MB"
    print("-----------------")
    print(baseData)
    baseData["memoryTotal"] = locale.format_string("%d", float(parts[1]), grouping=True) + "MB"
    print("-----------------")
    print(baseData)

    cmd = "df -h | awk '$NF==\"/\"{printf \"%d/%d\", $3,$2}'"
    data = str(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    parts = data.split("/")
    baseData["diskPct"] = locale.format_string("%d", float(parts[0]) / float(parts[1]) * 100, grouping=True) + "%"
    print(baseData)
    baseData["diskTotal"] = locale.format_string("%d", float(parts[1]), grouping=True) + "GB"
    print(baseData)
    baseData["diskUsed"] = locale.format_string("%d", float(parts[0]), grouping=True) + "GB"
    print(baseData)

    cmd = "vcgencmd measure_temp | grep -E -o \"([0-9.\-])*\""
    data = float(subprocess.check_output(cmd, shell=True).decode("utf-8").strip())
    baseData["temperature"] = locale.format_string("%.1f", data, grouping=True) + "°C"
    print(baseData)

    cmd = "uptime"
    data = str(subprocess.check_output(cmd, shell=True).decode("utf-8").strip())
    result = re.findall("up (.*?), +\d+ user.*?(\d\.\d\d).*?(\d\.\d\d).*?(\d\.\d\d)", data)
    baseData["uptime"] = result[0][0].replace("  ", " ")
    print(baseData)
    baseData["load"][0] = locale.format_string("%.2f", float(result[0][1]), grouping=True)
    print(baseData)
    baseData["load"][1] = locale.format_string("%.2f", float(result[0][2]), grouping=True)
    print(baseData)
    baseData["load"][2] = locale.format_string("%.2f", float(result[0][3]), grouping=True)
    print(baseData)

    return baseData


def getPiHoleData():
    api_url = "http://localhost/admin/api.php"

    piHoleData = {
        "clients": "n/a",
        "ads": "n/a",
        "queries": "n/a",
        "cache": "n/a",
    }

    try:
        r = requests.get(api_url)
        data = json.loads(r.text)
        piHoleData["queries"] = locale.format_string("%d", data["dns_queries_today"], grouping=True)
        piHoleData["ads"] = locale.format_string("%d", data["ads_blocked_today"], grouping=True)
        piHoleData["clients"] = locale.format_string("%d", data["unique_clients"], grouping=True)
        if data["dns_queries_today"] > 0:
            piHoleData["cache"] = locale.format_string("%.1f", (data["queries_cached"] / data["dns_queries_today"] * 100), grouping=True) + "%"
    except KeyError:
        time.sleep(1)

    return piHoleData


def displayClear():
    disp.fill(0)
    disp.show()


def drawHeader(ip, host, icon, name):
    topOffset = random.randint(0, 1)
    leftOffset = random.randint(0, 1)
    rightOffset = 128 - random.randint(0, 1)
    drawString = name
    w, h = draw.textsize(drawString, font=font16B)
    draw.text((128 - w, 0), drawString, font=font16B, fill=255)
    drawString = host
    w, h = draw.textsize(drawString, font=font12)
    draw.text((128 - w, 15), drawString, font=font12, fill=255)

    image.paste(icon, (0, 0))


def displayNetwork():
    displayClear()

    baseData = getBaseData()

    draw.rectangle((0, 0, displayWidth, displayHeight), outline=0, fill=0)
    drawHeader(baseData["ip"], baseData["host"], iconNet, "NETWORK")


    draw.text((0, 23), "IP:", font=font16, fill=255)
    drawString = baseData["ip"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 23), drawString, font=font16, fill=255)

    draw.text((0, 36), "LINK:", font=font16, fill=255)
    drawString = baseData["link"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 36), drawString, font=font16, fill=255)

    drawString = baseData["mac"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text(((128-w) / 2, 49), drawString, font=font16, fill=255)

    disp.image(image)
    disp.show()


def displayCPU():
    displayClear()

    baseData = getBaseData()

    draw.rectangle((0, 0, displayWidth, displayHeight), outline=0, fill=0)
    drawHeader(baseData["ip"], baseData["host"], iconCPU, "CPU")


    draw.text((0, 23), "LOAD:", font=font16, fill=255)
    drawString = baseData["load"][0] + "%"
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 23), drawString, font=font16, fill=255)

    draw.text((0, 36), "TEMP:", font=font16, fill=255)
    drawString = baseData["temperature"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 36), drawString, font=font16, fill=255)

    draw.text((0, 49), "UP:", font=font16, fill=255)
    drawString = baseData["uptime"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 49), drawString, font=font16, fill=255)

    disp.image(image)
    disp.show()


def displayRAM():
    displayClear()

    baseData = getBaseData()

    draw.rectangle((0, 0, displayWidth, displayHeight), outline=0, fill=0)
    drawHeader(baseData["ip"], baseData["host"], iconRAM, "MEMORY")


    draw.text((0, 23), "USED:", font=font16, fill=255)
    drawString = baseData["memoryUsed"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 23), drawString, font=font16, fill=255)

    draw.text((0, 36), "TOTAL:", font=font16, fill=255)
    drawString = baseData["memoryTotal"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 36), drawString, font=font16, fill=255)

    draw.text((0, 49), "UTILIZED:", font=font16, fill=255)
    drawString = baseData["memoryPct"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 49), drawString, font=font16, fill=255)

    disp.image(image)
    disp.show()


def displayStorage():
    displayClear()

    baseData = getBaseData()

    draw.rectangle((0, 0, displayWidth, displayHeight), outline=0, fill=0)
    drawHeader(baseData["ip"], baseData["host"], iconSD, "STORAGE")


    draw.text((0, 23), "USED:", font=font16, fill=255)
    drawString = baseData["diskUsed"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 23), drawString, font=font16, fill=255)

    draw.text((0, 36), "TOTAL:", font=font16, fill=255)
    drawString = baseData["diskTotal"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 36), drawString, font=font16, fill=255)

    draw.text((0, 49), "UTILIZED:", font=font16, fill=255)
    drawString = baseData["diskPct"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 49), drawString, font=font16, fill=255)

    disp.image(image)
    disp.show()


def displayAds():
    displayClear()

    baseData = getBaseData()
    piHoleData = getPiHoleData()

    draw.rectangle((0, 0, displayWidth, displayHeight), outline=0, fill=0)
    drawHeader(baseData["ip"], baseData["host"], iconPiHole, "PI HOLE")


    draw.text((0, 23), "QUERIES:", font=font16, fill=255)
    drawString = piHoleData["queries"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 23), drawString, font=font16, fill=255)

    draw.text((0, 36), "CACHE:", font=font16, fill=255)
    drawString = piHoleData["cache"]
    w, h = draw.textsize(drawString, font=font16)
    draw.text((128-w, 36), drawString, font=font16, fill=255)

    drawString = piHoleData["clients"] + " IPs / " + piHoleData["ads"] + " ads"
    w, h = draw.textsize(drawString, font=font16)
    draw.text(((128 - w) / 2, 49), drawString, font=font16, fill=255)

    disp.image(image)
    disp.show()


def displayMode():
    if args.mode == "pi-hole":
        displayAds()
    elif args.mode == "hassio":
        displayAds()


def run():
    if args.mode == "blank":
        displayClear()
        exit()
    elif args.mode != "pi-hole" and args.mode != "hassio":
        exit("--mode is not defined")

    schedule.every().minute.at(":00").do(displayNetwork)
    schedule.every().minute.at(":06").do(displayCPU)
    schedule.every().minute.at(":12").do(displayRAM)
    schedule.every().minute.at(":18").do(displayStorage)
    schedule.every().minute.at(":24").do(displayMode)
    schedule.every().minute.at(":30").do(displayNetwork)
    schedule.every().minute.at(":36").do(displayCPU)
    schedule.every().minute.at(":42").do(displayRAM)
    schedule.every().minute.at(":48").do(displayStorage)
    schedule.every().minute.at(":56").do(displayMode)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run()
