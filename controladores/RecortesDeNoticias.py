from librerias.CronTab import CronTab
from librerias.Evento import Evento
from modelos.Medio import Medio
from config import rss_sources as sources
import time
import controladores.Indice


class RecortesDeNoticias(object):
    _intervalo_consulta = 60  # en segundos
    medio_model = Medio()

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
        consulta : lista de listas de palabras y operaciones

        NO ESTOY SEGURO SI ESTA COSA FUNCIONA
        """
        map(lambda x: [controladores.Indice.Indice().obtener_apariciones(x[0]), x[1]], consulta)
        operaciones = {
            1: lambda x, y: x.union(y),
            2: lambda x, y: x.union(controladores.Indice.Indice().obtener_todos_docs().difference(y)),
            3: lambda x, y: x.intersection(y),
            4: lambda x, y: x.difference(y),
        }
        for i in range(0, len(consulta) - 2):
            consulta[i + 1][0] = operaciones[consulta[i][1]](consulta[i][0], consulta[i + 1][0])
        print(consulta[-1][0])


if __name__ == "__main__":
    # Testeamos la extraccion de noticias
    # luego esto se hace desde el menu cuando comienza la aplicacion

    recortes = RecortesDeNoticias()
    recortes.set_intervalo_consulta(1)
    recortes.extraer_noticias()

    time.sleep(121)
