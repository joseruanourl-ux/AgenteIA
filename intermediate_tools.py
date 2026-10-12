#######################
# Agente Basico De IA #
# Herramientas        #
#######################

# Importacion para el manejo de sistema
import os
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

    # Herramienta para consultar indicadores económicos del Banco Mundial (publica, sin API key)
    def consultar_indicador_banco_mundial_api(self, pais: str, indicador: str):
        print(f"Herramienta consultar_indicador_banco_mundial_api llamada con pais: {pais}, indicador: {indicador}")

        if not pais or not indicador:
            return "Error: Se requiere el código de país (ej. GT, MX, US) y el código de indicador (ej. NY.GDP.MKTP.CD)."

        url = (
            f"https://api.worldbank.org/v2/country/{pais.upper()}/indicator/{indicador}"
            f"?format=json&per_page=5&mrnev=1"
        )

        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                return f"ERROR: No se encontró el indicador {indicador} para el país: {pais}"

            observaciones = [o for o in data[1] if o.get("value") is not None]
            if not observaciones:
                return f"ERROR: No hay datos disponibles para el indicador {indicador} en el país: {pais}"

            reciente = observaciones[0]
            return {
                "pais": reciente.get("country", {}).get("value"),
                "indicador": reciente.get("indicator", {}).get("value"),
                "anio": reciente.get("date"),
                "valor": reciente.get("value")
            }
        except Exception as e:
            print(f"Error al consultar_indicador_banco_mundial_api: {pais}/{indicador}. Error: {e}")
            return f"ERROR: No se pudo obtener el indicador {indicador} para el país: {pais}"

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

    # Herramienta para convertir un monto entre dos monedas (Frankfurter.app,
    # mismo proveedor que consultar_tasa_cambio_frankfurter_api).
    def consultar_conversion_moneda_api(self, monto: float, moneda_base: str, moneda_destino: str = "GTQ"):
        print(f"Herramienta consultar_conversion_moneda_api llamada con monto: {monto}, base: {moneda_base}, destino: {moneda_destino}")

        if monto is None or not moneda_base:
            return "Error: Se requiere el monto y la moneda base (ej. 100 USD)."

        base = moneda_base.upper()
        destino = moneda_destino.upper() if moneda_destino else "GTQ"

        url = "https://api.frankfurter.app/latest"
        params = {"amount": monto, "from": base, "to": destino}

        try:
            response = requests.get(url, params=params, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            resultado = (data.get("rates") or {}).get(destino)
            if resultado is None:
                return f"ERROR: No se pudo convertir de {base} a {destino}."

            return {
                "monto_original": data.get("amount"),
                "moneda_base": data.get("base"),
                "moneda_destino": destino,
                "monto_convertido": resultado,
                "fecha": data.get("date")
            }
        except Exception as e:
            print(f"Error al consultar_conversion_moneda_api: {monto} {moneda_base}->{moneda_destino}. Error: {e}")
            return f"ERROR: No se pudo convertir la moneda: {moneda_base} a {moneda_destino}"

    # Herramienta para comparar un indicador macroeconomico entre varios paises
    # (Banco Mundial, mismo proveedor que las otras herramientas de indicadores).
    def consultar_comparativo_indicador_banco_mundial_api(self, paises: str, indicador: str):
        print(f"Herramienta consultar_comparativo_indicador_banco_mundial_api llamada con paises: {paises}, indicador: {indicador}")

        if not paises or not indicador:
            return "Error: Se requieren los códigos de país separados por coma (ej. GT,MX,US) y el indicador (nombre simple o código del Banco Mundial)."

        codigo = self._macro_indicadores.get(indicador.lower(), indicador)
        lista_paises = ";".join(p.strip().upper() for p in paises.split(",") if p.strip())

        if not lista_paises:
            return "Error: Se requiere al menos un código de país válido (ej. GT,MX,US)."

        url = (
            f"https://api.worldbank.org/v2/country/{lista_paises}/indicator/{codigo}"
            f"?format=json&per_page=100&mrnev=1"
        )

        try:
            response = requests.get(url, headers=self._default_headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                return f"ERROR: No se encontraron datos del indicador {indicador} para los países: {paises}"

            resultados = {}
            for obs in data[1]:
                if obs.get("value") is None:
                    continue
                nombre_pais = obs.get("country", {}).get("value")
                if nombre_pais not in resultados:
                    resultados[nombre_pais] = {"anio": obs.get("date"), "valor": obs.get("value")}

            if not resultados:
                return f"ERROR: No hay datos disponibles del indicador {indicador} para los países: {paises}"

            return resultados
        except Exception as e:
            print(f"Error al consultar_comparativo_indicador_banco_mundial_api: {paises}/{indicador}. Error: {e}")
            return f"ERROR: No se pudo obtener el comparativo del indicador: {indicador}"

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