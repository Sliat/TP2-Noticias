'''

    clase con los metodos que indican como extraer de cada medio para convertirlo en el xml fuente del indice invertido
    debemos convertir los rss de cada medio a una estructura xml compartida.
    Ejectua el metodo de la siguiente forma:
        extraer_[clave del dicc en config/rss_sources]

'''


class Medio(object):

    def extraer_telam(self):
        print("extraigo de telam")

    def extraer_clarin(self):
        print("extraigo de clarin")

    def extraer_lanacion(self):
        print("extraigo de la nacion")

    def extraer_bbc(self):
        print("extraigo de bbc")
