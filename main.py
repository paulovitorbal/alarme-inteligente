from machine import Pin, SPI
import time
import utime
import onewire, ds18x20
import urequests
import random
from ubutton import uButton
import uasyncio as asyncio
import alarme

import network
# https://github.com/RaspberryPiFoundation/picozero
from picozero import Speaker
# https://github.com/mcauser/micropython-max7219
import max7219
# https://github.com/notUnique/DS3231micro
import DS3231micro

# Display
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 4)
display.brightness(1)

# rtc
rtc = DS3231micro.DS3231(i2cClockPin=7, i2cDataPin=6)

# temperatura
SensorPin = Pin(26, Pin.IN)
sensor = ds18x20.DS18X20(onewire.OneWire(SensorPin))
roms = sensor.scan()

# speaker
speaker = Speaker(14)

# wlan
wlan = network.WLAN(network.STA_IF)

# variaveis globais
relogio_sincronizado = False
lista_alarmes = []

# botoes de controle
pin8 = Pin(8, Pin.IN, Pin.PULL_UP)  # temperatura
pin9 = Pin(9, Pin.IN, Pin.PULL_UP)  # tempo
pin10 = Pin(10, Pin.IN, Pin.PULL_UP)  # sincronizar
pin11 = Pin(11, Pin.IN, Pin.PULL_UP)  # alarme


def conectar():
    global wlan
    display_text("WiFi", 1)
    ssid = "BPL"
    password = "familiabpl"

    print("Connecting to:", ssid)
    wlan.active(True)
    print("WLAN Active:", wlan.active())
    if wlan.isconnected() is False:
        attempts = 0
        wlan.connect(ssid, password)
        while wlan.isconnected() is False:
            status = wlan.status()
            if status != network.STAT_CONNECTING:
                print(f"Can't connect status={status}")
                return
            if attempts > 29:
                break
            print(f"Wifi: Waiting for connection [{attempts}]")
            attempts += 1
            time.sleep(1)

    print("Connected:", wlan.isconnected())
    display_text("OK!", 1)


def sincronizar_relogio():
    print("sincronizar")
    global rtc
    global wlan
    global relogio_sincronizado
    global lista_alarmes

    if wlan.isconnected() is False:
        conectar()
    else:
        print("wlan ok")
    if relogio_sincronizado is False:
        display_text("S Tm", 1)
        response = urequests.get(url="http://worldtimeapi.org/api/timezone/America/Sao_Paulo")
        json_object = response.json()
        unixtime = json_object["unixtime"] - (3 * 60 * 60)
        tempo = time.localtime(unixtime)
        rtc.setYear(tempo[0])
        rtc.setMonth(tempo[1])
        rtc.setDay(tempo[2])
        rtc.setDayOfWeek(tempo[6] + 1)
        rtc.setHour(tempo[3])
        rtc.setMinutes(tempo[4])
        rtc.setSeconds(tempo[5])

        response.close()
        relogio_sincronizado = True
        display_text("S Ok", 1)

    display_text("S Al", 1)

    response = urequests.get(
        url="https://gist.githubusercontent.com/paulovitorbal/67ab9bbd2787fd4a46096ede8e51b746/raw"
            "/5a3fc772e5cbbf41f90bb8d1eff84191f5e30c5a/alarme.json")

    lista_alarmes.clear()

    json_object = response.json()
    for al in json_object["alarmes"]:
        a = alarme.Alarme(al["h"], al["m"], al["dow"])
        print(a.to_string())
        lista_alarmes.append(a)

    display_text("S Ok", 1)


def ler_temperatura():
    print("ler temperatura")
    global sensor
    global roms

    sensor.convert_temp()
    for rom in roms:
        temperature = sensor.read_temp(rom)
        return temperature


def display_time():
    print("display tempo")
    global display
    global rtc
    tick = True
    for i in range(20):
        utime.sleep(0.5)
        hora = rtc.getHour()
        minuto = rtc.getMinutes()
        display.fill(0)
        display.pixel(16, 0, 1)
        display.pixel(15, 0, 1)
        display.text(f'{hora:02d}', -1, 1, 1)
        display.text(f'{minuto:02d}', 17, 1, 1)
        if tick:
            display.pixel(15, 3, 1)
            display.pixel(15, 5, 1)
            display.pixel(16, 3, 1)
            display.pixel(16, 5, 1)
            tick = False
        else:
            tick = True
        display.show()

    display.fill(0)
    display.show()


def display_text(text, tempo):
    global display
    display.fill(0)
    display.text(text, 0, 1, 1)
    display.show()
    time.sleep(tempo)
    display.fill(0)
    display.show()


def display_temperature():
    print("display temperatura")
    global display
    temp = ler_temperatura()
    display.fill(0)
    display.text(f"{temp:2.2f}", 0, 1, 1)
    display.show()
    time.sleep(2)
    display.fill(0)
    display.show()


def soar_alarme():
    global speaker
    global lista_alarmes
    alarme_ativo = False
    for al in lista_alarmes:
        if al.tocar():
            alarme_ativo = True

    if alarme_ativo:
        speaker.beep(n=1, on_time=0.1)


def acionar_botao_soneca():
    global lista_alarmes
    alarme_ativo = False
    for al in lista_alarmes:
        if al.tocar():  # pressionado enquanto o alarme estava ativo -> ativa soneca
            print("soneca ativada")
            display_text("ZzZz", 1)
            al.soneca()
            alarme_ativo = True
        elif al.soneca_ativada:  # pressionado enquanto a soneca estava ativa -> reseta o alarme
            print("reset ativado")
            display_text("Desl", 1)
            al.cancelar_alarme()
            time.sleep(1)
            alarme_ativo = True

    if alarme_ativo is False:
        for index, al in enumerate(lista_alarmes):
            display.fill(0)
            display.pixel(index, 0, 1)
            display.text(f'{al.horas:02d}', -1, 1, 1)
            display.text(f'{al.minutos:02d}', 17, 1, 1)
            display.pixel(15, 3, 1)
            display.pixel(15, 5, 1)
            display.pixel(16, 3, 1)
            display.pixel(16, 5, 1)
            display.show()
            time.sleep(1)
        display.fill(0)
        display.show()


async def verificar_alarme():
    global lista_alarmes
    print(rtc.getDayOfWeek())
    while True:
        for al in lista_alarmes:
            al.match(alarme.get_minutos_from_horas_minutos(rtc.getHour(), rtc.getMinutes()), rtc.getDayOfWeek())
        soar_alarme()
        await asyncio.sleep_ms(500)


# limpa o display
display.fill(0)
display.show()


def main():
    global pin8
    global pin9
    global pin10
    global pin11

    b8 = uButton(
        pin8,
        short_wait=True,
        cb_long=display_temperature,
        bounce_time=25,
        long_time=1000,
        act_low=False
    )
    b9 = uButton(
        pin9,
        short_wait=True,
        cb_long=display_time,
        bounce_time=25,
        long_time=1000,
        act_low=False
    )
    b10 = uButton(
        pin10,
        short_wait=True,
        cb_long=sincronizar_relogio,
        bounce_time=25,
        long_time=1000,
        act_low=False
    )
    b11 = uButton(
        pin11,
        short_wait=True,
        cb_long=acionar_botao_soneca,
        bounce_time=25,
        long_time=1000,
        act_low=False
    )

    # Get a reference to the event loop
    loop = asyncio.get_event_loop()
    # Schedule coroutines to run ASAP
    loop.create_task(b8.run())
    loop.create_task(b9.run())
    loop.create_task(b10.run())
    loop.create_task(b11.run())
    loop.create_task(verificar_alarme())

    # Run the event loop
    loop.run_forever()


if __name__ == '__main__':
    sincronizar_relogio()
    main()
