import controladores.RecortesDeNoticias
import os


class Menu(object):
    def __init__(self):
        self.terminar = False
        self.nombre = "Recortes de noticias"
        self.controlador = controladores.RecortesDeNoticias.RecortesDeNoticias()
        self.operaciones = {
            1: "Ranking de palabras mas mencionadas",
            2: "Cantidad de noticias en un intervalo",
            3: "Consulta booleana - Busqueda de palabra",
            4: "Salir"
        }

        self.menus_disponibles = {
            1: self.ranking_n_palabras,
            2: self.cantidad_de_noticias,
            3: self.consulta_booleana,
            4: self.salir
        }

    def elegir_operacion(self):
        """PREGUNTA AL USUARIO QUE FUNCIONALIDAD REQUIERE"""
        try:
            titulo = self.nombre + " - Operaciones Disponibles"
            op = int(self.seleccion_simple(titulo, self.operaciones, "operación"))
            print("-" * 70)
            print("\nOperacion seleccionada:", self.operaciones[op], "\n")
            self.menus_disponibles[op]()
        except:
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
                if len(opciones) >= numero >= 1:
                    posicion = numero
                else:
                    self.clear()
                    print("Debe ingresar un numero entre 1 y " + str(len(opciones)))
            except ValueError:
                print("Debe ingresar un numero entre 1 y " + str(len(opciones)))
        return posicion

    def ranking_n_palabras(self):
        titulo = self.nombre + " - Ranking de palabras encontradas en"
        opciones = {1: "Titulos", 2: "Cuerpos"}
        op = int(self.seleccion_simple(titulo, opciones, "opcion"))
        lugar = self.obtener_lugar()
        self.controlador.ranking(op, lugar)

    def cantidad_de_noticias(self):
        """
        Incompleto
        """
        lugar = self.obtener_lugar()
        # self.controlador.cantidad(intervalo, lugar)

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
            consulta.append([palabra, op])
        self.controlador.booleana(consulta)

    def obtener_lugar(self):
        """
        :return tupla con medio y categoria
        """
        titulo_medio = self.nombre + " - Seleccion de medio"
        opciones_medio = {
            1: "Todos",
            2: "Clarin",
            3: "La Nacion",
            4: "Telam",
            5: "BBC",
            6: " OTRO "
        }
        op_medio = int(self.seleccion_simple(titulo_medio, opciones_medio, "medio"))
        titulo_categoria = self.nombre + " - Seleccion de categoria"
        opciones_categoria = {
            1: "Todas",
            2: "ultimas",
            3: "politica",
            4: "sociedad",
            5: "economia",
            6: "mundo"
        }
        op_categoria = int(self.seleccion_simple(titulo_categoria, opciones_categoria, "categoria"))
        return op_medio, op_categoria

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def salir(self):
        self.terminar = True
        print("Gracias por usar el " + self.nombre + " UNTREF")
