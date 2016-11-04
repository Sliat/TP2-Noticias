import os
import json
from itertools import islice

class Ranking(object):
    _BASIC_PATH = os.path.join(os.path.dirname(__file__), "..", "Rankings")
    #De aca lo toma indice para saber cuantas va a "rankear"
    MAX_RANKED = 10
    RANK_SECTOR =  {"0": "titulo", "1": "descripcion"}
    _INDICE_SECCION = {"1": "economia", "2": "mundo", "3": "politica", "4": "sociedad", "5": "ultimas"}
    _INDICE_MEDIOS = {"1": "telam", "2": "clarin", "3": "lavoz", "4": "lanacion", "5": "perfil"}

    def __init__(self):
        for idsector, sector in sorted(self.RANK_SECTOR.items()):
            try:
                archivo_json = os.path.join(self._BASIC_PATH, "ranking_"+sector + ".json")
                if not os.path.isfile(archivo_json):
                    diccionario = {}
                    for k,m in sorted(self._INDICE_MEDIOS.items()):
                        secciones = diccionario.setdefault(m , {})
                        for i , s in sorted(self._INDICE_SECCION.items()):
                            secciones.setdefault(s , {})

                        diccionario[m] = secciones

                    json.dump(diccionario, open(archivo_json, "w"))

            except IOError:
                print("Hubo un problema al generar los json de rankings")

        #Seteamos los path
        self.path_ranking_titulo = os.path.join(self._BASIC_PATH, 'ranking_descripcion.json')
        self.path_ranking_descripcion = os.path.join(self._BASIC_PATH, 'ranking_titulo.json')

        #Seteamos los dict
        self.ranking_descripcion = json.load(open(self.path_ranking_descripcion))
        self.ranking_titulo = json.load(open(self.path_ranking_titulo))

    def create_ranking_json(i):
        pass

    def get_ranking_descripcion(self , idmedio = None , idseccion = None):
        return json.load(open(os.path.join(self._BASIC_PATH , 'ranking_descripcion.json')))

        #Aca podemos filtrarlo para mostrarlo en el menu, sino lo devolvemos entero sera para actualizarlo

    def get_ranking_titulo(self , idmedio = None , idseccion = None):
        ranking_titulo = json.load(open(os.path.join(self._BASIC_PATH , 'ranking_titulo.json')))

        # Aca podemos filtrarlo para mostrarlo en el menu, sino lo devolvemos entero sera para actualizarlo
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
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            #ACA construyo el indice
            #acordate aca de cambiarlo en indice
            spimi = os.path.join(self._BASIC_PATH,'..', 'Indice', 'spimi' + self._INDICE_MEDIOS[medio] + '.txt')
            self.actualizar_ranking_medio(medio,spimi)

            self.guardar_rankings()

    def actualizar_ranking_medio(self, medio , spimi):
        (medio , archivo) = (self._INDICE_MEDIOS[medio] , open(spimi , encoding='latin-1'))
        print(medio)
        import re
        for line in archivo:
            palabra , ubicaciones = line.split(';')
            ubicaciones = re.sub(r'\n' , '', ubicaciones).split(',')
            self.add_to_ranking(palabra , ubicaciones)

    def add_to_ranking(self, palabra, ubicaciones):
        print(palabra)
        for u in ubicaciones:
            str_u = str(u)
            medio , seccion_sector = int(str_u[0:1]) , int(str_u[1:2])
            sector = int((seccion_sector%2))
            seccion = int((seccion_sector/2)+1)

            if sector == 0:
                freq = self.ranking_titulo[self._INDICE_MEDIOS[str(medio)]][self._INDICE_SECCION[str(seccion)]].setdefault(palabra, 0)
                self.ranking_titulo[self._INDICE_MEDIOS[str(medio)]][self._INDICE_SECCION[str(seccion)]][palabra] = freq + 1

            else:
                freq = self.ranking_descripcion[self._INDICE_MEDIOS[str(medio)]][self._INDICE_SECCION[str(seccion)]].setdefault(palabra, 0)
                self.ranking_descripcion[self._INDICE_MEDIOS[str(medio)]][self._INDICE_SECCION[str(seccion)]][palabra] = freq + 1

    def guardar_rankings(self):

        #Falta el slice para cortarlos a los N rankeados

        json.dump(self.ranking_descripcion, open(self.path_ranking_descripcion, "w"))
        json.dump(self.ranking_titulo, open(self.path_ranking_titulo, "w"))





# Test creacion-actualizacion indice
if __name__ == '__main__':
    print("Esto es el ranking que consume de indice y es consumido desde el recortes de noticias")
    ranking = Ranking()
    #print(ranking.ranking_cuerpo , ranking.ranking_titulo)
    ranking.actualizar_raking()
