"""
===============================================================================
COMPARACIÓN DE TIEMPO: AFND (con transiciones epsilon) vs AFD MINIMIZADO
===============================================================================

Este script mide el tiempo de ejecución de dos implementaciones del monitor:

1. AFND: unión de los seis patrones mediante transiciones epsilon.
2. AFD: tabla de transiciones del AFD minimizado usada en monitor_fase7.py.

La comparación se hace sobre las sesiones de sesiones_datos.csv y
sesiones_prueba.csv. Para obtener tiempos estables, cada conjunto se procesa
varias veces en rondas intercaladas y se toma la mediana de los tiempos.
===============================================================================
"""

from collections import defaultdict
import csv
import time

import monitor_fase7 as monitor


# -----------------------------------------------------------------------------
# 1. DEFINICIÓN DEL AFND (UNIÓN DE LOS SEIS PATRONES CON EPSILON)
# -----------------------------------------------------------------------------

ALFABETO = monitor.ALFABETO
PATRONES = monitor.PATRONES

INICIO_AFND = "S"
ESTADOS_ACEPTACION_AFND = set()

# TRANSICIONES_AFND[estado][simbolo] = conjunto de estados destino
TRANSICIONES_AFND = defaultdict(lambda: defaultdict(set))
# EPSILON_AFND[estado] = conjunto de estados alcanzables con epsilon
EPSILON_AFND = defaultdict(set)


for clave, patron in PATRONES.items():
    inicio_patron = ("inicio", clave)

    # El estado inicial global se une con cada AFND mediante epsilon.
    EPSILON_AFND[INICIO_AFND].add(inicio_patron)

    # El inicio de cada patrón puede ignorar cualquier evento.
    for simbolo in ALFABETO:
        TRANSICIONES_AFND[inicio_patron][simbolo].add(inicio_patron)

    # Primer símbolo del patrón: se activa la cadena del patrón.
    TRANSICIONES_AFND[inicio_patron][patron[0]].add((clave, 1))

    # Cadena del patrón.
    for i in range(1, len(patron)):
        TRANSICIONES_AFND[(clave, i)][patron[i]].add((clave, i + 1))

    # Estado de aceptación: una vez detectado el patrón, permanece activo.
    aceptacion = (clave, len(patron))
    ESTADOS_ACEPTACION_AFND.add(aceptacion)
    for simbolo in ALFABETO:
        TRANSICIONES_AFND[aceptacion][simbolo].add(aceptacion)


def cerradura_epsilon(estados):
    """Calcula la cerradura epsilon de un conjunto de estados."""
    pila = list(estados)
    cerradura = set(estados)

    while pila:
        estado = pila.pop()
        for siguiente in EPSILON_AFND.get(estado, ()):
            if siguiente not in cerradura:
                cerradura.add(siguiente)
                pila.append(siguiente)

    return cerradura


def evaluar_afnd(cadena_eventos):
    """Simula el AFND y devuelve True si detecta al menos un patrón."""
    estados = cerradura_epsilon({INICIO_AFND})

    for simbolo in cadena_eventos:
        if simbolo not in ALFABETO:
            continue

        siguientes = set()
        for estado in estados:
            siguientes.update(
                TRANSICIONES_AFND.get(estado, {}).get(simbolo, ())
            )

        estados = cerradura_epsilon(siguientes)

    return any(estado in ESTADOS_ACEPTACION_AFND for estado in estados)


def evaluar_afd(cadena_eventos):
    """Simula el AFD minimizado y devuelve True si detecta al menos un patrón."""
    es_aceptada, _, _ = monitor.evaluar_cadena(cadena_eventos)
    return es_aceptada


# -----------------------------------------------------------------------------
# 2. CARGA DE SESIONES Y MEDICIÓN DE TIEMPOS
# -----------------------------------------------------------------------------

def cargar_eventos(ruta_csv):
    """Lee la columna eventos de un CSV y devuelve una lista de cadenas."""
    with open(ruta_csv, mode="r", encoding="utf-8") as archivo:
        return [fila["eventos"] for fila in csv.DictReader(archivo)]


def medir(funcion, sesiones, repeticiones):
    """Ejecuta la función sobre todas las sesiones y devuelve el tiempo total."""
    inicio = time.perf_counter()

    for _ in range(repeticiones):
        for eventos in sesiones:
            funcion(eventos)

    return time.perf_counter() - inicio


def mediana(valores):
    """Devuelve la mediana de una lista de números."""
    ordenados = sorted(valores)
    n = len(ordenados)
    medio = n // 2

    if n % 2 == 1:
        return ordenados[medio]

    return (ordenados[medio - 1] + ordenados[medio]) / 2


def medir_intercalado(funciones, sesiones, repeticiones, rondas=5):
    """
    Mide varias funciones en rondas intercaladas.

    Intercalar las mediciones evita que una función se beneficie de un estado
    de CPU distinto al de la otra. De cada función se devuelve la mediana de
    los tiempos por ronda, que es más estable que el mínimo o el promedio.
    """
    tiempos = {nombre: [] for nombre in funciones}

    for _ in range(rondas):
        for nombre, funcion in funciones.items():
            tiempos[nombre].append(medir(funcion, sesiones, repeticiones))

    return {
        nombre: mediana(valores)
        for nombre, valores in tiempos.items()
    }


def contar_transiciones_afd():
    """Cuenta las transiciones del AFD completo (incluyendo el fallback a q0)."""
    return len(monitor.TRANSICIONES) * len(ALFABETO)


def contar_transiciones_afnd():
    """Cuenta transiciones del AFND, incluyendo las transiciones epsilon."""
    total = 0

    for estado in TRANSICIONES_AFND:
        for simbolo in ALFABETO:
            total += len(TRANSICIONES_AFND[estado].get(simbolo, ()))

    for estado in EPSILON_AFND:
        total += len(EPSILON_AFND[estado])

    return total


# -----------------------------------------------------------------------------
# 3. EJECUCIÓN DE LA COMPARACIÓN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    conjuntos = [
        ("Validación", "sesiones_datos.csv", 200),
        ("Prueba", "sesiones_prueba.csv", 200),
    ]

    filas_resultado = []

    print("=== COMPARACIÓN DE TIEMPO: AFND vs AFD MINIMIZADO ===")
    print(f"Estados del AFND: {len(TRANSICIONES_AFND) + 1}")
    print(f"Estados del AFD:  {len(monitor.TRANSICIONES)}")
    print(f"Transiciones del AFND (con epsilon): {contar_transiciones_afnd()}")
    print(f"Transiciones del AFD (completas):    {contar_transiciones_afd()}")
    print()

    for nombre, ruta_csv, repeticiones in conjuntos:
        sesiones = cargar_eventos(ruta_csv)

        # Verificación rápida: ambos autómatas deben aceptar lo mismo.
        for eventos in sesiones:
            if evaluar_afnd(eventos) != evaluar_afd(eventos):
                raise RuntimeError(
                    f"Discrepancia entre AFND y AFD en {ruta_csv}: {eventos}"
                )

        # Calentamiento para evitar medir la carga inicial de Python.
        medir(evaluar_afnd, sesiones, 1)
        medir(evaluar_afd, sesiones, 1)

        tiempos = medir_intercalado(
            {
                "afnd": evaluar_afnd,
                "afd": evaluar_afd,
            },
            sesiones,
            repeticiones,
            rondas=5,
        )
        tiempo_afnd = tiempos["afnd"]
        tiempo_afd = tiempos["afd"]

        total_sesiones = len(sesiones) * repeticiones
        us_afnd = (tiempo_afnd / total_sesiones) * 1_000_000
        us_afd = (tiempo_afd / total_sesiones) * 1_000_000
        aceleracion = tiempo_afnd / tiempo_afd if tiempo_afd > 0 else 0
        ahorro = (
            (1 - tiempo_afd / tiempo_afnd) * 100
            if tiempo_afnd > 0 else 0
        )

        filas_resultado.append({
            "conjunto": nombre,
            "archivo": ruta_csv,
            "sesiones": len(sesiones),
            "repeticiones": repeticiones,
            "rondas": 5,
            "tiempo_afnd_s": round(tiempo_afnd, 6),
            "tiempo_afd_s": round(tiempo_afd, 6),
            "tiempo_afnd_us_sesion": round(us_afnd, 3),
            "tiempo_afd_us_sesion": round(us_afd, 3),
            "aceleracion_afd": round(aceleracion, 2),
            "ahorro_porcentual": round(ahorro, 2),
            "estados_afnd": len(TRANSICIONES_AFND) + 1,
            "estados_afd": len(monitor.TRANSICIONES),
        })

        print(f"--- Conjunto: {nombre} ({ruta_csv}) ---")
        print(
            f"Sesiones: {len(sesiones)} | Repeticiones: {repeticiones} "
            f"| Rondas: 5 (mediana)"
        )
        print(f"AFND: {tiempo_afnd:.4f} s  ({us_afnd:.2f} us/sesión)")
        print(f"AFD:  {tiempo_afd:.4f} s  ({us_afd:.2f} us/sesión)")
        print(f"Aceleración del AFD: {aceleracion:.2f}x")
        print(f"Ahorro de tiempo: {ahorro:.1f}%")
        print()

    # Exportar la tabla de resultados.
    ruta_salida = "comparacion_tiempos.csv"
    with open(ruta_salida, mode="w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(
            f,
            fieldnames=list(filas_resultado[0].keys())
        )
        escritor.writeheader()
        escritor.writerows(filas_resultado)

    print(f"[OK] Resultados exportados a: {ruta_salida}")
