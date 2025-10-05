#!/usr/bin/env python3
"""
Descarga de datos MERRA-2 (NASA Earthdata)
Optimizado para hackathon — manejo de errores, autenticación y progreso.

Autor: Mario | 2025
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import earthaccess
import time
import sys


# =============================================================
# 🎨 Estilos consola
# =============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"

def log_info(msg): print(f"{CYAN}[INFO]{RESET} {msg}")
def log_ok(msg): print(f"{GREEN}[OK]{RESET} {msg}")
def log_warn(msg): print(f"{YELLOW}[WARN]{RESET} {msg}")
def log_err(msg): print(f"{RED}[ERR]{RESET} {msg}")


# =============================================================
# 🔐 Autenticación segura
# =============================================================

def ensure_login():
    """Asegura que Earthdata esté autenticado correctamente."""
    log_info("Autenticando con NASA Earthdata...")

    auth = earthaccess.login(strategy="netrc")
    if not (auth and getattr(auth, "authenticated", False)):
        log_warn("Autenticación con .netrc fallida. Intentando login interactivo...")
        auth = earthaccess.login(strategy="interactive")

    if auth and getattr(auth, "authenticated", False):
        log_ok("Autenticación exitosa ✅")
    else:
        log_err("No se pudo autenticar en NASA Earthdata. Verifica tus credenciales o conexión.")
        sys.exit(1)


# =============================================================
# 🔧 Descarga MERRA-2
# =============================================================

def download_merra2_product(product, start, end, bbox, dest, threads=2, max_retries=3):
    """Descarga un producto MERRA-2 con reintentos automáticos."""
    log_info(f"{product}: buscando granules entre {start} y {end}...")
    start_query = time.time()

    try:
        results = earthaccess.search_data(
            short_name=product,
            temporal=(start, end),
            bounding_box=bbox,
        )
    except Exception as e:
        log_err(f"{product}: error durante búsqueda -> {e}")
        return 0

    if not results:
        log_warn(f"{product}: no se encontraron archivos.")
        return 0

    log_ok(f"{product}: {len(results)} archivos encontrados en {time.time()-start_query:.1f}s")
    dest.mkdir(parents=True, exist_ok=True)

    downloaded = []
    total = len(results)

    for i, granule in enumerate(results, 1):
        for attempt in range(1, max_retries + 1):
            try:
                files = earthaccess.download(
                    [granule],
                    dest,
                    threads=threads,
                    show_progress=False
                )
                if files:
                    downloaded.extend(files)
                    break
            except Exception as e:
                log_warn(f"{product}: intento {attempt}/{max_retries} falló -> {e}")
                time.sleep(2)

        progress = int((i / total) * 100)
        sys.stdout.write(f"\r   Descargando {product}: [{('=' * (progress // 4)).ljust(25)}] {progress:3d}%")
        sys.stdout.flush()

    sys.stdout.write("\n")
    log_ok(f"{product}: descarga completada ({len(downloaded)} archivos).")
    return len(downloaded)


# =============================================================
# 🛰️ Ejecutor paralelo
# =============================================================

def run_merra2_download(start, end, bbox, dest, workers=2, threads=2):
    """Descarga MERRA-2 SLV (superficie) y AER (aerosoles)."""
    products = ["M2T1NXSLV", "M2T1NXAER"]

    log_info(f"Iniciando descargas MERRA-2 ({len(products)} productos, {workers} hilos)")
    log_info(f"Fechas: {start} → {end}")
    log_info(f"Bounding box: {bbox}")
    log_info(f"Destino: {dest.resolve()}")

    completed = 0
    total = len(products)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(download_merra2_product, p, start, end, bbox, dest / p, threads): p
            for p in products
        }
        for future in as_completed(futures):
            p = futures[future]
            try:
                count = future.result()
                completed += 1
                pct = int((completed / total) * 100)
                log_ok(f"Progreso global: {completed}/{total} ({pct}%)")
            except Exception as e:
                log_err(f"{p}: error en descarga -> {e}")


# =============================================================
# 🧠 MAIN
# =============================================================

def main():
    ensure_login()

    # --- Configuración ---
    start_date, end_date = "2025-08-05", "2025-10-04"
    bbox = (-100.9, 25.3, -99.8, 26.1)  # Monterrey
    base = Path("./data/merra2")

    log_info("===========================================")
    log_info("     🚀 NASA MERRA-2 DOWNLOADER")
    log_info(f"     Región: Monterrey, MX")
    log_info(f"     Fechas: {start_date} → {end_date}")
    log_info("===========================================\n")

    run_merra2_download(
        start=start_date,
        end=end_date,
        bbox=bbox,
        dest=base,
        workers=2,
        threads=2,
    )

    log_ok("\n✅ Descarga MERRA-2 completa. Datos guardados en ./data/merra2/")
    print(f"""
Estructura esperada:
 ├── data/
 │   └── merra2/
 │       ├── M2T1NXSLV/
 │       └── M2T1NXAER/
    """)


if __name__ == "__main__":
    main()

