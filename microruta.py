"""Reglas de negocio del sistema MicroRuta.

Implementa la validación de desbloqueo (RN-1), el cálculo de tarifa (RN-2)
y la máquina de estados del scooter (RN-3), tal como se describen en la
especificación del examen.
"""

import math

SALDO_MINIMO = 50.00
BATERIA_MINIMA = 20
EDAD_MINIMA = 18
ESTADOS_DESBLOQUEABLES = ("disponible", "reservado")

TARIFA_DESBLOQUEO = 10.00
TARIFA_POR_MINUTO = 3.50
DESCUENTO_ESTUDIANTE = 0.20
MINUTOS_LIMITE_RECARGO = 120
RECARGO_EXCESO = 80.00
HORA_LIMITE_MADRUGADOR = 8
DIA_INICIO_SEMANA_LABORAL = 1
DIA_FIN_SEMANA_LABORAL = 5

TRANSICIONES = {
    ("disponible", "reservar"): ("reservado", "reserva_iniciada"),
    ("disponible", "desbloquear"): ("en_uso", "viaje_iniciado"),
    ("disponible", "reportar_falla"): ("mantenimiento", "enviado_a_taller"),
    ("reservado", "desbloquear"): ("en_uso", "viaje_iniciado"),
    ("reservado", "expirar_reserva"): ("disponible", "reserva_liberada"),
    ("reservado", "reportar_falla"): ("mantenimiento", "enviado_a_taller"),
    ("en_uso", "reportar_falla"): ("en_uso", "falla_registrada"),
    ("sin_bateria", "recargar"): ("disponible", "scooter_recargado"),
    ("sin_bateria", "reportar_falla"): ("mantenimiento", "enviado_a_taller"),
    ("mantenimiento", "liberar_mantenimiento"): ("disponible", "scooter_liberado"),
}


def puede_desbloquear(edad, saldo, bateria, estado):
    """Valida si un usuario puede desbloquear un scooter (RN-1).

    Evalúa cuatro condiciones en orden de prioridad: estado, edad, saldo
    y batería. Devuelve la primera que falla.

    Args:
        edad: edad del usuario en años (0-120).
        saldo: saldo disponible en la cuenta del usuario.
        bateria: porcentaje de batería del scooter (0-100).
        estado: estado actual del scooter.

    Returns:
        Tupla (permitido: bool, motivo: str).
    """
    if estado not in ESTADOS_DESBLOQUEABLES:
        return False, "scooter_no_disponible"
    if edad < EDAD_MINIMA:
        return False, "menor_de_edad"
    if saldo < SALDO_MINIMO:
        return False, "saldo_insuficiente"
    if bateria < BATERIA_MINIMA:
        return False, "bateria_insuficiente"
    return True, "ok"


def _aplica_descuento_estudiante(es_estudiante, hora_inicio, dia_semana):
    """Determina si aplica el descuento de estudiante madrugador."""
    return (
        es_estudiante
        and DIA_INICIO_SEMANA_LABORAL <= dia_semana <= DIA_FIN_SEMANA_LABORAL
        and hora_inicio < HORA_LIMITE_MADRUGADOR
    )


def calcular_tarifa(minutos, es_estudiante, hora_inicio, dia_semana):
    """Calcula el total a cobrar por un viaje en MicroRuta (RN-2).

    Args:
        minutos: duración del viaje en minutos (puede tener decimales).
        es_estudiante: indica si el usuario tiene tarifa de estudiante.
        hora_inicio: hora en que inició el viaje (0-23).
        dia_semana: día de la semana (1=lunes ... 7=domingo).

    Returns:
        Total a cobrar, redondeado a 2 decimales.
    """
    minutos_cobrados = max(1, math.ceil(minutos))
    subtotal = TARIFA_DESBLOQUEO + TARIFA_POR_MINUTO * minutos_cobrados

    if _aplica_descuento_estudiante(es_estudiante, hora_inicio, dia_semana):
        subtotal *= 1 - DESCUENTO_ESTUDIANTE

    if minutos_cobrados > MINUTOS_LIMITE_RECARGO:
        subtotal += RECARGO_EXCESO

    return round(subtotal, 2)


def transicion(estado, evento, bateria):
    """Calcula la transición de estado de un scooter (RN-3).

    El evento 'finalizar_viaje' desde 'en_uso' es un caso especial: el
    estado siguiente depende del nivel de batería.

    Args:
        estado: estado actual del scooter.
        evento: evento que se intenta aplicar.
        bateria: porcentaje de batería del scooter (0-100).

    Returns:
        Tupla (estado_nuevo: str, salida: str).
    """
    if estado == "en_uso" and evento == "finalizar_viaje":
        if bateria >= BATERIA_MINIMA:
            return "disponible", "viaje_finalizado"
        return "sin_bateria", "requiere_recarga"

    return TRANSICIONES.get((estado, evento), (estado, "transicion_invalida"))
