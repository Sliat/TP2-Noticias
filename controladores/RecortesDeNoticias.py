import functools
import time
import json
import os
from lxml import etree
import modelos.Indice
from config import rss_sources as sources
from librerias.CronTab import CronTab
from librerias.Evento import Evento
from modelos.Medio import Medio
from modelos.Ranking import Ranking
import operator


class RecortesDeNoticias(object):
    _intervalo_consulta = 60  # en segundos
    medio_model = Medio()
    NOTICIAS_MAXIMAS_PARA_MOSTRAR = 25

    def __init__(self):
        self.indice = modelos.Indice.Indice()
        self.ranking = Ranking()

    def set_intervalo_consulta(self, minutos):
        self._intervalo_consulta = int(minutos * 60)

    def extraer_noticias(self):
        intervalo = self._intervalo_consulta
        # print("Se extraeran noticias de los medios registrados cada %s minutos" % int(intervalo / 60))
        medios = sources.rss_sources

        eventos = []

        for idmedio, medio in sorted(medios.items()):
            funcion = getattr(self.medio_model, 'extraer_' + medio["feed"])
            evento = Evento(funcion, idmedio)
            eventos.append(evento)

        CronTab(intervalo, eventos)

        # op = 1 significa titulos, op = 2 significa cuerpos
        # lugar : categorias y medios

    def mostrar_ranking(self, op, lugar):
        idmedio, idseccion = lugar
        ranking_seleccinado = self.ranking.get_ranking(op, idmedio, idseccion)
        print("\tRanking de las %s palabras más mencionadas en %s de noticias:" % (
            self.ranking.MAX_RANKED, self.ranking.RANK_SECTOR[str(op)]))
        print("\tMedio: %s - Seccion: %s" % (
            self.medio_model.medios[self.ranking.INDICE_MEDIOS[str(idmedio)]]["nombre"],
            self.ranking.INDICE_SECCION[str(idseccion)].title()))
        puesto = 1
        for palabra in sorted(ranking_seleccinado, key=ranking_seleccinado.get, reverse=True):
            print("\t\tPuesto %s : \"%s\" con %s apariciones" % (puesto, palabra, ranking_seleccinado[palabra]))
            puesto += 1

    def cantidad(self, intervalo, lugar):
        """
        :param intervalo: tupla inicio, fin en formato (MM,DD,HH)
        :param lugar: tupla con medio y categoria
        :return:
        """
        lugares = self.calcular_lugares(lugar)
        cantidades = json.load(
            open(os.path.abspath(os.path.join(modelos.Indice.Indice()._BASIC_PATH, "cantidad.json")), "r"))
        total = 0
        for lugar in lugares:
            total += self.sumar_cantidad_noticias(intervalo, lugar, cantidades)
        print("Hay " + str(total) + " noticias en el intervalo especificado")

    def ranking_categorias(self, intervalo):
        categorias = {}
        cantidades = json.load(
            open(os.path.abspath(os.path.join(modelos.Indice.Indice()._BASIC_PATH, "cantidad.json")), "r"))
        for seccion in range(1, 6):
            categorias[seccion] = 0
            for medio in range(1, 6):
                categorias[seccion] += self.sumar_cantidad_noticias(intervalo, (medio, seccion), cantidades)
        categorias = sorted(categorias.items(), key=operator.itemgetter(1))
        for i in range(4, -1, -1):
            print("Posicion " + str((i * -1) + 5) + ": " + modelos.Indice.Indice()._INDICE_SECCION[str(
                categorias[i][0])] + " con " + str(categorias[i][1]) + " notcias")

    def calcular_lugares(self, lugar):
        """Si se elijieron multiples lugares genera la lista con todos los indices"""
        if (lugar[0] != 0 and lugar[1] != 0):
            return [lugar]
        resultado = []
        if (lugar[0] != 0):
            medio = lugar[0]
            for i in range(1, 6):
                resultado.append((medio, i))
        elif (lugar[1] != 0):
            seccion = lugar[1]
            for i in range(1, 6):
                resultado.append((i, seccion))
        else:
            for i in range(1, 6):
                for j in range(1, 6):
                    resultado.append((i, j))
        return resultado

    def sumar_cantidad_noticias(self, intervalo, lugar, cantidades):
        total = 0
        total += self.contar_noticias((intervalo[0][0] + 1, intervalo[1][0]), (1, 32),
                                      (intervalo[0][2], intervalo[1][2] + 1), lugar, cantidades)
        if (intervalo[0][0] == intervalo[1][0]):
            total += self.contar_noticias((intervalo[0][0], intervalo[0][0] + 1), (intervalo[0][1], intervalo[1][1]),
                                          (intervalo[0][2], intervalo[1][2] + 1), lugar, cantidades)
        else:
            total += self.contar_noticias((intervalo[0][0], intervalo[0][0] + 1), (intervalo[0][1], 32),
                                          (intervalo[0][2], intervalo[1][2] + 1), lugar, cantidades)
            total += self.contar_noticias((intervalo[1][0], intervalo[1][0] + 1), (1, intervalo[1][1]),
                                          (intervalo[0][2], intervalo[1][2] + 1), lugar, cantidades)
        return total

    def contar_noticias(self, meses, dias, horas, lugar, cantidades):
        """
        :param meses: tupla inicio, fin en formato MM
        :param dias: tupla inicio, fin en formato MM
        :param horas: tupla inicio, fin en formato MM
        :param lugar: tupla con medio y categoria
        :param dic: diccionario de cantidades
        :return: int con la cantidad de noticias
        """
        total = 0
        for mes in range(meses[0], meses[1]):
            for dia in range(dias[0], dias[1]):
                for hora in range(horas[0], horas[1]):
                    fecha = str(mes).zfill(2) + str(dia).zfill(2) + str(hora).zfill(2)
                    total += cantidades.get((str(lugar[0]) + str(lugar[1]) + fecha), 0)
        return total

    def booleana(self, consulta):
        """
        consulta : lista de tuplas de palabras y operaciones
        """
        resultado = sorted(list(functools.reduce(self.calculo_booleano, consulta, (set(), 1))[0]))
        if (len(resultado) == 0):
            print("No hay coincidencias")
        elif (len(resultado) > self.NOTICIAS_MAXIMAS_PARA_MOSTRAR):
            print("Se encontraron demasiados resultados, repita la busqueda con una consulta mas especifica")
        else:
            self.mostrar_noticias(resultado)

    def mostrar_noticias(self, resultado):
        """
        muestra por consola las noticias en la lista de resultados
        :param resultado: lista ordenada de apariciones
        """
        print("-" * 30)
        medio = '1'
        seccion = '1'
        indice = modelos.Indice.Indice()
        while (resultado):
            # si no hay resultados en un medio pasa al siguiente
            if resultado[0][0] != medio:
                medio = resultado[0][0]
                continue
            tree = etree.parse(os.path.join(indice._BASIC_PATH, "..", "sources", indice._INDICE_MEDIOS[medio] + ".xml"),
                               etree.XMLParser(remove_blank_text=True))
            while (resultado[0][0] == medio):
                noticia = resultado.pop(0)
                busqueda = "seccion[" + noticia[1] + "]/noticia[" + noticia[2:] + "]"
                noticia = tree.xpath(busqueda)[0]
                print(noticia.xpath("titulo")[0].text)
                print(noticia.xpath("descripcion")[0].text)
                print("-" * 30)
                if not resultado:
                    return

    def calculo_booleano(self, set_op, str_next_op):
        """
        utiliza el mismo codigo que Menu.consulta_booleana
        1: "or",
        2: "or not",
        3: "and",
        4: "and not",
        :param set_op: tupla con el set de apariciones y la operacion a realizar
        :param str_next_op: str y proxima operacion
        :return: tupla con la operacion realizada entre ambos sets y la proxima operacion
        """
        operaciones = {
            1: lambda x, y: x.union(y),
            2: lambda x, y: x.union(self.indice.obtener_todos_docs().difference(y)),
            3: lambda x, y: x.intersection(y),
            4: lambda x, y: x.difference(y),
        }
        set_y = self.obtener_set(str_next_op[0])
        # Si el set de una palabra no se puede obtener se ignora la operacion,
        # para evitar la nulidad de una busqueda debido a un str vacio o una stop word
        if len(set_y) == 0:
            return set_op[0], str_next_op[1]
        return operaciones[set_op[1]](set_op[0], set_y), str_next_op[1]

    def obtener_set(self, string):
        palabras = self.indice.normalizar_string(string)
        set_final = set()
        if len(palabras) == 1:
            set_final = self.indice.obtener_apariciones(palabras[0])
        elif len(palabras) > 1:
            set_final = self.indice.obtener_apariciones(palabras[0])
            for i in range(0, len(palabras) - 1):
                set_final = self.calculo_booleano((set_final, 3), (palabras[i + 1], 3))[0]
        return set_final


if __name__ == "__main__":
    # Testeamos la extraccion de noticias
    # luego esto se hace desde el menu cuando comienza la aplicacion

    recortes = RecortesDeNoticias()
    recortes.set_intervalo_consulta(1)
    recortes.extraer_noticias()

    time.sleep(121)
