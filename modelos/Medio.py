'''

    clase con los metodos que indican como extraer de cada medio para convertirlo en el xml fuente del indice invertido
    debemos convertir los rss de cada medio a una estructura xml compartida.
    Ejectua el metodo de la siguiente forma:
        extraer_[clave del dicc en config/rss_sources]

'''
import config.rss_sources as sources
import os
import urllib.request
from lxml import etree

class Medio(object):
    medios = sources.rss_sources
    sources_path = os.path.join(os.path.dirname(__file__),"..","sources")
    def __init__(self):
        #no hace falta bajar los rss podemos trabajarlos directamente en la generacion de
        #nuestro propio xml
        self._check_medios()

    def _check_medios(self):
        for idmedio in sorted(sources.rss_sources.keys()):
            try:
                archivo_xml = os.path.join(self.sources_path, idmedio+".xml")
                if not os.path.isfile(archivo_xml):
                   self.create_medio_xml(idmedio , archivo_xml)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def extraer_telam(self):
        telam_rss = sources.rss_sources["telam"]["secciones"]
        for id,url_seccion in telam_rss.items():
            tree = etree.parse(self.extraer_rss(url_seccion))
            print(tree)
            exit()



    def extraer_clarin(self):
        print("extraigo de clarin")

    def extraer_lanacion(self):
        print("extraigo de la nacion")

    def extraer_bbc(self):
        print("extraigo de bbc")

    def extraer_rss(self, url):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as rss:
                datos = rss.read()
            return datos
        except:
            return None

    def create_medio_xml(self , idmedio, archivo_xml):
        root = etree.Element('medio')
        root.set("id" , idmedio)
        doc = etree.ElementTree(root)
        nombre = etree.SubElement(root , "nombre")
        nombre.text = self.medios[idmedio]["nombre"]

        for idseccion in sorted(self.medios[idmedio]["secciones"].keys()):
            etree.SubElement(root, 'seccion', name=idseccion)

        doc.write(archivo_xml, pretty_print=True, xml_declaration=True, encoding='UTF-16')


if __name__ == "__main__":
    medios = Medio()
    #medios.extraer_telam()
