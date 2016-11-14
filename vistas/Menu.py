import controladores.RecortesDeNoticias
import os
import re


class Menu(object):
    def __init__(self):
        self.terminar = False
        self.nombre = "Recortes de noticias"
        self.controlador = controladores.RecortesDeNoticias.RecortesDeNoticias()
        self.controlador.extraer_noticias()
        self.operaciones = {
            1: "Ranking de palabras mas mencionadas",
            2: "Cantidad de noticias en un intervalo",
            3: "Ranking de categorias",
            4: "Busqueda de palabras",
            5: "Salir"
        }

        self.menus_disponibles = {
            1: self.ranking_n_palabras,
            2: self.cantidad_de_noticias,
            3: self.ranking_categorias,
            4: self.consulta_booleana,
            5: self.salir
        }

    def elegir_operacion(self):
        """PREGUNTA AL USUARIO QUE FUNCIONALIDAD REQUIERE"""
        try:
            titulo = self.nombre + " - Operaciones Disponibles"
            op = int(self.seleccion_simple(titulo, self.operaciones, "operación"))
            print("-" * 70)
            print("\nOperacion seleccionada:", self.operaciones[op], "\n")
            self.menus_disponibles[op]()
        except IOError:
            print("Ocurrio un error en la seleccion de la operación")

    def seleccion_simple(self, titulo, opciones, texto):
        """
        Menu de seleccion de opciones
        titulo : string con el titulo de la seleccion
        opciones : diccionario de las operaciones
        texto : string con el nombre del tipo de opciones
        """
        posicion = -1
        while posicion == -1:
            print("-" * 70)
            print(titulo)
            for clave, valor in sorted(opciones.items()):
                print("\t [" + str(clave) + "] - ", valor)
            print("-" * 70)
            try:
                numero = int(input("\nInserte número de la " + texto + " que desea: "))
                if len(opciones) >= numero >= 0:
                    posicion = numero
                else:
                    self.clear()
                    print("Debe ingresar un numero entre 0 y " + str(len(opciones)))
            except ValueError:
                print("Debe ingresar un numero entre 0 y " + str(len(opciones)))
        return posicion

    def ranking_n_palabras(self):
        titulo = self.nombre + " - Ranking de palabras encontradas en"
        opciones = {1: "Titulos", 2: "Cuerpos"}
        op = int(self.seleccion_simple(titulo, opciones, "opcion"))
        lugar = self.obtener_lugar()
        self.controlador.mostrar_ranking(op, lugar)

    def ranking_categorias(self):
        """
        Muestra las categorias mas activas en el rango de fechas dado
        """
        intervalo = self.obtener_intervalo()
        self.controlador.ranking_categorias(intervalo)


    def cantidad_de_noticias(self):
        """
        Muestra la cantidad de noticias en el intervalo y lugar especificado
        """
        lugar = self.obtener_lugar()
        intervalo = self.obtener_intervalo()
        self.controlador.cantidad(intervalo, lugar)

    def consulta_booleana(self):
        """
        Ejemplo 1 : primer palabra
        los elementos se unen de izquierda a derecha
        Ejemplo 2 : (primer palabra or segunda palabra) and tercer palabra
        si se ingresa una frase se hace un and entre las palabras de la frase
        Ejemplo 3 : primer palabra or (primer palabra frase and segunda palabra frase)
        """
        titulo = self.nombre + " - Conector logico \n"
        booleano = ""
        opciones = {
            1: "or",
            2: "or not",
            3: "and",
            4: "and not",
            5: "Final"
        }
        consulta = []
        palabra = input("Escriba la palabra o frase a buscar")
        booleano = booleano + palabra
        op = int(self.seleccion_simple(titulo + booleano, opciones, "conector"))
        consulta.append((palabra, op))
        while op != len(opciones):
            palabra = input("Escriba la palabra o frase a buscar")
            booleano = "(" + booleano + " " + opciones[op] + " " + palabra + ")"
            op = int(self.seleccion_simple(titulo + booleano[1:-1], opciones, "conector"))
            consulta.append((palabra, op))
        self.controlador.booleana(consulta)

    def obtener_lugar(self):
        """
        :return tupla con medio y categoria
        """
        titulo_medio = self.nombre + " - Seleccion de medio"
        opciones_medio = {0: "Todos los medios"}
        for idmedio, medio in sorted(self.controlador.medio_model.medios.items()):
            opciones_medio[medio["id"]] = medio["nombre"]

        op_medio = int(self.seleccion_simple(titulo_medio, opciones_medio, "medio"))

        titulo_categoria = self.nombre + " - Seleccion de categoria"
        opciones_categoria = {}
        for idcategoria, categoria in sorted(self.controlador.ranking.INDICE_SECCION.items()):
            opciones_categoria[idcategoria] = categoria.title()

        opciones_categoria["0"] = "Todas las categorias"

        op_categoria = int(self.seleccion_simple(titulo_categoria, opciones_categoria, "categoria"))

        return op_medio, op_categoria

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def salir(self):
        self.terminar = True
        print("Gracias por usar el " + self.nombre + " UNTREF")

    def obtener_intervalo(self):
        """
        :return: tupla inicio, fin en formato (MM,DD,HH)
        """
        titulo = self.nombre + " - Conector logico \n"
        fecha_inicial = self.obtener_fecha('inicial')
        fecha_final = self.obtener_fecha('final')
        while fecha_final < fecha_inicial:
            print("La fecha final debe ser posterior o igual a la inicial")
            fecha_inicial = self.obtener_fecha('inicial')
            fecha_final = self.obtener_fecha('final')
        hora_inicial = self.obtener_hora('inicial')
        hora_final = self.obtener_hora('final')
        while (fecha_final == fecha_inicial and hora_final < hora_inicial):
            print("La hora inicial debe ser anterior a la final si se busca en un solo dia")
            hora_inicial = self.obtener_hora('inicial')
            hora_final = self.obtener_hora('final')
        return (int(fecha_inicial[0:2]), int(fecha_inicial[3:5]), int(hora_inicial)), (int(fecha_final[0:2]), int(
            fecha_final[3:5]), int(hora_final))

    def obtener_fecha(self, posicion):
        """
        :param posicion: indica si es final o inicial
        :return: fecha con formato MM-DD
        """
        fecha = input("Escriba el mes y dia " + posicion + " \n En el formato MM-DD\n")
        while (not re.match(r"(0[1-9]|1[012])-(0[1-9]|[12]\d|3[01])", fecha)):
            print("Formato incorrecto")
            fecha = input("Escriba el mes y dia " + posicion + " \n En el formato MM-DD\n")
        return fecha

    def obtener_hora(self, posicion):
        """
        :param posicion: indica si es final o inicial
        :return: hora con formato HH
        """
        hora = input("Escriba la hora " + posicion + " \n En el formato HH\n")
        while (not re.match(r"([01]\d|2[0-3])", hora)):
            print("Formato incorrecto")
            hora = input("Escriba la hora " + posicion + " \n En el formato HH\n")
        return hora


if __name__ == '__main__':
    menu = Menu()
    menu.obtener_lugar()
