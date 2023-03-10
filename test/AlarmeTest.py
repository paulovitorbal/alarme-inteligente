import unittest
import sys

# setting path
sys.path.append('..')
from alarme import Alarme
from alarme import DURACAO_SONECA


class AlarmeTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_criar_alarme_com_dia_da_semana_0(self):
        alarme = Alarme(5, 0, [0, 8])
        self.assertFalse(alarme.tocar())

    @unittest.expectedFailure
    def test_criar_alarme_com_hora_negativa(self):
        alarme = Alarme(-1, 0, [1])
        self.assertFalse(alarme.tocar())

    @unittest.expectedFailure
    def test_criar_alarme_com_hora_25(self):
        alarme = Alarme(25, 0, [1])
        self.assertFalse(alarme.tocar())

    @unittest.expectedFailure
    def test_criar_alarme_com_minuto_negativo(self):
        alarme = Alarme(0, -1, [1])
        self.assertFalse(alarme.tocar())

    @unittest.expectedFailure
    def test_criar_alarme_com_minuto_sessenta(self):
        alarme = Alarme(0, 60, [1])
        self.assertFalse(alarme.tocar())

    def test_alarme_dispara_no_horario_especifico(self):
        alarme = Alarme(5, 0, [1])
        alarme.match(5 * 60, 1)
        self.assertEqual(True, alarme.tocar())
        self.assertEqual(False, alarme.soneca_ativada)
        self.assertEqual(True, alarme.disparado)

    def test_alarme_disparado_entra_modo_soneca(self):
        alarme = Alarme(5, 0, [1])
        alarme.match(5 * 60, 1)
        alarme.soneca()
        self.assertEqual(False, alarme.tocar())
        self.assertEqual(5 * 60 + DURACAO_SONECA, alarme.alarme)
        self.assertEqual(True, alarme.soneca_ativada)
        self.assertEqual(True, alarme.disparado)
        self.assertEqual(5 * 60, alarme.disparado_em)

    def test_alarme_disparado_eh_desativado(self):
        alarme = Alarme(5, 0, [1])
        alarme.match(5 * 60, 1)
        self.assertEqual(False, alarme.skip)
        alarme.cancelar_alarme()
        self.assertEqual(True, alarme.skip)
        self.assertEqual(False, alarme.tocar())
        self.assertEqual(5 * 60, alarme.alarme)
        self.assertEqual(False, alarme.soneca_ativada)
        self.assertEqual(False, alarme.disparado)
        self.assertEqual(None, alarme.disparado_em)
        alarme.match(301, 1)  # proximo minuto
        self.assertEqual(False, alarme.skip)

    def test_alarme_nao_dispara_em_outro_horario(self):
        alarme = Alarme(5, 0, [1])
        alarme.match(299, 1)
        self.assertEqual(False, alarme.tocar())

    def test_alarme_nao_dispara_em_outro_horario2(self):
        alarme = Alarme(5, 0, [1])
        alarme.match(391, 1)
        self.assertEqual(False, alarme.tocar())

    def test_alarme_nao_dispara_em_outro_dia_da_semana(self):
        alarme = Alarme(5, 0, [1])
        alarme.match(300, 2)
        self.assertEqual(False, alarme.tocar())


if __name__ == '__main__':
    unittest.main()
