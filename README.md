# Automatas_ABP1
# 🥤 Máquina Dispensadora — Modelado mediante Autómatas Finitos

<p align="center">
  <strong>Teoría de Autómatas y Computabilidad Avanzada</strong><br>
  Universidad Nacional de Loja · Ingeniería en Computación
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/JFLAP-Autómatas-purple" alt="JFLAP">
  <img src="https://img.shields.io/badge/CSV-Procesamiento%20de%20datos-green" alt="CSV">
  <img src="https://img.shields.io/badge/Proyecto-Académico-orange" alt="Proyecto académico">
</p>

---

## 📖 Descripción del proyecto

El presente proyecto consiste en el modelado y análisis formal del comportamiento de una máquina dispensadora mediante los fundamentos de la teoría de autómatas y lenguajes formales.

Se representan las interacciones entre el usuario y la máquina como una secuencia ordenada de eventos discretos. A partir de estas secuencias, se construyen Autómatas Finitos No Deterministas (AFND) para representar distintos patrones de comportamiento. Posteriormente, se integran los autómatas, se eliminan las transiciones epsilon (ε), se realiza la conversión a un Autómata Finito Determinista (AFD) y se aplica la minimización.

Finalmente, se desarrolla un monitor en Python para procesar las bitácoras almacenadas en archivos CSV, evaluar las secuencias de eventos y analizar los resultados obtenidos mediante pruebas y métricas de clasificación.

## 🎯 Objetivos

### Objetivo general

Modelar el funcionamiento de una máquina dispensadora mediante autómatas finitos, aplicando técnicas de construcción, unión, determinización y minimización para analizar secuencias de eventos y evaluar el comportamiento del sistema.

### Objetivos específicos

- Definir el alfabeto de eventos que representa las interacciones de la máquina.
- Formalizar los patrones de comportamiento mediante lenguajes regulares.
- Diseñar los seis AFND individuales utilizando JFLAP.
- Construir un AFND unido mediante transiciones epsilon y eliminarlas posteriormente.
- Convertir el autómata resultante en un AFD y obtener su versión mínima.
- Implementar el monitor en Python para procesar sesiones transaccionales.
- Evaluar el funcionamiento del sistema mediante datos sintéticos, pruebas y métricas.

## 🏗️ Fundamentos del modelo formal

### 1. Alfabeto de eventos

El sistema utiliza el siguiente alfabeto finito:

\[
\Sigma=\{X,V,M,S,I,C,F,A,P,D,Q\}
\]

Cada símbolo representa un evento que puede ocurrir durante la interacción con la máquina dispensadora.

| Símbolo | Evento | Descripción |
|---|---|---|
| `X` | Configuración del sonido | Activar o desactivar el sonido |
| `V` | Consulta | Visualizar productos y precios |
| `M` | Inserción de moneda | Introducir dinero |
| `S` | Selección | Elegir un producto |
| `I` | Saldo insuficiente | Detectar que el dinero no alcanza |
| `C` | Pago confirmado | Confirmar el pago |
| `F` | Entrega | Dispensar el producto |
| `A` | Cancelación | Cancelar la compra |
| `P` | Producto agotado | Registrar que no existe disponibilidad |
| `D` | Devolución | Entregar el cambio o reembolso |
| `Q` | Moneda inválida | Rechazar y devolver una moneda |

### 2. Representación de las transacciones

Cada sesión se representa como una cadena \(w\in\Sigma^*\), formada por la concatenación de los símbolos correspondientes a sus eventos.

Ejemplos:

- `MSPF`: inserción de dinero, selección, registro de producto agotado y entrega.
- `MSCF`: inserción de dinero, selección, pago confirmado y entrega.
- `MSAD`: inserción de dinero, selección, cancelación y devolución.
- `QMSC`: rechazo de una moneda, nueva inserción, selección y confirmación del pago.

Estas cadenas permiten representar formalmente las transacciones y evaluar si cumplen los patrones definidos.

## 🔎 Patrones y lenguajes

El proyecto establece seis patrones para analizar las secuencias de eventos de la máquina dispensadora.

| Patrón | Cadena | Interpretación |
|---|---|---|
| P1 | `MSIF` | Entrega después de detectar saldo insuficiente |
| P2 | `MSAF` | Entrega después de cancelar la compra |
| P3 | `MSPF` | Entrega después de registrar un producto agotado |
| P4 | `MSCF` | Compra con pago confirmado y entrega |
| P5 | `QMSC` | Continuación del proceso después del rechazo de una moneda |
| P6 | `XMSC` | Continuación de la compra después de un evento neutro |

Los patrones P1, P2 y P3 representan anomalías definidas en el modelo. Los patrones P4, P5 y P6 representan secuencias de validación de determinados comportamientos esperados.

Cada lenguaje se define como el conjunto de cadenas sobre \(\Sigma\) que contienen la subcadena correspondiente.

## 🔄 Diseño de los AFND

Se construyen seis Autómatas Finitos No Deterministas, uno para cada patrón.

Cada autómata se describe mediante la quíntupla formal:

\[
M=(Q,\Sigma,\delta,q_0,F)
\]

Donde:

- \(Q\): conjunto de estados.
- \(\Sigma\): alfabeto de entrada.
- \(\delta\): función de transición.
- \(q_0\): estado inicial.
- \(F\): conjunto de estados de aceptación.

Los estados representan el progreso en el reconocimiento de una secuencia. Cuando se completa el patrón correspondiente, se alcanza un estado de aceptación.

Los diagramas y las tablas de transiciones se elaboran utilizando JFLAP.

## 🔗 Unión de autómatas y eliminación de ε

Para integrar los seis patrones en un único modelo, se incorpora un nuevo estado inicial global conectado mediante transiciones epsilon a los estados iniciales de los AFND individuales.

Posteriormente, se calculan las clausuras epsilon y se reorganizan las transiciones para obtener un AFND sin transiciones epsilon.

Este procedimiento permite combinar los lenguajes de los autómatas individuales en un modelo unificado, conservando las condiciones de aceptación correspondientes.

## ⚙️ Conversión a AFD y minimización

### Conversión de AFND a AFD

Se aplica el algoritmo de construcción de subconjuntos para transformar el autómata no determinista en uno determinista. Cada estado del nuevo autómata representa un conjunto de estados del AFND.

Se identifican los estados alcanzables desde el inicial y se construye la tabla de transiciones para los símbolos del alfabeto.

### Minimización del AFD

Se identifican los estados equivalentes mediante particiones entre estados de aceptación y no aceptación. Después de refinar las particiones, los estados equivalentes se agrupan para construir un AFD mínimo.

La minimización busca reducir la cantidad de estados sin modificar el lenguaje reconocido.

### Verificación de equivalencia

Se comparan las respuestas del AFD y del AFD mínimo utilizando cadenas de prueba. Ambos modelos deben aceptar y rechazar las mismas cadenas si la conversión y minimización son correctas.

## 💻 Implementación en Python

La implementación traslada el modelo formal a un monitor capaz de procesar sesiones transaccionales.

Sus componentes principales son:

1. **Definición del alfabeto:** establece los símbolos válidos.
2. **Definición de estados y transiciones:** representa el autómata mediante estructuras de datos.
3. **Evaluación de cadenas:** recorre los eventos y registra el historial de estados.
4. **Lectura de archivos CSV:** procesa las sesiones y sus etiquetas.
5. **Clasificación:** genera una predicción para cada sesión.
6. **Generación de resultados:** almacena la secuencia procesada, el estado final y la clasificación obtenida.

El motor de evaluación utiliza la función de transición para determinar cómo evoluciona el estado del autómata con cada símbolo de entrada.

## 📊 Generación y evaluación de datos

Para evaluar el monitor, el proyecto utiliza un generador de datos sintéticos implementado en Python con una semilla aleatoria fija (`random.Random(42)`).

El conjunto de validación descrito en el informe contiene:

| Característica | Cantidad |
|---|---:|
| Sesiones de validación | 300 |
| Sesiones etiquetadas como anómalas | 54 |
| Sesiones etiquetadas como normales | 246 |
| Eventos por sesión | Entre 5 y 20 |
| Semilla aleatoria | 42 |

También se contemplan sesiones de prueba sin etiquetas visibles y un archivo separado con las etiquetas de referencia para realizar una evaluación posterior.

## 📈 Métricas y análisis de resultados

La evaluación compara las predicciones del monitor con las etiquetas reales de las sesiones.

Las métricas consideradas son:

- **Verdaderos positivos (VP):** anomalías correctamente detectadas.
- **Falsos positivos (FP):** sesiones normales clasificadas como anómalas.
- **Falsos negativos (FN):** anomalías clasificadas como normales.
- **Verdaderos negativos (VN):** sesiones normales correctamente clasificadas.


También se propone comparar el AFD y el AFD mínimo mediante el número de estados, el número de transiciones, el tiempo de ejecución y la coincidencia de sus resultados.

Los valores experimentales definitivos deben obtenerse ejecutando el programa y verificando los autómatas.

## ⚠️ Limitaciones del modelo

El sistema se centra en el reconocimiento de secuencias de eventos representables mediante autómatas finitos. No realiza automáticamente todas las validaciones propias de una máquina dispensadora real, como el cálculo monetario ilimitado, la comprobación de precios o la gestión completa del inventario.

Como mejora futura, se propone integrar validaciones numéricas adicionales, ampliar los patrones y realizar pruebas con bitácoras reales.

## 🚀 Posibles mejoras

- Incorporar nuevos patrones de comportamiento.
- Mejorar el análisis de las transacciones y las cancelaciones.
- Automatizar la generación de reportes.
- Añadir visualizaciones de los recorridos de estados.
- Optimizar la clasificación de grandes conjuntos de datos.
- Ampliar las pruebas y el análisis de errores.
- Integrar validaciones monetarias y de inventario.

## 🛠️ Tecnologías utilizadas

| Herramienta | Uso |
|---|---|
| Python | Implementación y procesamiento de datos |
| JFLAP | Construcción y simulación de autómatas |
| CSV | Almacenamiento de sesiones |
| Git | Control de versiones |
| GitHub | Alojamiento y documentación del proyecto |

## 📂 Estructura del proyecto

La siguiente estructura es una propuesta de organización y debe ajustarse a los archivos reales del repositorio.

```text
Maquina-Dispensadora-Automatas/
├── README.md
├── generador.py
├── monitor.py
├── datos/
│   ├── sesiones_datos.csv
│   ├── sesiones_prueba.csv
│   └── clave_etiquetas_prueba.csv
├── automatas/
│   ├── patron_1.jff
│   ├── patron_2.jff
│   ├── patron_3.jff
│   ├── patron_4.jff
│   ├── patron_5.jff
│   ├── patron_6.jff
│   ├── afnd_unido.jff
│   ├── afd.jff
│   └── afd_minimo.jff
├── resultados/
└── docs/
    └── informe.pdf
```

## ▶️ Ejecución

Para ejecutar el proyecto, se requiere Python 3 y los archivos de datos correspondientes.

Clonar el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Maquina-Dispensadora-Automatas
```

Generar los datos, si el generador está disponible:

```bash
python generador.py
```

Ejecutar el monitor, si el archivo principal se denomina `monitor.py`:

```bash
python monitor.py
```

Los comandos deben ajustarse a los nombres y argumentos implementados en el proyecto.

## 👥 Equipo de trabajo

**Universidad Nacional de Loja**  
Facultad de la Energía, las Industrias y los Recursos Naturales no Renovables  
Carrera de Computación · Ciclo VI, paralelo A

- Marco Castillo
- Juan Castillo
- Ariana Córdova
- Wagner Balcazar

**Docente:** Ing. Genoveva Suing

**Asignatura:** Teoría de Autómatas y Computabilidad Avanzada

## 📚 Referencias

- Hopcroft, J. E., Motwani, R. y Ullman, J. D., *Introduction to Automata Theory, Languages, and Computation*, 3.ª ed. Pearson, 2006.
- Python Software Foundation, [Documentación oficial de Python](https://docs.python.org/3/).
- JFLAP, [Sitio oficial](https://www.jflap.org/).

---

<p align="center">
  <strong>Modelando sistemas reales mediante la teoría de autómatas.</strong><br>
  Universidad Nacional de Loja · Ingeniería en Computación
</p>
