import os
import json


class Ranking(object):
    _BASIC_PATH = os.path.join(os.path.dirname(__file__), "..", "Rankings")

    MAX_RANKED = 10
    RANK_SECTOR =  {"1": "titulo", "2": "descripcion"}
    INDICE_SECCION = {"1": "economia", "2": "mundo", "3": "politica", "4": "sociedad", "5": "ultimas", "0": "global"}
    INDICE_MEDIOS = {"1": "telam", "2": "clarin", "3": "lavoz", "4": "lanacion", "5": "perfil", "0": "global"}

    def __init__(self):
        for idsector, sector in sorted(self.RANK_SECTOR.items()):
            try:
                archivo_json = os.path.join(self._BASIC_PATH, "frecuencias_"+sector + ".json")
                if not os.path.isfile(archivo_json):
                    diccionario = {}
                    for k,m in sorted(self.INDICE_MEDIOS.items()):
                        secciones = diccionario.setdefault(m , {})
                        for i , s in sorted(self.INDICE_SECCION.items()):
                            secciones.setdefault(s , {})

                        diccionario[m] = secciones

                    json.dump(diccionario, open(archivo_json, "w"))

            except IOError:
                print("Hubo un problema al generar los json de rankings")

        #Seteamos los path
        self.path_freq_titulo = os.path.join(self._BASIC_PATH, 'frecuencias_titulo.json')
        self.path_freq_descripcion = os.path.join(self._BASIC_PATH, 'frecuencias_descripcion.json')

        self.path_ranking_descripcion = os.path.join(self._BASIC_PATH, 'ranking_descripcion.json')
        self.path_ranking_titulo = os.path.join(self._BASIC_PATH, 'ranking_titulo.json')

        # Seteamos los dict
        self.frecuencia_descripcion = json.load(open(self.path_freq_descripcion , 'r+'))
        self.frecuencia_titulo = json.load(open(self.path_freq_titulo , 'r+'))

    def get_ranking_descripcion(self , idmedio = None , idseccion = None):
        ranking_descripcion = json.load(open(os.path.join(self._BASIC_PATH , 'ranking_descripcion.json')))

        if idmedio is not None and idseccion is not None:
            return ranking_descripcion[self.INDICE_MEDIOS[str(idmedio)]][self.INDICE_SECCION[str(idseccion)]]

        return ranking_descripcion

    def get_ranking_titulo(self , idmedio = None , idseccion = None):


        ranking_titulo = json.load(open(os.path.join(self._BASIC_PATH , 'ranking_titulo.json')))

        if idmedio is not None and idseccion is not None:
            return ranking_titulo[self.INDICE_MEDIOS[str(idmedio)]][self.INDICE_SECCION[str(idseccion)]]

        return ranking_titulo

    def get_ranking(self , op , idmedio , idseccion):

        ranking_seleccionado = getattr(self , "get_ranking_"+self.RANK_SECTOR[str(op)])
        return ranking_seleccionado(idmedio, idseccion)


    def actualizar_raking(self):
        '''
        Este es el metodo de rankings, como solo funciona cuando hay noticias nuevas lo hago aca para probar
        luego se llamara desde indice.formar_indice
        :return:
        '''
        for medio in sorted(self.INDICE_MEDIOS.keys()):
            if eval(medio) == 0: continue
            # ACA construyo el indice
            # acordate aca de cambiarlo en indice
            spimi = os.path.join(self._BASIC_PATH,'..', 'Indice', 'spimi' + self.INDICE_MEDIOS[medio] + '.txt')
            self.actualizar_ranking_medio(medio,spimi)


        self.guardar_rankings()

    def actualizar_ranking_medio(self, medio , spimi):
        (medio , archivo) = (self.INDICE_MEDIOS[medio] , open(spimi, encoding='latin-1'))
        import re
        for line in archivo:
            palabra , ubicaciones = line.split(';')
            ubicaciones = re.sub(r'\n' , '', ubicaciones).split(',')
            self.add_to_ranking(palabra , ubicaciones)

    def add_to_ranking(self, palabra, ubicaciones):
        #print(palabra)
        for u in ubicaciones:
            str_u = str(u)
            medio , seccion_sector = int(str_u[0:1]) , int(str_u[1:2])
            sector = int((seccion_sector%2))
            seccion = int((seccion_sector/2)+1)

            if sector == 0:

                # Seteamos la frecuencia de medio por seccion
                freq = self.frecuencia_titulo[self.INDICE_MEDIOS[str(medio)]][self.INDICE_SECCION[str(seccion)]].setdefault(palabra, 0)
                self.frecuencia_titulo[self.INDICE_MEDIOS[str(medio)]][self.INDICE_SECCION[str(seccion)]][palabra] = freq + 1

                # Seteamos la frecuencia de medio para global las secciones
                freq_medio_global = self.frecuencia_titulo[self.INDICE_MEDIOS[str(medio)]]["global"].setdefault(palabra, 0)
                self.frecuencia_titulo[self.INDICE_MEDIOS[str(medio)]]["global"][palabra] = freq_medio_global + 1


                #Seteamos la frecuencia para todos los medios para global las secciones

                freq_global_global = self.frecuencia_titulo['global']["global"].setdefault(palabra,0)
                self.frecuencia_titulo["global"]["global"][palabra] = freq_global_global + 1

                #Seteamos la frecuencia para todos los medios pero por seccion
                freq_global_seccion = self.frecuencia_titulo["global"][self.INDICE_SECCION[str(seccion)]].setdefault(palabra, 0)
                self.frecuencia_titulo["global"][self.INDICE_SECCION[str(seccion)]][palabra] = freq_global_seccion + 1

            else:
                # Seteamos la frecuencia de medio por seccion
                freq = self.frecuencia_descripcion[self.INDICE_MEDIOS[str(medio)]][self.INDICE_SECCION[str(seccion)]].setdefault(palabra, 0)
                self.frecuencia_descripcion[self.INDICE_MEDIOS[str(medio)]][self.INDICE_SECCION[str(seccion)]][palabra] = freq + 1

                # Seteamos la frecuencia de medio para global las secciones
                freq_medio_global = self.frecuencia_descripcion[self.INDICE_MEDIOS[str(medio)]]["global"].setdefault(
                    palabra, 0)
                self.frecuencia_descripcion[self.INDICE_MEDIOS[str(medio)]]["global"][palabra] = freq_medio_global + 1

                # Seteamos la frecuencia para todos los medios para global las secciones

                freq_global_global = self.frecuencia_descripcion['global']["global"].setdefault(palabra, 0)
                self.frecuencia_descripcion["global"]["global"][palabra] = freq_global_global + 1

                # Seteamos la frecuencia para todos los medios pero por seccion
                freq_global_seccion = self.frecuencia_descripcion["global"][self.INDICE_SECCION[str(seccion)]].setdefault(palabra, 0)
                self.frecuencia_descripcion["global"][self.INDICE_SECCION[str(seccion)]][palabra] = freq_global_seccion + 1

    def guardar_rankings(self):
        import collections
        ranking_descripcion = collections.OrderedDict()
        for medio , dic_medio in sorted(self.frecuencia_descripcion.items()):
            ranking_descripcion[medio] =collections.OrderedDict()
            for seccion, freqs in sorted(self.frecuencia_descripcion[medio].items()):
                ranking_descripcion[medio][seccion] = collections.OrderedDict()
                for k in sorted(freqs , key=freqs.get , reverse=True)[:self.MAX_RANKED]:
                    ranking_descripcion[medio][seccion][k] = freqs[k]

        ranking_titulo = collections.OrderedDict()

        for medio, dic_medio in sorted(self.frecuencia_titulo.items()):
            ranking_titulo[medio] = collections.OrderedDict()
            for seccion, freqs in sorted(self.frecuencia_titulo[medio].items()):
                ranking_titulo[medio][seccion] = collections.OrderedDict()
                for k in sorted(freqs, key=freqs.get, reverse=True)[:self.MAX_RANKED]:
                    ranking_titulo[medio][seccion][k] = freqs[k]

        # Rankings globales de cada medio

        # Rankings de todos los medios de global las secciones

        # Guardamos los rankings
        json.dump(ranking_descripcion, open(self.path_ranking_descripcion, "w+") ,indent=4)
        json.dump(ranking_titulo, open(self.path_ranking_titulo, "w+"), indent=4)

        # Guardamos las frecuencias para la proxima reconstruccion del indice
        json.dump(self.frecuencia_descripcion, open(self.path_freq_descripcion, "w+"), indent=4)
        json.dump(self.frecuencia_titulo, open(self.path_freq_titulo, "w+"), indent=4)


# Test creacion-actualizacion indice
if __name__ == '__main__':
    print("Esto es el ranking que consume de indice y es consumido desde el recortes de noticias")
    ranking = Ranking()
    print(ranking.INDICE_SECCION)
    ranking.actualizar_raking()
