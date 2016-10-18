from librerias import CronTab , Evento
from config import rss_sources as sources


class RecortesDeNoticias(object):
    _intervalo_consulta = 10

    def set_intervalo_consulta(self , minutos):
        self._intervalo_consulta = int(minutos)

    def extraer_noticias(self):
        print("Se extraeran noticias de los medios registrados cada %s minutos"  % self._intervalo_consulta)
        medios = sources.rss_sources

        eventos = []
        for id_medio , medio in medios:
            evento = Evento('extraer_'+id_medio , min=self._intervalo_consulta)
            eventos.append(
                evento
            )

        crontab = CronTab(tuple(eventos))


if __name__ == "__main__":
    recortes = RecortesDeNoticias()

    recortes.extraer_noticias()
