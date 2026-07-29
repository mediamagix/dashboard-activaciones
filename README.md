# Dashboard de Activaciones — TELCEL

Dashboard interactivo de activaciones de equipos, construido con **Streamlit + Plotly**.

## Estructura
```
streamlit-deploy/
├── app.py                  ← Dashboard principal
├── requirements.txt        ← Dependencias Python
├── convertir_datos.py      ← Utilidad de actualización mensual
├── .streamlit/
│   └── config.toml         ← Tema y configuración
└── data/
    └── *.parquet           ← Base de datos (formato Parquet)
```

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Actualizar datos mensualmente
```bash
python convertir_datos.py "/ruta/al/nuevo_archivo_agosto.xlsb"
# Luego haz commit + push del nuevo .parquet a GitHub
```
