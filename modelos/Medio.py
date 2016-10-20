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
        parser = etree.XMLParser(remove_blank_text=True , remove_comments=True)
        telam_rss_secciones = sources.rss_sources["telam"]["secciones"]
        medio_xml = self.get_medio_xml("telam")
        root = medio_xml.getroot()

        for idseccion , url in sorted(telam_rss_secciones.items()):
            print("extract from ", idseccion ,url)
            seccion_xml = etree.XML(self.extraer_rss(url), parser)
            print(seccion_xml.findall("./channel/title")[0].text)
            noticias = seccion_xml.find('./channel')
            for noticia in noticias.findall('item'):
               self.add_to_medio_xml(noticia, "telam", idseccion , root)

        self.guardar_medio_xml("telam" , root)

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

    def guardar_medio_xml(self , idmedio, root):

        archivo_xml = os.path.join(self.sources_path, idmedio + ".xml")

        doc = etree.ElementTree(root)
        doc.write(archivo_xml, pretty_print=True, xml_declaration=True, encoding='UTF-16')



    def get_medio_xml(self , idmedio):
        medio_xml = os.path.join(self.sources_path, idmedio + ".xml")
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(medio_xml, parser)

    def get_next_id(self, medio , seccion):
        medio_xml = self.get_medio_xml(medio)
        root = medio_xml.getroot()
        print(root)
        path = "seccion[@name='"+seccion+"']/noticia"
        print(path)
        #noticias = root.find()

        #print(noticias)
        return 1

    def add_to_medio_xml(self , item , medio , seccion , root, feed='rss'):

        url = item.find('link').text

        if root.find(".//noticia[@url='"+url+"']")== None :
            seccion = root.find("seccion[@name='"+seccion+"']")

            attribs = {'id':'aca', 'url':item.find('link').text}
            noticia = etree.Element('noticia' , attrib=attribs)

            titulo = etree.SubElement(noticia , 'titulo')
            titulo.text = item.find('title').text

            descripcion = etree.SubElement(noticia , 'descripcion')
            descripcion.text = item.find('description').text

            fecha= etree.SubElement(noticia , 'fecha')
            fecha.text = item.find('pubDate').text

            seccion.append(noticia)




if __name__ == "__main__":
    medios = Medio()
    medios.extraer_telam()
