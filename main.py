# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from microruta import puede_desbloquear, calcular_tarifa, transicion

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    print(puede_desbloquear(25, 100.0, 50, "disponible"))
    print(calcular_tarifa(30, True, 7, 3))
    print(transicion("disponible", "desbloquear", 100))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
