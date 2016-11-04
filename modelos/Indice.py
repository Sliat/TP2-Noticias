import os
import json
import re
from lxml import etree
from nltk.stem import SnowballStemmer
from modelos.Ranking import Ranking


class Indice:
    _INDICE_MEDIOS = {"1": "telam", "2": "clarin", "3": "lavoz", "4": "lanacion", "5": "perfil"}
    _INDICE_SECCION = {"1": "economia", "2": "mundo", "3": "politica", "4": "sociedad", "5": "ultimas"}
    _INDICE_ELEMENTO = {"1": "titulo", "2": "descripcion"}
    _WORD_MIN_LENGTH = 4
    _BASIC_PATH = os.path.join(os.path.dirname(__file__), "..", "Indice")
    _STOP_WORDS = frozenset(['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los',
                             'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es',
                             'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha', 'sí',
                             'porque', 'esta', 'son', 'entre', 'está', 'cuando', 'muy', 'sin', 'sobre',
                             'ser', 'tiene', 'también', 'me', 'hasta', 'hay', 'donde', 'han', 'quien',
                             'están', 'estado', 'desde', 'todo', 'nos', 'durante', 'estados', 'todos',
                             'uno', 'les', 'ni', 'contra', 'otros', 'fueron', 'ese', 'eso', 'había',
                             'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo',
                             'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes',
                             'nada', 'muchos', 'cual', 'sea', 'poco', 'ella', 'estar', 'haber', 'estas',
                             'estaba', 'estamos', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te',
                             'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío',
                             'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya',
                             'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro',
                             'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'estás', 'está',
                             'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis', 'estén',
                             'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría',
                             'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas',
                             'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo',
                             'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras',
                             'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses',
                             'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada',
                             'estados', 'estadas', 'estad', 'none', 'he', 'has', 'ha', 'hemos', 'habéis', 'han',
                             'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá',
                             'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais',
                             'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube',
                             'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
                             'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos',
                             'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
                             'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seáis',
                             'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería',
                             'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais',
                             'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera',
                             'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos',
                             'fueseis', 'fuesen', 'siendo', 'sido', 'sed', 'tengo', 'tienes', 'tiene',
                             'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas', 'tengamos', 'tengáis',
                             'tengan', 'tendré', 'tendrás', 'tendrá', 'tendremos', 'tendréis', 'tendrán',
                             'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían', 'tenía',
                             'tenías', 'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo',
                             'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos',
                             'tuvierais', 'tuvieran', 'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis',
                             'tuviesen', 'teniendo', 'tenido', 'tenida', 'tenidos', 'tenidas', 'tened', ''])

    def formar_indice(self):
        """Actualiza el indice, en caso de que no exista lo crea"""
        try:
            diccionario = json.load(open(os.path.join(self._BASIC_PATH, "Dic.json")))
        except:
            diccionario = {"1": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "2": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "3": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "4": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "5": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}}
        self.spimi(diccionario)
        json.dump(diccionario, open(os.path.abspath(os.path.join(self._BASIC_PATH, "Dic.json")), "w"))
        elementos = self.preparar_elementos_para_el_merge()
        if elementos[0]:
            self.merge(4, elementos[0], elementos[1], elementos[2])
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            #ACA construyo el indice
            spimi = os.path.join(self._BASIC_PATH, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt')
            self.actualizar_ranking(medio,spimi)
            #os.remove(spimi)

    def spimi(self, diccionario):
        """
        SPIMI : Single-pass in-memory indexing
        crea multiples archivos intermedios con termino : postings
        :param diccionario: con los indices de los ultimos elementos agregados al indice
        :return:
        """
        for medio in diccionario.keys():
            indice = {}
            for seccion in sorted(diccionario[medio].keys()):
                noticias = self.obtener_noticias((medio, seccion, diccionario[medio]))
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
            temp = open(os.path.join(self._BASIC_PATH, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'), 'wt' ,encoding='latin-1')
            for termino in sorted(indice.keys()):
                temp.write(termino + ';' + ''.join([str(x) + ',' for x in indice[termino]])[:-1] + "\n")
            temp.close()

    def obtener_noticias(self, posicion):
        """
        :param posicion: tupla con medio, seccion, diccionario con id noticia anterior
        :return: todas las noticias de un medio y seccion especificas a partir de un id
        """
        tree = etree.parse(os.path.join(self._BASIC_PATH, "..", "sources", self._INDICE_MEDIOS[posicion[0]] + ".xml"),
                           etree.XMLParser(remove_blank_text=True))
        noticia_str = "seccion[" + posicion[1] + "]/noticia[" + str(posicion[2][posicion[1]] + 1) + "]"
        if len(tree.xpath(noticia_str)) == 0:
            return
        posicion[2][posicion[1]] += 1
        yield tree.xpath(noticia_str + "/titulo")[0].text, tree.xpath(noticia_str + "/descripcion")[0].text
        for noticia in tree.xpath(noticia_str)[0].itersiblings():
            posicion[2][posicion[1]] += 1
            yield (noticia.xpath("titulo")[0].text, noticia.xpath("descripcion")[0].text)


    def actualizar_ranking(self , medio , spimi):
        print(medio,spimi)




    def normalizar_string(self, string):
        """ :return: lista de palabras normalizadas"""
        stemmer = SnowballStemmer('spanish')
        string = re.split(r"[0-9_\W]", string)
        words = []
        for word in string:
            if word != "" and word not in self._STOP_WORDS and len(word) > self._WORD_MIN_LENGTH:
                word = stemmer.stem(word)
                word = word.replace("ñ", "o@")
                word = word.replace("ü", "u")
                words.append(word)
        return words

    def preparar_elementos_para_el_merge(self):
        """
        Crea listas de lineas y archivos para el merge, obteniendo solo los elementos que tienen informacion
        :return: tupla con (lista de lineas, lista de archivos, archivo previo) ordenadas
        """
        intermedios = []
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            intermedios.append(
                open(os.path.join(self._BASIC_PATH, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'), 'rt' , encoding='latin-1'))
        lineas = []
        for x in range(len(intermedios) - 1, -1, -1):
            linea = intermedios[x].readline().split(";")
            if len(linea[0].lstrip()) != 0:
                lineas.append(intermedios[x].readline().split(";"))
            else:
                intermedios[x].close()
                intermedios.remove(intermedios[x])
        file = None
        if lineas:
            try:
                file = self.descomprimir_indice()
                intermedios.append(file)
                lineas.append(file.readline().split(";"))
            except:
                pass
        return lineas, intermedios, file

    def merge(self, block_size, lineas, intermedios, previo):
        """
        Unifica los archivos intermedios creados por SPIMI en un indice comprimido que consiste en un "block storage"
        con las palabras, un posting_list y una estructura auxiliar con referencias a los postings y al "block storage"
        :param block_size: tamaño de cada bloque en el "block storage"
        :param lineas: lista de lineas ordenadas
        :param intermedios: lista de archivos ordenadas
        :param previo: archivo con los elementos anteriores, None si no es una actualizacion
        """
        block_storage = open(os.path.join(self._BASIC_PATH, "block_storage.txt"), 'wt' , encoding='latin-1')
        estructura_auxiliar = open(os.path.join(self._BASIC_PATH, "estructura_auxiliar.txt"), 'wt' , encoding='latin-1')
        postings_list = open(os.path.join(self._BASIC_PATH, "postings_list.txt"), 'wt' , encoding='latin-1')
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
                    for j in range(0, len(apariciones)):
                        apariciones[j] -= 1
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
        if previo:
            os.remove(os.path.join(self._BASIC_PATH, "temporal_previo.txt"))

    def comprimir_postings(self, postings, ref):
        """
        :param postings: string con los postings
        :param ref: indice del comienzo de los postings en el archivo
        :return: string comprimido con los postings, indices del comienzo de cada posting en el archivo
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

    def descomprimir_indice(self):
        """
        Transfora el indice comprimido (block_storage, estructura_auxiliar y postings_list)
        al formato de un archivo intermedio para poder hacer el merge al actualizar el indice
        """
        block_storage = open(os.path.join(self._BASIC_PATH, "block_storage.txt"), 'rt' , encoding='latin-1')
        postings_list = open(os.path.join(self._BASIC_PATH, "postings_list.txt"), 'rt' , encoding='latin-1')
        temporal_previo = open(os.path.join(self._BASIC_PATH, "temporal_previo.txt"), 'wt' , encoding='latin-1')
        for block in open(os.path.join(self._BASIC_PATH, "estructura_auxiliar.txt"), 'rt' , encoding='latin-1').read()[:-1].split(";"):
            indice_palabra = int(block.split("-")[0])
            for posting in block.split("-")[1].split(","):
                post_list = self.leer_apariciones(postings_list, posting)
                post_str = ""
                for post in post_list:
                    post_str += post + ","
                palabra, indice_palabra = self.leer_palabra(block_storage, indice_palabra)
                if palabra:
                    temporal_previo.write(palabra + ";" + post_str[:-1] + "\n")
        block_storage.close()
        postings_list.close()
        temporal_previo.close()
        return open(os.path.join(self._BASIC_PATH, "temporal_previo.txt"), 'rt')

    def obtener_apariciones(self, palabra):
        """
        :param palabra: palabra normalizada a buscar
        :return: set con las apariciones de la palabra
        """
        basic_path = os.path.join(os.path.dirname(__file__), "..", "Indice")
        block_storage = open(os.path.join(basic_path, "block_storage.txt"), "rt" , encoding='latin-1')
        estructura_auxiliar = open(os.path.join(basic_path, "estructura_auxiliar.txt"), 'rt' , encoding='latin-1').read()[:-1].split(";")
        inicio = 0
        fin = len(estructura_auxiliar)
        medio = int((inicio + fin) / 2)
        while inicio + 1 < fin:
            indice = int(estructura_auxiliar[medio].split("-")[0])
            word, indice = self.leer_palabra(block_storage, indice)
            if word:
                if word <= palabra:
                    inicio = medio
                elif word > palabra:
                    fin = medio
            medio = int((inicio + fin) / 2)
        posicion = self.obtener_posicion_bloque(palabra, int(estructura_auxiliar[medio].split("-")[0]), block_storage)
        block_storage.close()
        if posicion == -1:
            return set()
        postrings_list = open(os.path.join(basic_path, "postings_list.txt"), 'rt' , encoding='latin-1')
        indice = int(estructura_auxiliar[medio].split("-")[1].split(",")[posicion])
        apariciones = self.leer_apariciones(postrings_list, indice)
        postrings_list.close()
        #Las devuelve ordenadas por medio
        return sorted(set(apariciones))

    def leer_palabra(self, block_storage, indice_palabra):
        """
        :param block_storage: archivo block_storage
        :param indice_palabra: indice de inicio palabra en el archivo
        :return:
        """
        block_storage.seek(indice_palabra)
        longitud_palabra = block_storage.read(1)
        indice_palabra += 1
        continuar = True
        while continuar:
            temp = block_storage.read(1)
            continuar = temp.isdigit()
            if continuar:
                longitud_palabra += temp
                indice_palabra += 1
        block_storage.seek(indice_palabra)
        if len(longitud_palabra) != 0:
            palabra = block_storage.read(int(longitud_palabra))
            indice_palabra += len(palabra)
        return palabra, indice_palabra

    def leer_apariciones(self, postings_list, indice):
        """
        :param postings_list: archivo postings_list
        :param indice: indice de inicio postings en el archivo
        :return: lista con las apariciones
        """
        post_list = ""
        cont = True
        postings_list.seek(int(indice))
        while cont:
            temp = postings_list.read(1)
            cont = temp != ","
            if cont:
                post_list += temp
        post_list = post_list.split("+")
        for i in range(1, len(post_list)):
            post_list[i] = str(int(post_list[i]) + int(post_list[i - 1]))
        return post_list

    def obtener_posicion_bloque(self, palabra, indice, block_storage):
        """
        :param palabra: palabra a buscar
        :param indice: indice de inicio bloque
        :param block_storage: archivo block_storage
        :return: numero con la posicion en el bloque 0-(tamaño bloque -1), -1 si no esta
        """
        posicion = -1
        word = ""
        while word != palabra and posicion < 3:
            word, indice = self.leer_palabra(block_storage, indice)
            posicion += 1
        if word != palabra:
            posicion = -1
        return posicion

    def obtener_todos_docs(self):
        """Devuelve un SET con todos los docs"""
        pass


# Test creacion-actualizacion indice
if __name__ == '__main__':
    Indice().formar_indice()
    #Indice().descomprimir_indice()
    #print(Indice().obtener_apariciones("econom"))
