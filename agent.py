#######################
# Agente de IA        #
# Logica del agente   #
#######################

import json

from groq import Groq

from intermediate_tools import IntermediateTools

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = f"""
Eres un asistente que habla en español y responde de manera muy breve y concisa.

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
- consultar_info_pais_banco_mundial_api: da información básica de un país (región, nivel de ingreso, capital) según el Banco Mundial. El código de país de 2 letras es obligatorio.

Si una herramienta regresa un error (por ejemplo, falta de un dato obligatorio o dato no disponible),
debes decírselo al usuario de forma honesta y breve, sin inventar datos.
La respuesta de una herramienta exitosa debes regresarla tal cual, considerando que es correcta.
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
