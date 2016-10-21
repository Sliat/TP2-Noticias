from librerias.CronTab import CronTab
from librerias.Evento import Evento
from modelos.Medio import Medio
from config import rss_sources as sources
import functools
import time
import controladores.Indice


class RecortesDeNoticias(object):
    _intervalo_consulta = 60  # en segundos
    medio_model = Medio()

    def __init__(self):
        self.indice = controladores.Indice.Indice()

    def set_intervalo_consulta(self, minutos):
        self._intervalo_consulta = int(minutos * 60)

    def extraer_noticias(self):
        intervalo = self._intervalo_consulta
        print("Se extraeran noticias de los medios registrados cada %s minutos" % int(intervalo / 60))
        medios = sources.rss_sources

        eventos = []

        for id_medio, medio in sorted(medios.items()):
            funcion = getattr(self.medio_model, 'extraer_' + id_medio)
            evento = Evento(funcion)
            eventos.append(evento)

        crontab = CronTab(intervalo, eventos)

        # op = 1 significa titulos, op = 2 significa cuerpos
        # lugar : categorias y medios

    def ranking(self, op, lugar):
        pass

    def cantidad(self, intervalo, lugar):
        pass

    def booleana(self, consulta):
        """
        consulta : lista de tuplas de palabras y operaciones
        """
        functools.reduce(self.calculo_booleano, consulta, (set(), 1))

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
        set_y = self.obtener_set(str_next_op)
        # Si el set de una palabra no se puede obtener se ignora la operacion,
        # para evitar la nulidad de una busqueda debido a un str vacio o una stop word
        if len(set_y) == 0:
            return set_op[0], str_next_op[1]
        return operaciones[set_op[1]](set_op[0], str_next_op[0]), str_next_op[1]

    def obtener_set(self, string):
        palabras = self.indice.normalizar_string(string)
        set_final = set()
        if len(palabras) == 1:
            set_final = self.indice.obtener_apariciones(palabras[0])
        elif len(palabras) > 1:
            set_final = self.indice.obtener_apariciones(palabras[0])
            for i in range(0, len(palabras) - 2):
                set_final = self.calculo_booleano((self.indice.obtener_apariciones(palabras[i])), 3), \
                            (palabras[i + 1], 3)[0]
        return self.indice.obtener_apariciones(string)


if __name__ == "__main__":
    # Testeamos la extraccion de noticias
    # luego esto se hace desde el menu cuando comienza la aplicacion

    recortes = RecortesDeNoticias()
    recortes.set_intervalo_consulta(1)
    recortes.extraer_noticias()

    time.sleep(121)
