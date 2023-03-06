# This is a sample Python script.
import time
from math import floor
from typing import List

DURACAO_SONECA = 5


class Alarm:
    disparado = False
    soneca_ativada = False
    alarme = None

    def __init__(self, horas: int, minutos: int, dias_da_semana):
        if horas > 23 or horas < 0:
            raise Exception('horas em formato invalido: {}', horas)
        if minutos > 59 or minutos < 0:
            raise Exception('minutos em formato invalido: {}', minutos)
        self.horas = horas
        self.minutos = minutos
        self.dias_da_semana = dias_da_semana
        self.reset()

    def reset(self):
        self.disparado = False
        self.soneca_ativada = False
        self.alarme = get_minutos_from_horas_minutos(self.horas, self.minutos)

    def soneca(self):
        self.soneca_ativada = True
        self.alarme = self.alarme + DURACAO_SONECA

    def debug(self, horario_atual: int, dia_da_semana):
        h = get_string_from_minutos(horario_atual)
        a = get_string_from_minutos(self.alarme)
        print(
            f"horario [{h}] alarme [{a}] dow [{dia_da_semana}] disparado [{self.disparado}] soneca [{self.soneca_ativada}]"
        )

    def match(self, horario_atual: int, dia_da_semana):
        if self.alarme == horario_atual and dia_da_semana in self.dias_da_semana:
            self.disparado = True
            self.soneca_ativada = False
            self.debug(horario_atual, dia_da_semana)
            return True

        self.debug(horario_atual, dia_da_semana)
        return False


def get_string_from_minutos(minutos: int):
    horas, minutos = divmod(minutos, 60)
    return f'{horas:02}:{minutos:02}'


def get_minutos_from_time(tempo: time.struct_time):
    return get_minutos_from_horas_minutos(tempo.tm_hour, tempo.tm_min)


def get_minutos_from_horas_minutos(horas: int, minutos: int):
    return minutos + (horas * 60)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')
    print(time.localtime())
    alarmes = [Alarm(16, 34, [0, 1, 2, 3, 4])]
    while True:
        for alarme in alarmes:
            alarme.match(get_minutos_from_time(time.localtime()), time.localtime()[6])

        time.sleep(1)

#check https://awesome-micropython.com/
#https://gitlab.com/WiLED-Project/ubutton