import os
import json
from lxml import etree
from collections import defaultdict


class Indice:
    def formar_indice(self):
        """Actualiza el indice, en caso de que no exista lo crea"""
        basic_path = os.path.join(os.path.dirname(__file__), "..", "Indice")
        try:
            self.SPIMI(json.load(open(os.path.join(basic_path, "Dic.json"))), basic_path)
        except:
            self.SPIMI({"telam": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                        "clarin": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                        "lavoz": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                        "lanacion": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                        "perfil": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}}, basic_path)
            # path = os.path.join(os.path.dirname(__file__), "..", "Indice")
            # filepath = os.path.abspath(os.path.join(path, "Dic.json"))
            # f = open(filepath, "w")
            # f.close()

    def SPIMI(self, diccionario, basic_path):
        """
        SPIMI : Single-pass in-memory indexing
        crea multiples archivos intermedios y luego los une
        :param diccionario: con los indices de los ultimos elementos agregados al indice
        :return:
        """
        for medio in diccionario.keys():
            for seccion in diccionario[medio].keys():
                vocab = defaultdict(lambda: len(vocab))
                index = defaultdict(lambda: [])
                noticias = self.obtener_noticias((medio, seccion, diccionario[medio]), basic_path)
                noticias = list(map(
                    lambda x: (self.normalizar_string(x[0]), self.normalizar_string(x[1]), diccionario[medio][seccion]),
                    noticias))
                for titulo, descripcion, id_noticia in noticias:
                    for word in titulo:
                        index[vocab[word]].append((medio, seccion, "titulo", id_noticia))
                    for word in descripcion:
                        index[vocab[word]].append((medio, seccion, "descripcion", id_noticia))
                sorted_terms = sorted(vocab.keys())
                temp = open(os.path.join(basic_path, 'spimi_block' + medio + seccion + '.txt'), 'wt')
                temp.write('\n'.join(['%d, %s' % (vocab[t], str(index[vocab[t]])) for t in sorted_terms]))
                for x in vocab.keys():
                    temp.write('\n' + str(vocab[x]) + x)
                temp.close()

    def obtener_noticias(self, posicion, basic_path):
        """
        Devuelve todas las noticias de un medio y seccion especificas a partir de un id
        :param posicion: tupla con medio, seccion, diccionario con id noticia anterior
        :return:
        """
        tree = etree.parse(os.path.join(basic_path, "..", "sources", posicion[0] + ".xml"),
                           etree.XMLParser(remove_blank_text=True))
        noticia_str = "seccion[" + posicion[1] + "]/noticia[" + str(posicion[2][posicion[1]] + 1) + "]"
        if len(tree.xpath(noticia_str)) == 0:
            return
        yield tree.xpath(noticia_str + "/titulo")[0].text, tree.xpath(noticia_str + "/descripcion")[0].text
        for noticia in tree.xpath(noticia_str)[0].itersiblings():
            posicion[2][posicion[1]] += 1
            yield (noticia.xpath("titulo")[0].text, noticia.xpath("descripcion")[0].text)

    def obtener_apariciones(self, palabra):
        """Devuelve un SET con las apariciones de la palabra"""
        pass

    def obtener_todos_docs(self):
        """Devuelve un SET con todos los docs"""
        pass

    def normalizar_string(self, str):
        """Devuelve lista de palabras normalizadas
        """
        return str.split()


# Test creacion-actualizacion indice
if __name__ == '__main__':
    Indice().formar_indice()
