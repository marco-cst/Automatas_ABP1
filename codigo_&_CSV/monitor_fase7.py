
"""
===============================================================================
UNIVERSIDAD NACIONAL DE LOJA
Carrera de Computación - Teoría de Autómatas y Computabilidad Avanzada
FASE 7: Implementación del Monitor de Eventos en Python
===============================================================================

Descripción:
Este script simula el recorrido de un Autómata Finito Determinista (AFD)
minimizado sobre secuencias de eventos de la máquina dispensadora para
detectar patrones válidos y anomalías transaccionales.
===============================================================================
"""

import csv

# -----------------------------------------------------------------------------
# 1. DEFINICIÓN FORMAL DEL AFD MINIMIZADO M = (Q, Σ, δ, q0, F)
# -----------------------------------------------------------------------------

# Alfabeto de eventos Σ = {X, V, M, S, I, C, F, A, P, D, Q}
ALFABETO = {"X", "V", "M", "S", "I", "C", "F", "A", "P", "D", "Q"}

# Estado Inicial q0
ESTADO_INICIAL = "q0"

# Conjunto de Estados de Aceptación/Finales (F) - Detectan la presencia de patrones
ESTADOS_ACEPTACION = {"q_F"}

# Patrones del modelo. P1-P3 son anomalías; P4-P6 son validaciones.
PATRONES = {
    "P1": "MSIF",
    "P2": "MSAF",
    "P3": "MSPF",
    "P4": "MSCF",
    "P5": "QMSC",
    "P6": "XMSC",
}

PATRONES_ANOMALIA = {"P1", "P2", "P3"}

# Función de Transición δ(estado_actual, simbolo) -> nuevo_estado
# Representada mediante un diccionario anidado para búsquedas O(1) por símbolo.
TRANSICIONES = {
    "q0": {
        "M": "q_M",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_M": {
        "M": "q_M",
        "S": "q_MS",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_MS": {
        "M": "q_M",
        "I": "q_MSI",
        "A": "q_MSA",
        "P": "q_MSP",
        "C": "q_MSC",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_MSI": {
        "M": "q_M",
        "F": "q_F",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_MSA": {
        "M": "q_M",
        "F": "q_F",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_MSP": {
        "M": "q_M",
        "F": "q_F",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_MSC": {
        "M": "q_M",
        "F": "q_F",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_Q": {
        "M": "q_QM",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_QM": {
        "M": "q_M",
        "S": "q_QMS",
        "Q": "q_Q",
        "X": "q_X"
    },
    # Tras QMS/XMS, un evento I, A o P puede iniciar los patrones
    # MSIF, MSAF o MSPF (prefijos solapados).
    "q_QMS": {
        "M": "q_M",
        "I": "q_MSI",
        "A": "q_MSA",
        "P": "q_MSP",
        "C": "q_F",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_X": {
        "M": "q_XM",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_XM": {
        "M": "q_M",
        "S": "q_XMS",
        "Q": "q_Q",
        "X": "q_X"
    },
    "q_XMS": {
        "M": "q_M",
        "I": "q_MSI",
        "A": "q_MSA",
        "P": "q_MSP",
        "C": "q_F",
        "Q": "q_Q",
        "X": "q_X"
    },

    # Estado final absorbente: Permanece en sí mismo ante cualquier evento posterior
    "q_F": {simbolo: "q_F" for simbolo in ALFABETO}
}


# -----------------------------------------------------------------------------
# 2. MOTOR DE EVALUACIÓN (SIMULADOR DEL AFD)
# -----------------------------------------------------------------------------

def evaluar_cadena(cadena_eventos):
    """
    Simula el procesamiento de una cadena w ∈ Σ* paso a paso sobre el AFD.

    Parámetros:
        cadena_eventos (str): Secuencia ordenada de símbolos de la sesión.

    Retorna:
        tuple: (es_aceptada: bool, estado_final: str, historial_estados: list)
    """

    estado_actual = ESTADO_INICIAL
    historial = [estado_actual]

    for simbolo in cadena_eventos:
        if simbolo not in ALFABETO:
            # Evento fuera del alfabeto formal
            continue

        # Determinar el siguiente estado mediante la función δ
        if estado_actual in TRANSICIONES and simbolo in TRANSICIONES[estado_actual]:
            estado_actual = TRANSICIONES[estado_actual][simbolo]
        else:
            # Si el símbolo no mantiene ni avanza un prefijo, regresa a q0
            estado_actual = ESTADO_INICIAL

        historial.append(estado_actual)

    es_aceptada = estado_actual in ESTADOS_ACEPTACION

    return es_aceptada, estado_actual, historial


# -----------------------------------------------------------------------------
# 2.1 AFD AUXILIARES PARA IDENTIFICAR EL PATRÓN DETECTADO
# -----------------------------------------------------------------------------

# El AFD minimizado de la unión indica si la sesión contiene al menos un
# patrón. Estos seis AFD auxiliares (tipo KMP) indican cuál o cuáles patrones
# aparecen, para poder distinguir una anomalía (P1-P3) de una validación
# (P4-P6).

def construir_afd_patron(patron):
    """
    Construye la tabla de transiciones de un AFD que reconoce la presencia
    de 'patron' dentro de una cadena.

    Parámetros:
        patron (str): Subcadena que se desea detectar.

    Retorna:
        list: Lista de diccionarios; transiciones[estado][simbolo] = nuevo_estado.
    """
    m = len(patron)
    fallo = [0] * m

    # Función de fallo (prefijo-sufijo) para las transiciones de retroceso.
    k = 0
    for i in range(1, m):
        while k > 0 and patron[i] != patron[k]:
            k = fallo[k - 1]
        if patron[i] == patron[k]:
            k += 1
        fallo[i] = k

    transiciones = []
    for estado in range(m + 1):
        fila = {}
        for simbolo in ALFABETO:
            if estado < m and simbolo == patron[estado]:
                fila[simbolo] = estado + 1
            elif estado == 0:
                fila[simbolo] = 0
            else:
                k = fallo[estado - 1]
                while k > 0 and simbolo != patron[k]:
                    k = fallo[k - 1]
                if simbolo == patron[k]:
                    k += 1
                fila[simbolo] = k
        transiciones.append(fila)

    return transiciones


AFD_PATRONES = {
    clave: construir_afd_patron(subcadena)
    for clave, subcadena in PATRONES.items()
}


def detectar_patrones(cadena_eventos):
    """
    Ejecuta los seis AFD auxiliares sobre la sesión y devuelve las claves
    de los patrones presentes (por ejemplo, ['P1', 'P4']).
    """
    encontrados = []

    for clave, transiciones in AFD_PATRONES.items():
        estado = 0
        longitud = len(PATRONES[clave])

        for simbolo in cadena_eventos:
            if simbolo not in ALFABETO:
                continue
            estado = transiciones[estado][simbolo]
            if estado == longitud:
                encontrados.append(clave)
                break

    return encontrados


# -----------------------------------------------------------------------------
# 3. PROCESAMIENTO DE ARCHIVOS DE BITÁCORA (CSV)
# -----------------------------------------------------------------------------

def procesar_bitacora(ruta_csv_entrada, ruta_csv_salida=None,
                      ruta_clave_etiquetas=None):
    """
    Lee las sesiones desde un archivo CSV, simula el monitor y genera el informe.

    Soporta estructuras de CSV con o sin columna 'etiqueta':
        - id_sesion, eventos, etiqueta (ej. sesiones_datos.csv)
        - id_sesion, eventos (ej. sesiones_prueba.csv)

    Si se indica ruta_clave_etiquetas, completa la etiqueta real de cada
    sesión usando el archivo de claves (id_sesion, etiqueta_real).
    """

    resultados = []

    # Etiquetas del conjunto de prueba, si se proporciona la clave.
    etiquetas_clave = {}
    if ruta_clave_etiquetas:
        try:
            with open(
                ruta_clave_etiquetas,
                mode='r',
                encoding='utf-8'
            ) as f_clave:
                for fila_clave in csv.DictReader(f_clave):
                    etiquetas_clave[fila_clave['id_sesion']] = (
                        fila_clave['etiqueta_real']
                    )
        except FileNotFoundError:
            print(
                f"[ERROR] El archivo de claves '{ruta_clave_etiquetas}' "
                "no se encuentra en el directorio."
            )
            return []

    try:
        with open(ruta_csv_entrada, mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)

            for fila in lector:
                id_sesion = fila['id_sesion']
                eventos = fila['eventos']
                etiqueta_real = fila.get('etiqueta', None)

                if etiqueta_real is None:
                    etiqueta_real = etiquetas_clave.get(id_sesion)

                # Evaluación con el AFD minimizado de la unión
                _, estado_final, _ = evaluar_cadena(eventos)

                # Identificación del patrón o patrones presentes
                patrones = detectar_patrones(eventos)
                es_anomalia = any(p in PATRONES_ANOMALIA for p in patrones)
                prediccion = "anomala" if es_anomalia else "normal"

                patrones_txt = (
                    ", ".join(f"{p}:{PATRONES[p]}" for p in patrones)
                    if patrones else "ninguno"
                )

                res = {
                    "id_sesion": id_sesion,
                    "eventos": eventos,
                    "prediccion": prediccion,
                    "estado_final": estado_final,
                    "patrones_detectados": patrones_txt,
                    "etiqueta": etiqueta_real
                }

                resultados.append(res)

    except FileNotFoundError:
        print(
            f"[ERROR] El archivo '{ruta_csv_entrada}' "
            "no se encuentra en el directorio."
        )
        return []

    # Exportar resultados a un nuevo CSV si se especifica la ruta
    if ruta_csv_salida:
        with open(
            ruta_csv_salida,
            mode='w',
            encoding='utf-8',
            newline=''
        ) as f_out:

            campos = [
                "id_sesion",
                "eventos",
                "prediccion",
                "estado_final",
                "patrones_detectados"
            ]

            if any(r["etiqueta"] is not None for r in resultados):
                campos.append("etiqueta")

            escritor = csv.DictWriter(f_out, fieldnames=campos)
            escritor.writeheader()

            for r in resultados:
                fila_out = {k: r[k] for k in campos if k in r}
                escritor.writerow(fila_out)

        print(f"[OK] Resultados exportados exitosamente a: {ruta_csv_salida}")

    return resultados


# -----------------------------------------------------------------------------
# 4. EJECUCIÓN Y MUESTRA EN CONSOLA
# -----------------------------------------------------------------------------

def imprimir_resumen(sesiones):
    """Imprime el conteo de predicciones y las detecciones por patrón."""
    anomalas = sum(
        1 for s in sesiones
        if s['prediccion'] == "anomala"
    )

    normales = sum(
        1 for s in sesiones
        if s['prediccion'] == "normal"
    )

    print(
        f"Resumen del Monitor -> "
        f"Anómalas (P1-P3): {anomalas} | "
        f"Normales/Validaciones: {normales}\n"
    )

    print("Detecciones por patrón:")
    for clave, subcadena in PATRONES.items():
        cantidad = sum(
            1 for s in sesiones
            if clave in s["patrones_detectados"]
        )
        print(f"  {clave} ({subcadena}): {cantidad}")


def imprimir_comparacion_etiquetas(sesiones):
    """Imprime la matriz de confusión contra la etiqueta real disponible."""
    etiquetadas = [
        s for s in sesiones
        if s.get("etiqueta") in ("anomala", "normal")
    ]

    if not etiquetadas:
        return

    vp = sum(
        1 for s in etiquetadas
        if s["etiqueta"] == "anomala" and s["prediccion"] == "anomala"
    )
    fp = sum(
        1 for s in etiquetadas
        if s["etiqueta"] == "normal" and s["prediccion"] == "anomala"
    )
    fn = sum(
        1 for s in etiquetadas
        if s["etiqueta"] == "anomala" and s["prediccion"] == "normal"
    )
    vn = sum(
        1 for s in etiquetadas
        if s["etiqueta"] == "normal" and s["prediccion"] == "normal"
    )

    print("\nComparación con las etiquetas reales:")
    print(f"  VP: {vp} | FP: {fp} | FN: {fn} | VN: {vn}")


if __name__ == "__main__":
    archivo_input = "sesiones_datos.csv"
    archivo_output = "resultados_monitor.csv"

    print("=== INICIANDO MONITOR DE EVENTOS (FASE 7) ===")
    print(f"Procesando bitácora: {archivo_input}...\n")

    sesiones_procesadas = procesar_bitacora(
        archivo_input,
        archivo_output
    )

    if sesiones_procesadas:
        print(f"Total de sesiones monitoreadas: {len(sesiones_procesadas)}")

        print("\n--- MUESTRA DE LAS PRIMERAS 5 SESIONES PROCESADAS ---")

        print(
            f"{'ID SESIÓN':<12} | "
            f"{'EVENTOS':<22} | "
            f"{'PREDICCIÓN':<10} | "
            f"{'PATRÓN':<24} | "
            f"{'ESTADO FINAL'}"
        )

        print("-" * 90)

        for s in sesiones_procesadas[:5]:
            print(
                f"{s['id_sesion']:<12} | "
                f"{s['eventos']:<22} | "
                f"{s['prediccion']:<10} | "
                f"{s['patrones_detectados']:<24} | "
                f"{s['estado_final']}"
            )

        print("-" * 90)
        imprimir_resumen(sesiones_procesadas)
        imprimir_comparacion_etiquetas(sesiones_procesadas)

    # --- Conjunto de prueba: genera resultados_prueba.csv ---
    archivo_prueba = "sesiones_prueba.csv"
    archivo_clave_prueba = "clave_etiquetas_prueba.csv"
    archivo_salida_prueba = "resultados_prueba.csv"

    print("\n=== PROCESANDO CONJUNTO DE PRUEBA (FASE 7) ===")
    print(f"Procesando bitácora: {archivo_prueba}...\n")

    sesiones_prueba = procesar_bitacora(
        archivo_prueba,
        archivo_salida_prueba,
        archivo_clave_prueba
    )

    if sesiones_prueba:
        print(f"Total de sesiones monitoreadas: {len(sesiones_prueba)}")
        print("-" * 90)
        imprimir_resumen(sesiones_prueba)
        imprimir_comparacion_etiquetas(sesiones_prueba)
