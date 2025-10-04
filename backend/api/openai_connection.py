"""Generic OpenAI assistant template that accepts a prompt and returns a JSON reply.

The script can receive its configuration either through command-line arguments or by
passing a JSON object via stdin with keys such as:

{
  "prompt": "Describe your output structure",
  "system": "Optional system message",
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "max_tokens": 500
}

Run ``python openai_assistant.py --help`` for CLI usage. The output is always a JSON
object emitted to stdout. Logging information is printed to stderr with the ``[INFO]``
prefix so it can be separated easily from the JSON payload.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

try:
    from constants import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
except ImportError:
    # Enable execution via `python api/openai_connection.py`.
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from constants import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE


DEFAULT_MODEL = OPENAI_MODEL or "gpt-4o-mini"

try:
    DEFAULT_TEMPERATURE = float(OPENAI_TEMPERATURE) if OPENAI_TEMPERATURE is not None else 0.2
except ValueError:
    print("[INFO] OPENAI_TEMPERATURE inválido; usando 0.2.", file=sys.stderr)
    DEFAULT_TEMPERATURE = 0.2
DEFAULT_SYSTEM_PROMPT = (
    "Eres un asistente que siempre responde con JSON válido. El JSON debe ser un "
    "objeto UTF-8 sin comentarios ni texto adicional."
)


@dataclass
class PromptRequest:
    prompt: str
    system: str
    model: str
    temperature: float
    max_tokens: Optional[int]


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solicita una respuesta JSON al modelo de OpenAI.")
    parser.add_argument("--prompt", help="Prompt a enviar al modelo. Si se omite, se busca en stdin.")
    parser.add_argument("--system", help="Mensaje del sistema para guiar la respuesta.")
    parser.add_argument("--model", help=f"Modelo a utilizar (default: {DEFAULT_MODEL}).")
    parser.add_argument("--temperature", type=float, help="Temperatura de muestreo para el modelo.")
    parser.add_argument("--max-tokens", type=int, help="Límite de tokens en la respuesta del modelo.")
    parser.add_argument("--test", action="store_true", help="Prueba rápida de conexión con el modelo.")
    return parser


def _create_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise SystemExit("OPENAI_API_KEY no está definido en el entorno.")
    return OpenAI(api_key=OPENAI_API_KEY)


def _read_payload_from_stdin() -> Dict[str, Any]:
    if sys.stdin.isatty():
        return {}

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Entrada JSON inválida: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit("La entrada estándar debe contener un objeto JSON.")
    return payload


def _load_request(args: argparse.Namespace) -> PromptRequest:
    payload = _read_payload_from_stdin()

    prompt = args.prompt or payload.get("prompt")
    if not prompt:
        raise SystemExit("No se proporcionó prompt. Usa --prompt o pasa un JSON por stdin.")

    system_prompt = args.system or payload.get("system") or DEFAULT_SYSTEM_PROMPT
    model = args.model or payload.get("model") or DEFAULT_MODEL

    temperature_value: Optional[float]
    if args.temperature is not None:
        temperature_value = args.temperature
    else:
        temperature_value = _coerce_float(payload.get("temperature"), DEFAULT_TEMPERATURE)

    max_tokens_value = args.max_tokens if args.max_tokens is not None else _coerce_int(payload.get("max_tokens"))

    return PromptRequest(
        prompt=prompt,
        system=system_prompt,
        model=model,
        temperature=temperature_value,
        max_tokens=max_tokens_value,
    )


def _coerce_float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _coerce_int(value: Any) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def request_json_response(request: PromptRequest) -> Dict[str, Any]:
    print("[INFO] Creando cliente de OpenAI...", file=sys.stderr)
    client = _create_client()

    messages = [{"role": "system", "content": request.system}, {"role": "user", "content": request.prompt}]

    print(f"[INFO] Enviando prompt al modelo {request.model}...", file=sys.stderr)
    response = client.chat.completions.create(
        model=request.model,
        messages=messages,
        temperature=request.temperature,
        response_format={"type": "json_object"},
        **({"max_tokens": request.max_tokens} if request.max_tokens is not None else {}),
    )

    content = response.choices[0].message.content or "{}"

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("El modelo no devolvió JSON válido.") from exc


def test_openai_connection() -> Dict[str, Any]:
    print("[INFO] Probando conexión con OpenAI...", file=sys.stderr)
    request = PromptRequest(
        prompt="Devuelve {\"status\": \"ok\"}",
        system=DEFAULT_SYSTEM_PROMPT,
        model=DEFAULT_MODEL,
        temperature=0.0,
        max_tokens=60,
    )
    response = request_json_response(request)
    print("[INFO] Conexión exitosa; respuesta recibida.", file=sys.stderr)
    return response


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.test:
        response = test_openai_connection()
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    request = _load_request(args)

    print("[INFO] Enviando solicitud al asistente...", file=sys.stderr)
    response = request_json_response(request)
    print("[INFO] Respuesta recibida; escribiendo salida JSON.", file=sys.stderr)
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_openai_connection()
