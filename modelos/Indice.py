# -*- coding: 850 -*-
import os
import json
import re
from lxml import etree
from nltk.stem import SnowballStemmer
from functools import reduce


class Indice:
    _INDICE_MEDIOS = {"1": "telam", "2": "clarin", "3": "lavoz", "4": "lanacion", "5": "perfil"}
    _INDICE_SECCION = {"1": "economia", "2": "mundo", "3": "politica", "4": "sociedad", "5": "ultimas"}
    _INDICE_ELEMENTO = {"1": "titulo", "2": "descripcion"}
    _WORD_MIN_LENGTH = 3
    _STOP_WORDS = frozenset(['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los',
                             'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es',
                             'lo', 'como', 'm s', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha', 's¡',
                             'porque', 'esta', 'son', 'entre', 'est ', 'cuando', 'muy', 'sin', 'sobre',
                             'ser', 'tiene', 'tambi‚n', 'me', 'hasta', 'hay', 'donde', 'han', 'quien',
                             'est n', 'estado', 'desde', 'todo', 'nos', 'durante', 'estados', 'todos',
                             'uno', 'les', 'ni', 'contra', 'otros', 'fueron', 'ese', 'eso', 'hab¡a',
                             'ante', 'ellos', 'e', 'esto', 'm¡', 'antes', 'algunos', 'qu‚', 'unos', 'yo',
                             'otro', 'otras', 'otra', '‚l', 'tanto', 'esa', 'estos', 'mucho', 'quienes',
                             'nada', 'muchos', 'cual', 'sea', 'poco', 'ella', 'estar', 'haber', 'estas',
                             'estaba', 'estamos', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 't£', 'te',
                             'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'm¡o',
                             'm¡a', 'm¡os', 'm¡as', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya',
                             'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro',
                             'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'est s', 'est ',
                             'estamos', 'est is', 'est n', 'est‚', 'est‚s', 'estemos', 'est‚is', 'est‚n',
                             'estar‚', 'estar s', 'estar ', 'estaremos', 'estar‚is', 'estar n', 'estar¡a',
                             'estar¡as', 'estar¡amos', 'estar¡ais', 'estar¡an', 'estaba', 'estabas',
                             'est bamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo',
                             'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras',
                             'estuvi‚ramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses',
                             'estuvi‚semos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada',
                             'estados', 'estadas', 'estad', 'none', 'he', 'has', 'ha', 'hemos', 'hab‚is', 'han',
                             'haya', 'hayas', 'hayamos', 'hay is', 'hayan', 'habr‚', 'habr s', 'habr ',
                             'habremos', 'habr‚is', 'habr n', 'habr¡a', 'habr¡as', 'habr¡amos', 'habr¡ais',
                             'habr¡an', 'hab¡a', 'hab¡as', 'hab¡amos', 'hab¡ais', 'hab¡an', 'hube',
                             'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
                             'hubi‚ramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubi‚semos',
                             'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
                             'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'se is',
                             'sean', 'ser‚', 'ser s', 'ser ', 'seremos', 'ser‚is', 'ser n', 'ser¡a',
                             'ser¡as', 'ser¡amos', 'ser¡ais', 'ser¡an', 'era', 'eras', '‚ramos', 'erais',
                             'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera',
                             'fueras', 'fu‚ramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fu‚semos',
                             'fueseis', 'fuesen', 'siendo', 'sido', 'sed', 'tengo', 'tienes', 'tiene',
                             'tenemos', 'ten‚is', 'tienen', 'tenga', 'tengas', 'tengamos', 'teng is',
                             'tengan', 'tendr‚', 'tendr s', 'tendr ', 'tendremos', 'tendr‚is', 'tendr n',
                             'tendr¡a', 'tendr¡as', 'tendr¡amos', 'tendr¡ais', 'tendr¡an', 'ten¡a',
                             'ten¡as', 'ten¡amos', 'ten¡ais', 'ten¡an', 'tuve', 'tuviste', 'tuvo',
                             'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuvi‚ramos',
                             'tuvierais', 'tuvieran', 'tuviese', 'tuvieses', 'tuvi‚semos', 'tuvieseis',
                             'tuviesen', 'teniendo', 'tenido', 'tenida', 'tenidos', 'tenidas', 'tened', ''])

    def formar_indice(self):
        """Actualiza el indice, en caso de que no exista lo crea"""
        basic_path = os.path.join(os.path.dirname(__file__), "..", "Indice")
        try:
            diccionario = json.load(open(os.path.join(basic_path, "Dic.json")))
        except:
            diccionario = {"1": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "2": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "3": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "4": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "5": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}}
        self.SPIMI(diccionario, basic_path)
        json.dump(diccionario, open(os.path.abspath(os.path.join(basic_path, "Dic.json")), "w"))
        self.merge(basic_path, 4)
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            os.remove(os.path.join(basic_path, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'))

    def SPIMI(self, diccionario, basic_path):
        """
        SPIMI : Single-pass in-memory indexing
        crea multiples archivos intermedios con termino : postings
        :param diccionario: con los indices de los ultimos elementos agregados al indice
        :return:
        """
        for medio in diccionario.keys():
            indice = {}
            for seccion in sorted(diccionario[medio].keys()):
                noticias = self.obtener_noticias((medio, seccion, diccionario[medio]), basic_path)
                noticias = list(map(
                    lambda x: (self.normalizar_string(x[0]), self.normalizar_string(x[1]), diccionario[medio][seccion]),
                    noticias))
                for titulo, descripcion, id_noticia in noticias:
                    for word in titulo:
                        indice.setdefault(word, []).append(
                            (medio + str((int(seccion) * 2) - 2) + '{0:03d}'.format(id_noticia)))
                for titulo, descripcion, id_noticia in noticias:
                    for word in descripcion:
                        indice.setdefault(word, []).append(
                            (medio + str((int(seccion) * 2) - 1) + '{0:03d}'.format(id_noticia)))
            temp = open(os.path.join(basic_path, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'), 'wt')
            for termino in sorted(indice.keys()):
                temp.write(termino + ';' + ''.join([str(x) + ',' for x in indice[termino]])[:-1] + "\n")
            temp.close()

    def obtener_noticias(self, posicion, basic_path):
        """
        :param posicion: tupla con medio, seccion, diccionario con id noticia anterior
        :return: todas las noticias de un medio y seccion especificas a partir de un id
        """
        tree = etree.parse(os.path.join(basic_path, "..", "sources", self._INDICE_MEDIOS[posicion[0]] + ".xml"),
                           etree.XMLParser(remove_blank_text=True))
        noticia_str = "seccion[" + posicion[1] + "]/noticia[" + str(posicion[2][posicion[1]] + 1) + "]"
        if len(tree.xpath(noticia_str)) == 0:
            return
        posicion[2][posicion[1]] += 1
        yield tree.xpath(noticia_str + "/titulo")[0].text, tree.xpath(noticia_str + "/descripcion")[0].text
        for noticia in tree.xpath(noticia_str)[0].itersiblings():
            posicion[2][posicion[1]] += 1
            yield (noticia.xpath("titulo")[0].text, noticia.xpath("descripcion")[0].text)

    def normalizar_string(self, str):
        """ :return: lista de palabras normalizadas"""
        stemmer = SnowballStemmer('spanish')
        str = re.split(r"[0-9_\W]", str)
        words = []
        for word in str:
            if word != "" and word not in self._STOP_WORDS and len(word) >= self._WORD_MIN_LENGTH:
                words.append(stemmer.stem(word))
        return words

    def merge(self, basic_path, block_size):
        """
        Unifica los archivos intermedios creados por SPIMI en un indice comprimido que consiste en un "block storage"
        con las palabras y una estructura auxiliar con los postings y referencias al "block storage"
        :param basic_path: path de la carpeta Indice donde se encuentras los archivos
        :param block_size: tama¤o de cada bloque en el "block storage"
        """
        intermedios = []
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            intermedios.append(open(os.path.join(basic_path, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'), 'rt'))
        lineas = []
        for archivo in intermedios:
            linea = archivo.readline().split(";")
            if len(linea[0]) != 0:
                lineas.append(archivo.readline().split(";"))
            else:
                archivo.close()
        actualizacion = False
        if lineas:
            try:
                intermedios.append(self.descomprimir_indice(basic_path))
                lineas.append(intermedios[-1].readline().split(";"))
                actualizacion = True
            except:
                pass
        block_storage = open(os.path.join(basic_path, "block_storage.txt"), 'wt' , encoding='ISO-8859-1')
        estructura_auxiliar = open(os.path.join(basic_path, "estructura_auxiliar.txt"), 'wt')
        postings_list = open(os.path.join(basic_path, "postings_list.txt"), 'wt')
        indice_block = 0
        indice_postings = 0
        postings = []
        salto_block = 0
        while lineas:
            palabra = lineas[0][0]
            apariciones = []
            for x in range(0, len(lineas)):
                if lineas[x][0] < palabra:
                    palabra = lineas[x][0]
                    apariciones = [x]
                elif lineas[x][0] == palabra:
                    apariciones.append(x)
            resultado = ""
            for i in apariciones:
                resultado += lineas[i][1][:-1] + ","
                lineas[i] = intermedios[i].readline().split(";")
                if len(lineas[i][0]) == 0:
                    intermedios[i].close()
                    del (intermedios[i])
                    del (lineas[i])
                    for i in range(0, len(apariciones)):
                        apariciones[i] -= 1
            block_storage.write(str(len(palabra)) + palabra)
            postings.append(resultado[:-1])
            salto_block += len(str(len(palabra))) + len(palabra)
            if len(postings) == block_size:
                post_compr = self.comprimir_postings(postings, indice_postings)
                postings_list.write(post_compr[0])
                estructura_auxiliar.write(str(indice_block) + "-" + post_compr[1] + ";")
                indice_postings += len(post_compr[0])
                postings = []
                indice_block += salto_block
                salto_block = 0
        if len(postings) != 0:
            post_compr = self.comprimir_postings(postings, indice_postings)
            postings_list.write(post_compr[0])
            estructura_auxiliar.write(str(indice_block) + "-" + post_compr[1] + ";")
        estructura_auxiliar.close()
        postings_list.close()
        block_storage.close()
        if actualizacion:
            lineas[0].close()
            os.remove(os.path.join(basic_path, "temporal_previo.txt"))

    def comprimir_postings(self, postings, ref):
        """
        :param postings: string con los postings
        :return: string comprimido con los postings
        """
        res = ""
        for post in postings:
            elementos = post.split(",")
            res += elementos[0]
            for i in range(len(elementos) - 1, 0, -1):
                elementos[i] = str(int(elementos[i]) - int(elementos[i - 1]))
            for i in range(1, len(elementos)):
                res += "+" + elementos[i]
            res += ","
        posiciones = []
        for x in res[:-1].split(","):
            posiciones.append(ref)
            ref += len(x) + 1
        pos_str = ""
        for i in range(0, len(posiciones)):
            pos_str += str(posiciones[i]) + ","
        return res, pos_str[:-1]

    def descomprimir_indice(self, basic_path):
        block_storage = open(os.path.join(basic_path, "block_storage.txt"), 'rt' , encoding='ISO-8859-1')
        postings_list = open(os.path.join(basic_path, "postings_list.txt"), 'rt')
        temporal_previo = open(os.path.join(basic_path, "temporal_previo.txt"), 'wt')
        for block in open(os.path.join(basic_path, "estructura_auxiliar.txt"), 'rt').read()[:-1].split(";"):
            indice_palabra = int(block.split("-")[0])
            for posting in block.split("-")[1].split(","):
                post_list = ""
                cont = True
                postings_list.seek(int(posting))
                while cont:
                    temp = postings_list.read(1)
                    cont = temp != ","
                    if cont:
                        post_list += temp
                post_list = post_list.split("+")
                for i in range(1, len(post_list)):
                    post_list[i] = str(int(post_list[i]) + int(post_list[i - 1]))
                post_str = ""
                for post in post_list:
                    post_str += post + ","
                block_storage.seek(indice_palabra)
                longitud_palabra = block_storage.read(1)
                indice_palabra += 1
                continuar = True
                while (continuar):
                    temp = block_storage.read(1)
                    continuar = temp.isdigit()
                    if continuar:
                        longitud_palabra += temp
                        indice_palabra += 1
                block_storage.seek(indice_palabra)
                if len(longitud_palabra) != 0:
                    palabra = block_storage.read(int(longitud_palabra))
                    temporal_previo.write(palabra + ";" + post_str + "\n")
                    indice_palabra += len(palabra)
        block_storage.close()
        postings_list.close()
        temporal_previo.close()
        return open(os.path.join(basic_path, "temporal_previo.txt"), 'rt')

    def buscar_palabra(self, palabra):
        """INCOMPLETO
        """
        palabra = self.normalizar_string(palabra)
        file = open(os.path.join(os.path.dirname(__file__), "..", "Indice", "block_storage.txt"), "r")
        file.close()

    def obtener_apariciones(self, palabra):
        """Devuelve un SET con las apariciones de la palabra"""
        pass

    def obtener_todos_docs(self):
        """Devuelve un SET con todos los docs"""
        pass


# Test creacion-actualizacion indice
if __name__ == '__main__':
    Indice().formar_indice()
    # Indice().merge(os.path.join(os.path.dirname(__file__), "..", "Indice"), 4)
    Indice().descomprimir_indice(os.path.join(os.path.dirname(__file__), "..", "Indice"))
