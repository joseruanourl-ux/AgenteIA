#######################
# Agente de IA        #
# Logica del agente   #
#######################

import json

from groq import Groq

from intermediate_tools import IntermediateTools

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = f"""
Eres un asistente financiero y económico que habla en español. Responde de forma clara y concisa: una o dos frases en consultas simples y, en análisis, un resumen de hasta 5 viñetas cortas.

Herramientas:
- consultar_tipo_cambio_api: da el tipo de cambio entre dos monedas. La moneda base es obligatoria, la moneda destino es opcional (por defecto GTQ).
- consultar_precio_cripto_api: da el precio de una criptomoneda. El id de la cripto es obligatorio (ej. bitcoin, ethereum).
- consultar_indicador_banco_mundial_api: da el dato más reciente de un indicador macroeconómico por país usando el código técnico exacto del Banco Mundial (ej. NY.GDP.MKTP.CD). País (2 letras) e indicador son obligatorios.
- consultar_indicador_macro_api: da el dato más reciente de un indicador macroeconómico común (Banco Mundial), usando nombres simples en vez de códigos técnicos. El indicador debe ser uno de: crecimiento_pib, inflacion, desempleo, pib_per_capita, deuda_publica. El país (2 letras, ej. GT, MX, US) es obligatorio.
- consultar_tasa_cambio_frankfurter_api: da el tipo de cambio actual entre dos monedas (datos del Banco Central Europeo). La moneda base y destino son opcionales (por defecto EUR y USD).
- consultar_top_criptos_api: da un listado de las principales criptomonedas por capitalización de mercado. La cantidad y la moneda de referencia son opcionales (por defecto 10 y usd).
- consultar_historial_tasa_cambio_api: da el tipo de cambio entre dos monedas en una fecha pasada. La fecha (formato YYYY-MM-DD) es obligatoria, las monedas son opcionales (por defecto EUR y USD).
- consultar_conversion_moneda_api: convierte un monto de una moneda a otra. El monto y la moneda base son obligatorios, la moneda destino es opcional (por defecto GTQ).
- consultar_comparativo_indicador_banco_mundial_api: compara un indicador macroeconómico entre varios países. La lista de países (2 letras, separados por coma, ej. GT,MX,US) y el indicador (nombre simple o código del Banco Mundial) son obligatorios.
- consultar_serie_historica_banco_mundial_api: da la serie histórica ANUAL de un indicador para uno o varios países (hasta 5), con resumen estadístico (mínimo, máximo, promedio, variación, tendencia) y proyección opcional. Países (2 letras, separados por coma) e indicador (nombre simple o código) son obligatorios; año inicial, año final y años a proyectar (0 a 5) son opcionales (por defecto, los últimos 10 años y sin proyección).
- consultar_proyecciones_fmi_api: da la serie anual de un indicador con las PROYECCIONES OFICIALES del FMI (World Economic Outlook, se actualiza en abril y octubre). El país es obligatorio; el indicador es opcional y debe ser uno de: crecimiento_pib (por defecto), inflacion, desempleo, deuda_publica, pib_per_capita, cuenta_corriente, pib_usd. Año inicial y final son opcionales.
- consultar_clima_api: da el clima actual y el pronóstico de varios días de una ciudad (Open-Meteo). La ciudad es obligatoria; los días (1 a 7) son opcionales (por defecto 3).
- consultar_precio_metales_api: da el precio del oro, la plata, el platino o el paladio por onza troy y por gramo, en dólares u otra moneda (dato diario de referencia). El metal es opcional (oro por defecto) y la moneda también (USD por defecto).
- consultar_mercado_cripto_global_api: da el panorama global del mercado cripto: capitalización total, volumen de 24 horas, dominancia de Bitcoin y cantidad de criptomonedas (CoinPaprika). No necesita parámetros.
- consultar_deuda_publica_eeuu_api: da la deuda pública total de Estados Unidos (Tesoro de EE. UU.) con su variación anual, o las tasas de interés promedio de los títulos del Tesoro. El parámetro dato es opcional: deuda (por defecto) o tasas_interes.
- consultar_indice_miedo_codicia_api: da el índice de miedo y codicia del mercado de criptomonedas (0 a 100). Los días de historial son opcionales (1 a 30).
- consultar_concepto_wikipedia_api: da el resumen de un concepto desde Wikipedia (por ejemplo, un término económico). El tema es obligatorio; el idioma es opcional (es o en).
- consultar_tipo_cambio_banguat_api: da el tipo de cambio de referencia oficial del dólar en quetzales publicado por el Banco de Guatemala. No necesita parámetros.
- consultar_info_pais_banco_mundial_api: da información básica de un país (región, nivel de ingreso, capital) según el Banco Mundial. El código de país de 2 letras es obligatorio.

Si una herramienta regresa un error (por ejemplo, falta de un dato obligatorio o dato no disponible),
debes decírselo al usuario de forma honesta y breve, sin inventar datos.
Reglas de análisis y gráficas:
- Si el usuario pide una gráfica, evolución, tendencia, histórico, comparación en el tiempo, análisis o proyección, usa consultar_serie_historica_banco_mundial_api. La aplicación dibuja la gráfica automáticamente con esos datos, así que NUNCA digas que no puedes hacer gráficas ni intentes dibujarlas con texto.
- Interpreta los datos con base en el resumen que entrega la herramienta; no inventes cifras que la herramienta no devolvió y no repitas la tabla completa.
- Los datos del Banco Mundial son anuales y pueden tener 1 a 2 años de retraso. No hay datos trimestrales ni desglose por rubro (alimentos, vivienda, transporte, etc.): si te lo piden, dilo con honestidad y ofrece la inflación anual general como alternativa.
- Una proyección es solo una extrapolación de tendencia lineal simple, no un pronóstico oficial: acláralo siempre que la presentes.
- Para consultas simples de un dato, regresa el resultado de la herramienta tal cual, considerándolo correcto.
- Si piden el tipo de cambio oficial o de referencia de Guatemala, usa consultar_tipo_cambio_banguat_api y cita al Banco de Guatemala.
- Si piden proyecciones o pronósticos oficiales, usa consultar_proyecciones_fmi_api (la app dibuja la gráfica sola) y cita al FMI. Para una proyección de tendencia propia usa proyectar_anios en la serie histórica.
- Si piden definir un concepto, usa consultar_concepto_wikipedia_api, explícalo con tus propias palabras y menciona que la fuente es Wikipedia.
- Si piden el clima o el pronóstico del tiempo de una ciudad, usa consultar_clima_api e indica que la fuente es Open-Meteo.
- Si piden el precio del oro, la plata u otro metal precioso, usa consultar_precio_metales_api y aclara que es un dato diario de referencia.
- Si piden el panorama o la capitalización total del mercado cripto, usa consultar_mercado_cripto_global_api.
- Menciona siempre la fuente de los datos (Banco Mundial, FMI, Tesoro de EE. UU., Banguat, etc.).
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_tipo_cambio_api",
            "description": (
                "Llama a esta funcion para consultar el tipo de cambio entre dos monedas. "
                "La moneda base es obligatoria. La moneda destino es opcional, por defecto GTQ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda": {
                        "type": "string",
                        "description": "Codigo de la moneda base que se desea consultar, por ejemplo USD"
                    },
                    "moneda_destino": {
                        "type": "string",
                        "description": "Codigo de la moneda destino, por ejemplo GTQ (opcional, por defecto GTQ)"
                    }
                },
                "required": ["moneda"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_precio_cripto_api",
            "description": (
                "Consulta el precio actual de una criptomoneda en una moneda de referencia. "
                "Usa ids de CoinGecko, por ejemplo bitcoin, ethereum, solana."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cripto": {
                        "type": "string",
                        "description": "Id de la criptomoneda, por ejemplo bitcoin"
                    },
                    "moneda_referencia": {
                        "type": "string",
                        "description": "Moneda en la que se quiere el precio, por ejemplo usd"
                    }
                },
                "required": ["cripto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_indicador_banco_mundial_api",
            "description": (
                "Consulta el dato mas reciente de un indicador macroeconomico del Banco Mundial "
                "para un pais, usando el codigo tecnico exacto del indicador, por ejemplo "
                "NY.GDP.MKTP.CD para PIB. Si no conoces el codigo exacto, usa mejor "
                "consultar_indicador_macro_api."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": "Codigo de pais de 2 letras, por ejemplo GT, MX, US"
                    },
                    "indicador": {
                        "type": "string",
                        "description": "Codigo del indicador del Banco Mundial, por ejemplo NY.GDP.MKTP.CD"
                    }
                },
                "required": ["pais", "indicador"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_indicador_macro_api",
            "description": (
                "Consulta el dato mas reciente de un indicador macroeconomico comun "
                "(Banco Mundial) para un pais, usando un nombre simple en vez de un "
                "codigo tecnico. Util para preguntas como crecimiento del PIB, "
                "inflacion, desempleo, PIB per capita o deuda publica."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "indicador": {
                        "type": "string",
                        "description": (
                            "Nombre del indicador. Debe ser uno de: crecimiento_pib, "
                            "inflacion, desempleo, pib_per_capita, deuda_publica"
                        )
                    },
                    "pais": {
                        "type": "string",
                        "description": "Codigo de pais de 2 letras, por ejemplo GT, MX, US"
                    }
                },
                "required": ["indicador", "pais"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_tasa_cambio_frankfurter_api",
            "description": (
                "Consulta el tipo de cambio actual entre dos monedas usando datos de referencia "
                "del Banco Central Europeo. Ambas monedas son opcionales, por defecto EUR a USD."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda_base": {
                        "type": "string",
                        "description": "Codigo de la moneda base, por ejemplo EUR, USD (opcional, por defecto EUR)"
                    },
                    "moneda_destino": {
                        "type": "string",
                        "description": "Codigo de la moneda destino, por ejemplo GTQ (opcional, por defecto USD)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_top_criptos_api",
            "description": (
                "Consulta un listado de las principales criptomonedas ordenadas por "
                "capitalizacion de mercado. La cantidad y la moneda de referencia son opcionales."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cantidad": {
                        "type": "integer",
                        "description": "Cantidad de criptomonedas a listar, entre 1 y 25 (opcional, por defecto 10)"
                    },
                    "moneda_referencia": {
                        "type": "string",
                        "description": "Moneda en la que se quiere el precio, por ejemplo usd (opcional, por defecto usd)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_historial_tasa_cambio_api",
            "description": (
                "Consulta el tipo de cambio entre dos monedas en una fecha pasada especifica, "
                "usando datos de referencia del Banco Central Europeo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha": {
                        "type": "string",
                        "description": "Fecha en formato YYYY-MM-DD, por ejemplo 2024-01-15"
                    },
                    "moneda_base": {
                        "type": "string",
                        "description": "Codigo de la moneda base, por ejemplo EUR, USD (opcional, por defecto EUR)"
                    },
                    "moneda_destino": {
                        "type": "string",
                        "description": "Codigo de la moneda destino, por ejemplo USD (opcional, por defecto USD)"
                    }
                },
                "required": ["fecha"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_conversion_moneda_api",
            "description": (
                "Convierte un monto especifico de una moneda a otra usando tipos de cambio "
                "actuales de referencia del Banco Central Europeo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "monto": {
                        "type": "number",
                        "description": "Cantidad a convertir, por ejemplo 100"
                    },
                    "moneda_base": {
                        "type": "string",
                        "description": "Codigo de la moneda de origen, por ejemplo USD"
                    },
                    "moneda_destino": {
                        "type": "string",
                        "description": "Codigo de la moneda destino, por ejemplo GTQ (opcional, por defecto GTQ)"
                    }
                },
                "required": ["monto", "moneda_base"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_comparativo_indicador_banco_mundial_api",
            "description": (
                "Compara el dato mas reciente de un indicador macroeconomico entre varios "
                "paises del Banco Mundial. El indicador puede ser un nombre simple "
                "(crecimiento_pib, inflacion, desempleo, pib_per_capita, deuda_publica) o un "
                "codigo tecnico del Banco Mundial."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paises": {
                        "type": "string",
                        "description": "Codigos de pais de 2 letras separados por coma, por ejemplo GT,MX,US"
                    },
                    "indicador": {
                        "type": "string",
                        "description": "Nombre simple o codigo tecnico del indicador, por ejemplo inflacion o NY.GDP.MKTP.CD"
                    }
                },
                "required": ["paises", "indicador"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_info_pais_banco_mundial_api",
            "description": (
                "Consulta informacion basica de un pais segun el Banco Mundial: region, "
                "nivel de ingreso y ciudad capital."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": "Codigo de pais de 2 letras, por ejemplo GT, MX, US"
                    }
                },
                "required": ["pais"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_serie_historica_banco_mundial_api",
            "description": (
                "Consulta la serie historica anual de un indicador macroeconomico para uno o varios paises "
                "(Banco Mundial) y devuelve los datos, un resumen estadistico y, opcionalmente, una proyeccion "
                "de tendencia lineal. Sirve para graficar, analizar tendencias y comparar paises en el tiempo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paises": {
                        "type": "string",
                        "description": "Codigos de pais de 2 letras separados por coma (maximo 5), por ejemplo GT o GT,MX,CR"
                    },
                    "indicador": {
                        "type": "string",
                        "description": "Nombre simple (crecimiento_pib, inflacion, desempleo, pib_per_capita, deuda_publica) o codigo del Banco Mundial"
                    },
                    "anio_inicio": {
                        "type": "integer",
                        "description": "Opcional. Ano inicial, por ejemplo 2015. Por defecto, 10 anos antes del final"
                    },
                    "anio_fin": {
                        "type": "integer",
                        "description": "Opcional. Ano final, por ejemplo 2024. Por defecto, el ano actual"
                    },
                    "proyectar_anios": {
                        "type": "integer",
                        "description": "Opcional. Cantidad de anos a proyectar con tendencia lineal (0 a 5). Solo funciona con un unico pais"
                    }
                },
                "required": ["paises", "indicador"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_proyecciones_fmi_api",
            "description": (
                "Consulta la serie anual de un indicador macroeconomico de un pais con las proyecciones oficiales del FMI (World Economic Outlook). Sirve para graficar y para saber que proyecta el FMI."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": "Codigo de pais de 2 letras, por ejemplo GT, MX, US"
                    },
                    "indicador": {
                        "type": "string",
                        "description": "Opcional. crecimiento_pib, inflacion, desempleo, deuda_publica, pib_per_capita, cuenta_corriente o pib_usd. Por defecto crecimiento_pib"
                    },
                    "anio_inicio": {
                        "type": "integer",
                        "description": "Opcional. Ano inicial, por ejemplo 2020"
                    },
                    "anio_fin": {
                        "type": "integer",
                        "description": "Opcional. Ano final, por ejemplo 2030"
                    }
                },
                "required": ["pais"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_clima_api",
            "description": (
                "Consulta el clima actual y el pronostico de los proximos dias de una ciudad (Open-Meteo)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Nombre de la ciudad, por ejemplo Guatemala, Madrid o Nueva York"
                    },
                    "dias": {
                        "type": "integer",
                        "description": "Opcional. Dias de pronostico entre 1 y 7. Por defecto 3"
                    }
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_deuda_publica_eeuu_api",
            "description": (
                "Consulta la deuda publica total de Estados Unidos con su variacion anual, o las tasas de interes promedio de los titulos del Tesoro (Tesoro de EE. UU.)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dato": {
                        "type": "string",
                        "description": "Opcional. deuda (por defecto) o tasas_interes"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_indice_miedo_codicia_api",
            "description": (
                "Consulta el indice de miedo y codicia del mercado de criptomonedas (0 a 100) y opcionalmente su historial reciente."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dias": {
                        "type": "integer",
                        "description": "Opcional. Cantidad de dias de historial entre 1 y 30. Por defecto 1"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_concepto_wikipedia_api",
            "description": (
                "Consulta el resumen de un concepto o termino en Wikipedia, util para definir conceptos economicos y financieros."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tema": {
                        "type": "string",
                        "description": "Concepto a consultar, por ejemplo inflacion o tasa de interes"
                    },
                    "idioma": {
                        "type": "string",
                        "description": "Opcional. es (por defecto) o en"
                    }
                },
                "required": ["tema"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_tipo_cambio_banguat_api",
            "description": (
                "Consulta el tipo de cambio de referencia oficial del dolar en quetzales publicado por el Banco de Guatemala. No requiere parametros."
            ),
            "parameters": {
                "type": "object",
                "properties": {

                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_precio_metales_api",
            "description": (
                "Consulta el precio de un metal precioso (oro, plata, platino o paladio) por onza troy y por gramo, en dolares u otra moneda. Es un dato diario de referencia."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "metal": {
                        "type": "string",
                        "description": "Opcional. oro (por defecto), plata, platino o paladio"
                    },
                    "moneda": {
                        "type": "string",
                        "description": "Opcional. Codigo de la moneda, por ejemplo USD (por defecto), GTQ o EUR"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_mercado_cripto_global_api",
            "description": (
                "Consulta el panorama global del mercado de criptomonedas: capitalizacion total, volumen de 24 horas, dominancia de Bitcoin y numero de criptomonedas. No requiere parametros."
            ),
            "parameters": {
                "type": "object",
                "properties": {

                },
                "required": []
            }
        }
    }
]


def process_response(client:Groq, memory_messages: list[dict], user_text:str, trace: list | None = None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory_messages)
    messages.append({"role": "user", "content": user_text})

    tools = IntermediateTools()

    while True:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS
        )

        msg = resp.choices[0].message

        # Si no hay llamados a herramientas, entonces ya regresamos la respuesta
        if not getattr(msg, "tool_calls", None):
            return msg.content or ""

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")

            if name == "consultar_tipo_cambio_api":
                result = tools.consultar_tipo_cambio_api(
                    moneda=args["moneda"],
                    moneda_destino=args.get("moneda_destino", "GTQ")
                )
            elif name == "consultar_precio_cripto_api":
                result = tools.consultar_precio_cripto_api(
                    cripto=args["cripto"],
                    moneda_referencia=args.get("moneda_referencia", "usd")
                )
            elif name == "consultar_indicador_banco_mundial_api":
                result = tools.consultar_indicador_banco_mundial_api(
                    pais=args["pais"],
                    indicador=args["indicador"]
                )
            elif name == "consultar_indicador_macro_api":
                result = tools.consultar_indicador_macro_api(
                    indicador=args["indicador"],
                    pais=args["pais"]
                )
            elif name == "consultar_tasa_cambio_frankfurter_api":
                result = tools.consultar_tasa_cambio_frankfurter_api(
                    moneda_base=args.get("moneda_base", "EUR"),
                    moneda_destino=args.get("moneda_destino", "USD")
                )
            elif name == "consultar_top_criptos_api":
                result = tools.consultar_top_criptos_api(
                    cantidad=args.get("cantidad", 10),
                    moneda_referencia=args.get("moneda_referencia", "usd")
                )
            elif name == "consultar_historial_tasa_cambio_api":
                result = tools.consultar_historial_tasa_cambio_api(
                    fecha=args["fecha"],
                    moneda_base=args.get("moneda_base", "EUR"),
                    moneda_destino=args.get("moneda_destino", "USD")
                )
            elif name == "consultar_conversion_moneda_api":
                result = tools.consultar_conversion_moneda_api(
                    monto=args["monto"],
                    moneda_base=args["moneda_base"],
                    moneda_destino=args.get("moneda_destino", "GTQ")
                )
            elif name == "consultar_comparativo_indicador_banco_mundial_api":
                result = tools.consultar_comparativo_indicador_banco_mundial_api(
                    paises=args["paises"],
                    indicador=args["indicador"]
                )
            elif name == "consultar_info_pais_banco_mundial_api":
                result = tools.consultar_info_pais_banco_mundial_api(
                    pais=args["pais"]
                )
            elif name == "consultar_serie_historica_banco_mundial_api":
                result = tools.consultar_serie_historica_banco_mundial_api(
                    paises=args["paises"],
                    indicador=args["indicador"],
                    anio_inicio=args.get("anio_inicio"),
                    anio_fin=args.get("anio_fin"),
                    proyectar_anios=args.get("proyectar_anios", 0)
                )
            elif name == "consultar_proyecciones_fmi_api":
                result = tools.consultar_proyecciones_fmi_api(
                    pais=args["pais"],
                    indicador=args.get("indicador", "crecimiento_pib"),
                    anio_inicio=args.get("anio_inicio"),
                    anio_fin=args.get("anio_fin")
                )
            elif name == "consultar_clima_api":
                result = tools.consultar_clima_api(ciudad=args["ciudad"], dias=args.get("dias", 3))
            elif name == "consultar_deuda_publica_eeuu_api":
                result = tools.consultar_deuda_publica_eeuu_api(dato=args.get("dato", "deuda"))
            elif name == "consultar_indice_miedo_codicia_api":
                result = tools.consultar_indice_miedo_codicia_api(dias=args.get("dias", 1))
            elif name == "consultar_concepto_wikipedia_api":
                result = tools.consultar_concepto_wikipedia_api(
                    tema=args["tema"],
                    idioma=args.get("idioma", "es")
                )
            elif name == "consultar_tipo_cambio_banguat_api":
                result = tools.consultar_tipo_cambio_banguat_api()
            elif name == "consultar_precio_metales_api":
                result = tools.consultar_precio_metales_api(
                    metal=args.get("metal", "oro"),
                    moneda=args.get("moneda", "USD")
                )
            elif name == "consultar_mercado_cripto_global_api":
                result = tools.consultar_mercado_cripto_global_api()
            else:
                print(f"Se intentó llamar a una herramienta desconocida {name}")
                result = {"error": f"Herramienta desconocida: {name}"}

            # Registrar la llamada (para mostrarla en la interfaz)
            if trace is not None:
                trace.append({"herramienta": name, "argumentos": args, "resultado": result})

            # Agregar a los mensajes el resultado del llamado de la herramienta
            # Esto lo recibirá el modelo al continuar la iteración
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })
