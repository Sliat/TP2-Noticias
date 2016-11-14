import vistas.Menu
import modelos.Indice

modelos.Indice.Indice().formar_indice()
menu = vistas.Menu.Menu()

while not menu.terminar:
    menu.elegir_operacion()