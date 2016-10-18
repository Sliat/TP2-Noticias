from librerias.CronTab import CronTab
from librerias.Evento import Evento
from modelos.Medio import Medio
from config import rss_sources as sources
import time


class RecortesDeNoticias(object):
    _intervalo_consulta = 60 #en segundos
    medio_model = Medio()

    def set_intervalo_consulta(self , minutos):
        self._intervalo_consulta = int(minutos*60)

    def extraer_noticias(self):
        intervalo = self._intervalo_consulta
        print("Se extraeran noticias de los medios registrados cada %s minutos"  % int(intervalo/60))
        medios = sources.rss_sources

        eventos = []

        for id_medio,medio in sorted(medios.items()):
            funcion = getattr(self.medio_model ,'extraer_'+id_medio)
            evento = Evento(funcion)
            eventos.append(evento)

        crontab = CronTab(intervalo , eventos)



if __name__ == "__main__":
    #Testeamos la extraccion de noticias
    #luego esto se hace desde el menu cuando comienza la aplicacion

    recortes = RecortesDeNoticias()
    recortes.set_intervalo_consulta(1)
    recortes.extraer_noticias()

    time.sleep(121)
