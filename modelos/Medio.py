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
from datetime import datetime

class Medio(object):
    medios = sources.rss_sources
    sources_path = os.path.join(os.path.dirname(__file__),"..","sources")
    def __init__(self):
        # Chequeamos si existen medios nuevos agregados y creamos un xml con nuestra estructura en blanco.
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

    def extraer_noticias_medios(self):
        for idmedio, medio in sorted(sources.rss_sources.items()):
            feed = medio["feed"]
            feed_extractor = getattr(self, 'extraer_'+feed)
            feed_extractor(idmedio)

    def extraer_rss(self,idmedio):

        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, encoding='utf-8')

        telam_rss_secciones = sources.rss_sources[idmedio]["secciones"]
        medio_xml = self.get_medio_xml(idmedio)
        root = medio_xml.getroot()

        for idseccion, url in sorted(telam_rss_secciones.items()):
            print("extract from ", idseccion, url)

            seccion_xml = etree.XML(self.extraer_feed(url), parser)
            print(seccion_xml.findall("./channel/title")[0].text)

            noticias = seccion_xml.find('./channel')
            next_id = self.get_next_id(idmedio, idseccion)
            for noticia in noticias.findall('item'):
                noticia_ya_agregada = self.add_from_rss(noticia, idmedio, idseccion, root, next_id)

                if not noticia_ya_agregada:
                    next_id += 1

        self.guardar_medio_xml(idmedio, root)

    def extraer_atom(self, idmedio):
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

        medio_rss_secciones = sources.rss_sources[idmedio]["secciones"]
        medio_xml = self.get_medio_xml(idmedio)
        root = medio_xml.getroot()

        for idseccion, url in sorted(medio_rss_secciones.items()):
            print("extract from ", idseccion, url)

            seccion_xml = etree.XML(self.extraer_feed(url), parser)

            # Atom usa namespaces por eso cuesta hacer el find. Con esto se arregla y se busca
            # normalmente, sino habria que usar XPATH directamente que igual lo necesita

            ns = 'http://www.w3.org/2005/Atom'
            ns_map = {'ns': ns}

            title = seccion_xml.find('ns:title', namespaces=ns_map)
            print(title.text)
            next_id = self.get_next_id(idmedio, idseccion)
            for noticia in seccion_xml.findall('ns:entry', namespaces=ns_map):

                noticia_ya_agregada = self.add_from_atom(noticia, idmedio, idseccion, root, ns_map, next_id)

                if not noticia_ya_agregada:
                    next_id += 1

        self.guardar_medio_xml(idmedio, root)

    def extraer_feed(self, url):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as rss:
                datos = rss.read()
            return datos
        except:
            return None

    def create_medio_xml(self , idmedio, archivo_xml):
        root = etree.Element('medio')
        #Seteamos un id numerico como el verdadero id del xml y otro name con el id del dic de medios
        root.set("id", str(self.medios[idmedio]["id"]))
        root.set("name", idmedio)

        doc = etree.ElementTree(root)
        nombre = etree.SubElement(root , "nombre")
        nombre.text = self.medios[idmedio]["nombre"]
        seccion_index = 1
        #Las secciones no tienen id prefijados porque pueden tener diferentes secciones y con nombres parecidos
        #en el orden alfabetico de las secciones enumera los indices de las secciones
        for idseccion in sorted(self.medios[idmedio]["secciones"].keys()):
            etree.SubElement(root, 'seccion', attrib={'name':idseccion, 'id':str(seccion_index)})
            seccion_index += 1

        doc.write(archivo_xml, pretty_print=True, xml_declaration=True, encoding='UTF-16')

    def guardar_medio_xml(self , idmedio, root):

        archivo_xml = os.path.join(self.sources_path, idmedio + ".xml")

        doc = etree.ElementTree(root)
        doc.write(archivo_xml, pretty_print=True, xml_declaration=True, encoding='UTF-16')



    def get_medio_xml(self , idmedio):
        medio_xml = os.path.join(self.sources_path, idmedio + ".xml")
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(medio_xml, parser)

    def get_next_id(self, idmedio , idseccion):
        medio_xml = self.get_medio_xml(idmedio)
        root = medio_xml.getroot()
        path = "./seccion[@name='%s']/noticia" % idseccion
        noticias = root.findall(path)

        return len(noticias)+1

    def add_from_rss(self, item, idmedio, idseccion, root, next_id):

        url = item.find('link').text

        if root.find(".//noticia[@url='" + url + "']") is not None:
            return True

        seccion = root.find("seccion[@name='"+idseccion+"']")

        attribs = {'id':str(next_id), 'url':item.find('link').text}
        noticia = etree.Element('noticia' , attrib=attribs)

        titulo = etree.SubElement(noticia , 'titulo')
        titulo.text = item.find('title').text

        descripcion = etree.SubElement(noticia , 'descripcion')
        descripcion.text = self.limpiar_tags_html(item.find('description').text)

        fecha= etree.SubElement(noticia , 'fecha')
        try:
            # Algunos diarios omiten las fechas en los rss, generamos el nuestro con
            # la fecha de extraccion

            fecha.text = item.find('pubDate').text
        except AttributeError:
            fecha.text = str(datetime.now())

        seccion.append(noticia)

    def add_from_atom(self , item , idmedio, idseccion , root, ns_map , next_id):

        url = item.find('ns:link', namespaces=ns_map).get('href')

        if root.find(".//noticia[@url='" + url + "']") is not None:
            return True
        # Agregamos un namespaces porque en Atom content esta en xhtml
        ns_map['ns-2'] = "http://www.w3.org/1999/xhtml"

        seccion = root.find("seccion[@name='" + idseccion + "']")
        attribs = {'id': str(next_id), 'url': url}
        noticia = etree.Element('noticia', attrib=attribs)

        titulo = etree.SubElement(noticia, 'titulo')
        titulo.text = item.find('ns:title', namespaces=ns_map).text

        descripcion = etree.SubElement(noticia, 'descripcion')
        descripcion.text = self.limpiar_tags_html(item.find('ns:content', namespaces=ns_map).find('ns-2:div' , namespaces=ns_map).text)

        fecha = etree.SubElement(noticia, 'fecha')
        fecha.text = item.find('ns:updated', namespaces=ns_map).text

        seccion.append(noticia)

    def limpiar_tags_html(self , html):
        import re
        limpiador = re.compile('<.*?>')
        return re.sub(limpiador, '', str(html))

if __name__ == "__main__":
    medios = Medio()
    medios.extraer_noticias_medios()
