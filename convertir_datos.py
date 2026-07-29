"""
convertir_datos.py — Utilidad de actualización mensual
──────────────────────────────────────────────────────
Uso:
  python convertir_datos.py ruta/al/nuevo_archivo.xlsb
  python convertir_datos.py ruta/al/nuevo_archivo.xlsx

Convierte el nuevo archivo de datos a .parquet y lo coloca en /data/
listo para subir a GitHub (el dashboard lo detecta automáticamente).
"""

import sys
import pandas as pd
from pathlib import Path

def convertir(origen: str):
    src = Path(origen)
    if not src.exists():
        print(f"❌ Archivo no encontrado: {src}")
        sys.exit(1)

    print(f"📂 Leyendo: {src.name}  ({src.stat().st_size / 1024 / 1024:.1f} MB)")

    ext = src.suffix.lower()
    if ext == ".xlsb":
        df = pd.read_excel(src, engine="pyxlsb")
        # Convertir fecha serial Excel → datetime
        if "FECHA_ACTIVACION" in df.columns:
            df["FECHA"] = pd.to_datetime(df["FECHA_ACTIVACION"] - 25569,
                                         unit="D", errors="coerce")
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(src, engine="openpyxl")
        if "FECHA_ACTIVACION" in df.columns and pd.api.types.is_float_dtype(df["FECHA_ACTIVACION"]):
            df["FECHA"] = pd.to_datetime(df["FECHA_ACTIVACION"] - 25569,
                                         unit="D", errors="coerce")
        elif "FECHA_ACTIVACION" in df.columns:
            df["FECHA"] = pd.to_datetime(df["FECHA_ACTIVACION"], errors="coerce")
    else:
        print(f"❌ Formato no soportado: {ext}  (usa .xlsb, .xlsx)")
        sys.exit(1)

    # Limpiar
    if "SEMANA" in df.columns:
        df["SEMANA"] = df["SEMANA"].fillna(0).astype(int)
    if "UNIDADES" in df.columns:
        df["UNIDADES"] = pd.to_numeric(df["UNIDADES"], errors="coerce").fillna(0).astype(int)

    # Generar nombre de salida con el mismo nombre base
    destino = Path(__file__).parent / "data" / (src.stem.replace(" ", "_") + ".parquet")
    df.to_parquet(destino, index=False)

    orig_mb  = src.stat().st_size / 1024 / 1024
    parq_kb  = destino.stat().st_size / 1024
    print(f"✅ Convertido: {destino.name}")
    print(f"   Original: {orig_mb:.1f} MB  →  Parquet: {parq_kb:.0f} KB  ({parq_kb*100//(orig_mb*1024):.0f}% del tamaño)")
    print(f"   Filas: {len(df):,}")
    print(f"\nPróximo paso: sube el archivo '{destino.name}' a GitHub en la carpeta /data/")
    print("El dashboard detectará el archivo nuevo automáticamente al hacer deploy.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python convertir_datos.py ruta/al/archivo.xlsb")
        sys.exit(1)
    convertir(sys.argv[1])
