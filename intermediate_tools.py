#######################
# Agente Basico De IA #
# Herramientas        #
#######################

# Importacion para el manejo de sistema
import os
import unicodedata
from datetime import datetime
import requests


class IntermediateTools:

    def __init__(self):
        # Cabecera generica tipo navegador. Varias APIs publicas
        # bloquean con 403 el User-Agent por defecto que manda "requests".
        self._default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

        # Mapa de indicadores macroeconomicos "amigables" hacia los codigos
        # tecnicos del Banco Mundial.
        self._macro_indicadores = {
            "crecimiento_pib": "NY.GDP.MKTP.KD.ZG",
            "inflacion": "FP.CPI.TOTL.ZG",
            "desempleo": "SL.UEM.TOTL.ZS",
            "pib_per_capita": "NY.GDP.PCAP.CD",
            "deuda_publica": "GC.DOD.TOTL.GD.ZS",
        }

    # ------------------------------------------------------------------
    # Herramientas originales que SI funcionan
    # ------------------------------------------------------------------

    # Herramienta para consultar el tipo de cambio (open.er-api.com, publica, sin API key)
    def consultar_tipo_cambio_api(self, moneda: str, moneda_destino: str = "GTQ"):
        print(f"Herramienta consultar_tipo_cambio_api llamada con moneda: {moneda}, moneda_destino: {moneda_destino}")

        if not moneda:
            return "Error: Se requiere el código de la moneda base para obtener el tipo de cambio."

        url = f"https://open.er-api.com/v6/latest/{moneda.upper()}"

        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                return f"ERROR: No se pudo obtener el tipo de cambio para la moneda: {moneda}"

            rates = data.get("rates", {})
            destino = moneda_destino.upper() if moneda_destino else "GTQ"
            tasa = rates.get(destino)

            if tasa is None:
                return f"ERROR: No se encontró la moneda destino {destino} para la base {moneda}"

            return {
                "moneda_base": moneda.upper(),
                "moneda_destino": destino,
                "tasa": tasa,
                "fecha_actualizacion": data.get("time_last_update_utc")
            }
        except Exception as e:
            print(f"Error al consultar_tipo_cambio_api: {moneda}. Error: {e}")
            return f"ERROR: No se pudo obtener el tipo de cambio para la moneda: {moneda}"

    # Herramienta para consultar el precio de una criptomoneda (CoinGecko, publica, sin API key)
    def consultar_precio_cripto_api(self, cripto: str, moneda_referencia: str = "usd"):
        print(f"Herramienta consultar_precio_cripto_api llamada con cripto: {cripto}, referencia: {moneda_referencia}")

        if not cripto:
            return "Error: Se requiere el id de la criptomoneda (ej. bitcoin, ethereum)."

        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": cripto.lower(),
            "vs_currencies": moneda_referencia.lower(),
        }

        try:
            response = requests.get(url, params=params, headers=self._default_headers, timeout=30)

            if response.status_code == 429:
                return "ERROR: Se alcanzó el límite de peticiones gratuitas de CoinGecko, intenta de nuevo en unos segundos."

            response.raise_for_status()
            data = response.json()
            if not data:
                return f"ERROR: No se encontró la criptomoneda: {cripto}"
            return data
        except Exception as e:
            print(f"Error al consultar_precio_cripto_api: {cripto}. Error: {e}")
            return f"ERROR: No se pudo obtener el precio de la criptomoneda: {cripto}"

    # ------------------------------------------------------------------
    # Ayudas internas para el Banco Mundial
    # ------------------------------------------------------------------

    _PAISES = {
        "guatemala": "GT", "mexico": "MX", "estados unidos": "US", "usa": "US",
        "eeuu": "US", "ee.uu.": "US", "costa rica": "CR", "honduras": "HN",
        "el salvador": "SV", "nicaragua": "NI", "panama": "PA", "belice": "BZ",
        "colombia": "CO", "venezuela": "VE", "ecuador": "EC", "peru": "PE",
        "bolivia": "BO", "chile": "CL", "argentina": "AR", "uruguay": "UY",
        "paraguay": "PY", "brasil": "BR", "brazil": "BR", "cuba": "CU",
        "republica dominicana": "DO", "espana": "ES", "alemania": "DE",
        "francia": "FR", "italia": "IT", "reino unido": "GB", "canada": "CA",
        "china": "CN", "japon": "JP", "india": "IN",
    }

    def _normalizar_pais(self, pais: str) -> str:
        # Acepta codigo de 2 letras o un nombre comun en español y devuelve el codigo.
        limpio = unicodedata.normalize("NFKD", (pais or "").strip().lower())
        limpio = "".join(c for c in limpio if not unicodedata.combining(c))
        return self._PAISES.get(limpio, limpio.upper())

    def _bm_ultimo_dato(self, pais: str, codigo: str):
        # Consulta UN pais y UN indicador. Devuelve dict con el dato o str con el error.
        url = (
            f"https://api.worldbank.org/v2/country/{pais}/indicator/{codigo}"
            f"?format=json&per_page=5&mrnev=1"
        )
        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return f"fallo la consulta al Banco Mundial ({type(e).__name__}: {e})"

        if isinstance(data, list) and data and isinstance(data[0], dict) and "message" in data[0]:
            mensajes = data[0].get("message") or []
            detalle = mensajes[0].get("value") if mensajes and isinstance(mensajes[0], dict) else "respuesta de error"
            return f"el Banco Mundial rechazo la consulta: {detalle}"

        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return "no se encontraron datos para ese pais e indicador"

        observaciones = [o for o in data[1] if o.get("value") is not None]
        if not observaciones:
            return "no hay datos disponibles para ese pais e indicador"

        reciente = observaciones[0]
        return {
            "pais": (reciente.get("country") or {}).get("value"),
            "indicador": (reciente.get("indicator") or {}).get("value"),
            "anio": reciente.get("date"),
            "valor": reciente.get("value"),
        }

    # Herramienta para consultar indicadores económicos del Banco Mundial (publica, sin API key)
    def consultar_indicador_banco_mundial_api(self, pais: str, indicador: str):
        print(f"Herramienta consultar_indicador_banco_mundial_api llamada con pais: {pais}, indicador: {indicador}")

        if not pais or not indicador:
            return "Error: Se requiere el código de país (ej. GT, MX, US) y el código de indicador (ej. NY.GDP.MKTP.CD)."

        codigo_pais = self._normalizar_pais(pais)
        codigo = self._macro_indicadores.get(indicador.strip().lower(), indicador.strip())

        resultado = self._bm_ultimo_dato(codigo_pais, codigo)
        if isinstance(resultado, str):
            print(f"Error en consultar_indicador_banco_mundial_api: {codigo_pais}/{codigo}: {resultado}")
            return f"ERROR: {resultado} (pais: {codigo_pais}, indicador: {codigo})"
        return resultado

    # Herramienta para consultar un indicador macroeconomico comun (Banco Mundial, publica, sin API key)
    def consultar_indicador_macro_api(self, indicador: str, pais: str):
        print(f"Herramienta consultar_indicador_macro_api llamada con indicador: {indicador}, pais: {pais}")

        if not indicador or not pais:
            disponibles = ", ".join(self._macro_indicadores.keys())
            return f"Error: Se requiere el indicador (uno de: {disponibles}) y el código de país (ej. GT, MX, US)."

        codigo = self._macro_indicadores.get(indicador.lower())
        if not codigo:
            disponibles = ", ".join(self._macro_indicadores.keys())
            return f"Error: Indicador no reconocido. Usa uno de: {disponibles}"

        url = (
            f"https://api.worldbank.org/v2/country/{pais.upper()}/indicator/{codigo}"
            f"?format=json&per_page=5&mrnev=1"
        )

        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                return f"ERROR: No hay datos para el indicador {indicador} en el país: {pais}"

            observaciones = [o for o in data[1] if o.get("value") is not None]
            if not observaciones:
                return f"ERROR: No hay datos disponibles para el indicador {indicador} en el país: {pais}"

            reciente = observaciones[0]
            return {
                "pais": reciente.get("country", {}).get("value"),
                "indicador": indicador.lower(),
                "anio": reciente.get("date"),
                "valor": reciente.get("value")
            }
        except Exception as e:
            print(f"Error al consultar_indicador_macro_api: {indicador}/{pais}. Error: {e}")
            return f"ERROR: No se pudo obtener el indicador macroeconómico: {indicador}/{pais}"

    # Herramienta para consultar tipos de cambio actuales (Frankfurter.app, publica, sin API key)
    def consultar_tasa_cambio_frankfurter_api(self, moneda_base: str = "EUR", moneda_destino: str = "USD"):
        print(f"Herramienta consultar_tasa_cambio_frankfurter_api llamada con base: {moneda_base}, destino: {moneda_destino}")

        if not moneda_base:
            return "Error: Se requiere la moneda base (ej. EUR, USD)."

        destino = moneda_destino.upper() if moneda_destino else "USD"
        url = "https://api.frankfurter.app/latest"
        params = {"from": moneda_base.upper(), "to": destino}

        try:
            response = requests.get(url, params=params, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            tasa = (data.get("rates") or {}).get(destino)
            if tasa is None:
                return f"ERROR: No se encontró la moneda destino {destino}"

            return {
                "moneda_base": data.get("base"),
                "moneda_destino": destino,
                "tasa": tasa,
                "fecha": data.get("date")
            }
        except Exception as e:
            print(f"Error al consultar_tasa_cambio_frankfurter_api: {moneda_base}/{moneda_destino}. Error: {e}")
            return f"ERROR: No se pudo obtener el tipo de cambio para: {moneda_base}"

    # ------------------------------------------------------------------
    # Herramientas nuevas (mismos proveedores que ya funcionan)
    # ------------------------------------------------------------------

    # Herramienta para consultar las principales criptomonedas por capitalización
    # de mercado (CoinGecko, mismo proveedor que consultar_precio_cripto_api).
    def consultar_top_criptos_api(self, cantidad: int = 10, moneda_referencia: str = "usd"):
        print(f"Herramienta consultar_top_criptos_api llamada con cantidad: {cantidad}, referencia: {moneda_referencia}")

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 10
        cantidad = max(1, min(cantidad, 25))

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": (moneda_referencia or "usd").lower(),
            "order": "market_cap_desc",
            "per_page": cantidad,
            "page": 1,
            "sparkline": "false",
        }

        try:
            response = requests.get(url, params=params, headers=self._default_headers, timeout=30)

            if response.status_code == 429:
                return "ERROR: Se alcanzó el límite de peticiones gratuitas de CoinGecko, intenta de nuevo en unos segundos."

            response.raise_for_status()
            data = response.json()

            if not data:
                return f"ERROR: No se encontraron criptomonedas para la moneda de referencia: {moneda_referencia}"

            return [
                {
                    "id": c.get("id"),
                    "simbolo": c.get("symbol"),
                    "nombre": c.get("name"),
                    "precio": c.get("current_price"),
                    "cambio_24h_porcentaje": c.get("price_change_percentage_24h"),
                    "capitalizacion_mercado": c.get("market_cap"),
                }
                for c in data
            ]
        except Exception as e:
            print(f"Error al consultar_top_criptos_api. Error: {e}")
            return "ERROR: No se pudo obtener el listado de las criptomonedas principales."

    # Herramienta para consultar un tipo de cambio historico en una fecha pasada
    # (Frankfurter.app, mismo proveedor que consultar_tasa_cambio_frankfurter_api).
    def consultar_historial_tasa_cambio_api(self, fecha: str, moneda_base: str = "EUR", moneda_destino: str = "USD"):
        print(f"Herramienta consultar_historial_tasa_cambio_api llamada con fecha: {fecha}, base: {moneda_base}, destino: {moneda_destino}")

        if not fecha:
            return "Error: Se requiere la fecha en formato YYYY-MM-DD (ej. 2024-01-15)."

        base = moneda_base.upper() if moneda_base else "EUR"
        destino = moneda_destino.upper() if moneda_destino else "USD"

        url = f"https://api.frankfurter.app/{fecha}"
        params = {"from": base, "to": destino}

        try:
            response = requests.get(url, params=params, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            tasa = (data.get("rates") or {}).get(destino)
            if tasa is None:
                return f"ERROR: No se encontró el tipo de cambio de {base} a {destino} para la fecha {fecha}."

            return {
                "moneda_base": data.get("base"),
                "moneda_destino": destino,
                "tasa": tasa,
                "fecha": data.get("date")
            }
        except Exception as e:
            print(f"Error al consultar_historial_tasa_cambio_api: {fecha}. Error: {e}")
            return f"ERROR: No se pudo obtener el tipo de cambio histórico para la fecha: {fecha}"

    # Herramienta para convertir un monto entre dos monedas (open.er-api.com,
    # publica, sin API key). Se usa este proveedor porque soporta GTQ; Frankfurter
    # (Banco Central Europeo) no incluye el quetzal.
    def consultar_conversion_moneda_api(self, monto: float, moneda_base: str, moneda_destino: str = "GTQ"):
        print(f"Herramienta consultar_conversion_moneda_api llamada con monto: {monto}, base: {moneda_base}, destino: {moneda_destino}")

        if monto is None or not moneda_base:
            return "Error: Se requiere el monto y la moneda base (ej. 100 USD)."

        try:
            monto = float(monto)
        except (TypeError, ValueError):
            return f"Error: El monto debe ser un número, se recibió: {monto}"

        base = moneda_base.upper()
        destino = moneda_destino.upper() if moneda_destino else "GTQ"

        url = f"https://open.er-api.com/v6/latest/{base}"

        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                return f"ERROR: No se pudo convertir de {base} a {destino}."

            tasa = (data.get("rates") or {}).get(destino)
            if tasa is None:
                return f"ERROR: No se encontró la moneda destino {destino} para la base {base}."

            return {
                "monto_original": monto,
                "moneda_base": base,
                "moneda_destino": destino,
                "tasa": tasa,
                "monto_convertido": round(monto * tasa, 2),
                "fecha_actualizacion": data.get("time_last_update_utc")
            }
        except Exception as e:
            print(f"Error al consultar_conversion_moneda_api: {monto} {moneda_base}->{moneda_destino}. Error: {e}")
            return f"ERROR: No se pudo convertir la moneda: {moneda_base} a {moneda_destino}"

    # Herramienta para comparar un indicador macroeconomico entre varios paises
    # (Banco Mundial). Consulta un pais a la vez, igual que las otras herramientas
    # de indicadores, y junta los resultados.
    def consultar_comparativo_indicador_banco_mundial_api(self, paises: str, indicador: str):
        print(f"Herramienta consultar_comparativo_indicador_banco_mundial_api llamada con paises: {paises}, indicador: {indicador}")

        if not paises or not indicador:
            return "Error: Se requieren los códigos de país separados por coma (ej. GT,MX,US) y el indicador (nombre simple o código del Banco Mundial)."

        codigo = self._macro_indicadores.get(indicador.strip().lower(), indicador.strip())
        lista = [self._normalizar_pais(p) for p in paises.split(",") if p.strip()]

        if not lista:
            return "Error: Se requiere al menos un código de país válido (ej. GT,MX,US)."

        resultados = {}
        errores = {}
        for p in lista[:10]:
            dato = self._bm_ultimo_dato(p, codigo)
            if isinstance(dato, str):
                errores[p] = dato
            else:
                resultados[dato.get("pais") or p] = {"anio": dato.get("anio"), "valor": dato.get("valor")}

        if not resultados:
            print(f"Error en consultar_comparativo_indicador_banco_mundial_api: {errores}")
            return f"ERROR: No se pudo obtener el indicador {indicador} para ningún país. Detalle: {errores}"

        if errores:
            resultados["_paises_sin_datos"] = errores
        return resultados

    # ------------------------------------------------------------------
    # Series historicas, resumen estadistico y proyeccion (Banco Mundial)
    # ------------------------------------------------------------------

    def _bm_serie(self, pais: str, codigo: str, anio_inicio: int, anio_fin: int):
        # Serie anual de UN pais y UN indicador. Devuelve dict o str con el error.
        url = (
            f"https://api.worldbank.org/v2/country/{pais}/indicator/{codigo}"
            f"?format=json&per_page=200&date={anio_inicio}:{anio_fin}"
        )
        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return f"fallo la consulta al Banco Mundial ({type(e).__name__}: {e})"

        if isinstance(data, list) and data and isinstance(data[0], dict) and "message" in data[0]:
            mensajes = data[0].get("message") or []
            detalle = mensajes[0].get("value") if mensajes and isinstance(mensajes[0], dict) else "respuesta de error"
            return f"el Banco Mundial rechazo la consulta: {detalle}"
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return "no se encontraron datos para ese pais e indicador"

        puntos, nombre_pais, nombre_ind = {}, None, None
        for o in data[1]:
            nombre_pais = nombre_pais or (o.get("country") or {}).get("value")
            nombre_ind = nombre_ind or (o.get("indicator") or {}).get("value")
            if o.get("value") is None:
                continue
            try:
                puntos[int(o["date"])] = round(float(o["value"]), 2)
            except (TypeError, ValueError, KeyError):
                continue
        if not puntos:
            return "no hay datos disponibles en ese periodo"
        return {"pais": nombre_pais or pais, "indicador": nombre_ind, "datos": dict(sorted(puntos.items()))}

    @staticmethod
    def _resumen_serie(datos: dict):
        # Estadisticas calculadas en Python (no por el modelo) para evitar errores de calculo.
        anios, vals = list(datos.keys()), list(datos.values())
        n = len(vals)
        i_min, i_max = vals.index(min(vals)), vals.index(max(vals))
        resumen = {
            "n_anios": n,
            "primer_dato": {"anio": anios[0], "valor": vals[0]},
            "ultimo_dato": {"anio": anios[-1], "valor": vals[-1]},
            "minimo": {"anio": anios[i_min], "valor": vals[i_min]},
            "maximo": {"anio": anios[i_max], "valor": vals[i_max]},
            "promedio": round(sum(vals) / n, 2),
            "variacion_total": round(vals[-1] - vals[0], 2),
        }
        if n >= 3:
            pendiente, _ = _regresion_lineal(anios, vals)
            amplitud = max(vals) - min(vals)
            cambio = pendiente * (anios[-1] - anios[0])
            if amplitud == 0 or abs(cambio) < 0.15 * amplitud:
                resumen["tendencia"] = "estable (sin tendencia clara)"
            else:
                resumen["tendencia"] = "al alza" if pendiente > 0 else "a la baja"
        return resumen

    # Herramienta para series historicas de un indicador (Banco Mundial, publica, sin API key).
    # Devuelve datos anuales + resumen estadistico + proyeccion opcional. La app dibuja la grafica.
    def consultar_serie_historica_banco_mundial_api(self, paises: str, indicador: str, anio_inicio=None, anio_fin=None, proyectar_anios=0):
        print(f"Herramienta consultar_serie_historica_banco_mundial_api llamada con paises: {paises}, indicador: {indicador}, "
              f"anio_inicio: {anio_inicio}, anio_fin: {anio_fin}, proyectar_anios: {proyectar_anios}")

        if not paises or not indicador:
            disponibles = ", ".join(self._macro_indicadores.keys())
            return f"Error: Se requieren los países (ej. GT o GT,MX) y el indicador (uno de: {disponibles}, o un código del Banco Mundial)."

        codigo = self._macro_indicadores.get(indicador.strip().lower(), indicador.strip())
        lista = [self._normalizar_pais(p) for p in str(paises).split(",") if p.strip()][:5]

        actual = datetime.now().year
        try:
            fin = int(anio_fin) if anio_fin else actual
            ini = int(anio_inicio) if anio_inicio else fin - 10
            proy = max(0, min(int(proyectar_anios or 0), 5))
        except (TypeError, ValueError):
            return "Error: los años deben ser números (ej. 2015)."
        fin = min(fin, actual)
        ini = max(ini, 1960)
        if ini >= fin:
            return "Error: el año inicial debe ser menor que el año final."
        if fin - ini > 40:
            ini = fin - 40

        series, errores, nombre_ind = {}, {}, None
        for p in lista:
            r = self._bm_serie(p, codigo, ini, fin)
            if isinstance(r, str):
                errores[p] = r
                continue
            nombre_ind = nombre_ind or r["indicador"]
            series[r["pais"]] = {
                "datos": {str(a): v for a, v in r["datos"].items()},
                "resumen": self._resumen_serie(r["datos"]),
            }

        if not series:
            print(f"Error en consultar_serie_historica_banco_mundial_api: {errores}")
            return f"ERROR: No se pudo obtener la serie de {indicador}. Detalle: {errores}"

        salida = {
            "indicador": nombre_ind or indicador,
            "codigo": codigo,
            "periodo_solicitado": f"{ini}-{fin}",
            "frecuencia": "anual (el Banco Mundial suele publicar con 1 a 2 años de retraso)",
            "series": series,
        }

        if proy and len(series) == 1:
            nombre = next(iter(series))
            datos = {int(a): v for a, v in series[nombre]["datos"].items()}
            if len(datos) >= 4:
                pendiente, ordenada = _regresion_lineal(list(datos.keys()), list(datos.values()))
                ultimo = max(datos)
                salida["proyeccion"] = {
                    "pais": nombre,
                    "metodo": "extrapolación de tendencia lineal simple; NO es un pronóstico oficial",
                    "datos": {str(ultimo + i): round(pendiente * (ultimo + i) + ordenada, 2) for i in range(1, proy + 1)},
                }
            else:
                salida["aviso"] = "Hay muy pocos datos para proyectar (se necesitan al menos 4 años)."
        elif proy:
            salida["aviso"] = "La proyección solo se calcula cuando se consulta un único país."

        if errores:
            salida["paises_sin_datos"] = errores
        return salida

    # Herramienta para consultar informacion basica de un pais (Banco Mundial,
    # mismo proveedor que las otras herramientas de indicadores; reemplaza a
    # REST Countries, que dejo de responder de forma confiable).
    def consultar_info_pais_banco_mundial_api(self, pais: str):
        print(f"Herramienta consultar_info_pais_banco_mundial_api llamada con pais: {pais}")

        if not pais:
            return "Error: Se requiere el código de país de 2 letras (ej. GT, MX, US)."

        url = f"https://api.worldbank.org/v2/country/{pais.upper()}?format=json"

        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                return f"ERROR: No se encontró información para el país: {pais}"

            info = data[1][0]
            return {
                "nombre": info.get("name"),
                "region": (info.get("region") or {}).get("value"),
                "nivel_ingreso": (info.get("incomeLevel") or {}).get("value"),
                "capital": info.get("capitalCity"),
            }
        except Exception as e:
            print(f"Error al consultar_info_pais_banco_mundial_api: {pais}. Error: {e}")
            return f"ERROR: No se pudo obtener información para el país: {pais}"


def _regresion_lineal(xs, ys):
    # Minimos cuadrados simple: devuelve (pendiente, ordenada).
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, my
    pendiente = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return pendiente, my - pendiente * mx
