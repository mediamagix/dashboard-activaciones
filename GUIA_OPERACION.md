# Guía de Operación — Dashboard de Activaciones

---

## Índice
1. [Requisitos previos](#1-requisitos-previos)
2. [Alta en Streamlit Cloud](#2-alta-en-streamlit-cloud)
3. [Deploy del dashboard](#3-deploy-del-dashboard)
4. [Cambiar URL de la app](#4-cambiar-url-de-la-app)
5. [Actualización mensual de datos](#5-actualización-mensual-de-datos)
6. [Cambiar la contraseña de acceso](#6-cambiar-la-contraseña-de-acceso)
7. [Estructura del proyecto](#7-estructura-del-proyecto)
8. [Solución de problemas](#8-solución-de-problemas)

---

## 1. Requisitos previos

### En tu Mac
- **Python 3.x** instalado (`/usr/local/bin/python3`)
- **git** instalado (viene con Xcode Command Line Tools)
- Librerías Python instaladas:
  ```bash
  /usr/local/bin/pip3 install --break-system-packages streamlit pandas plotly pyarrow openpyxl pyxlsb
  ```

### Cuentas necesarias
- **GitHub** — [github.com](https://github.com) (gratuita)
- **Streamlit Cloud** — [share.streamlit.io](https://share.streamlit.io) (gratuita, login con GitHub)

---

## 2. Alta en Streamlit Cloud

> Si ya tienes cuenta, salta al paso 3.

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Click en **"Sign in with GitHub"**
3. Autoriza el acceso con tu cuenta de GitHub
4. Listo — ya tienes workspace activo

---

## 3. Deploy del dashboard

### 3.1 Preparar el repositorio en GitHub

```bash
# En terminal, desde la carpeta del proyecto
cd "/Volumes/MM2T/Proyectos/@MM/Tercero/streamlit-deploy"

git init
git add .
git commit -m "Dashboard inicial"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
git push -u origin main
```

> Para el `git push` necesitas un **Personal Access Token** de GitHub:
> 1. Ve a [github.com/settings/tokens/new](https://github.com/settings/tokens/new)
> 2. Nombre: cualquiera, scope: ✅ `repo`, Expiration: 90 days
> 3. Genera el token y úsalo como contraseña en el push

### 3.2 Publicar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Click en **"Create app"** (arriba a la derecha)
3. Selecciona **"Deploy a public app from GitHub"** → **"Deploy now"**
4. Click en **"Paste GitHub URL"** y pega:
   ```
   https://github.com/TU_USUARIO/NOMBRE_REPO/blob/main/app.py
   ```
5. En **"App URL"** escribe el nombre corto deseado (ej. `dashboard-activaciones-mm`)
6. Click en **"Deploy"**
7. Espera ~2 minutos mientras instala dependencias

La app quedará disponible en:
`https://dashboard-activaciones-mm.streamlit.app`

---

## 4. Cambiar URL de la app

1. Ve a [share.streamlit.io](https://share.streamlit.io) → **"My apps"**
2. Click en los **tres puntos `⋮`** de tu app → **"Settings"**
3. Campo **"Custom subdomain"** → escribe el nombre deseado
4. Click **"Save"**

---

## 5. Actualización mensual de datos

Cuando llegue el nuevo archivo de datos (`.xlsb` o `.xlsx`):

### Paso 1 — Convertir el archivo a Parquet

```bash
cd "/Volumes/MM2T/Proyectos/@MM/Tercero/streamlit-deploy"
/usr/local/bin/python3 convertir_datos.py "/ruta/completa/al/nuevo_archivo.xlsb"
```

El script genera automáticamente un archivo `.parquet` en la carpeta `data/`.

**Ejemplo:**
```bash
/usr/local/bin/python3 convertir_datos.py "/Volumes/MM2T/Proyectos/@MM/Tercero/mat/bases de datos/01 al 31 Agosto 2026.xlsb"
```

### Paso 2 — Subir a GitHub

```bash
git add data/
git commit -m "Datos Agosto 2026"
git push
```

Streamlit Cloud detecta el cambio y redespliega automáticamente en ~1 minuto.

> **Nota:** El dashboard siempre usa el archivo `.parquet` más reciente en la carpeta `data/`. Puedes tener varios archivos históricos — solo se carga el último modificado.

---

## 6. Cambiar la contraseña de acceso

### Paso 1 — Generar el hash de la nueva contraseña

```bash
/usr/local/bin/python3 -c "import hashlib; print(hashlib.sha256('TU_NUEVA_CONTRASEÑA'.encode()).hexdigest())"
```

Copia el resultado (es una cadena de 64 caracteres hexadecimales).

### Paso 2 — Actualizar el archivo app.py

Abre `streamlit-deploy/app.py` y localiza esta línea (aproximadamente línea 17):

```python
APP_PASSWORD_HASH = "641509a..."
```

Reemplaza el valor entre comillas con el hash generado en el paso anterior.

### Paso 3 — Subir el cambio

```bash
git add app.py
git commit -m "Actualizar contraseña"
git push
```

---

## 7. Estructura del proyecto

```
streamlit-deploy/
├── app.py                  ← Dashboard principal (no modificar salvo contraseña)
├── requirements.txt        ← Dependencias Python (no modificar)
├── convertir_datos.py      ← Script de actualización mensual
├── GUIA_OPERACION.md       ← Este archivo
├── .streamlit/
│   └── config.toml         ← Tema y configuración visual
└── data/
    └── julio_2026.parquet  ← Base de datos activa (reemplazar mensualmente)
```

---

## 8. Solución de problemas

### La app muestra "Your app is in the oven" por mucho tiempo
- Click en **"Manage app"** (abajo a la derecha) para ver el log
- Si hay un error en rojo, copiar el mensaje y consultar

### Error `ModuleNotFoundError` al arrancar
Alguna librería no está en `requirements.txt`. Agregar la librería faltante al archivo y hacer push:
```bash
git add requirements.txt
git commit -m "fix: agregar dependencia"
git push
```

### La contraseña no funciona
Verificar que el hash en `app.py` corresponde exactamente a la contraseña generada. El hash distingue mayúsculas de minúsculas.

### Los datos no se actualizan tras el push
1. Verificar que el nuevo `.parquet` está en la carpeta `data/`
2. En Streamlit Cloud → **Manage app** → **"Reboot app"** para forzar recarga

### Recuperar la URL actual de la app
- [share.streamlit.io](https://share.streamlit.io) → **"My apps"** → click en el nombre de la app

---

*Última actualización: Julio 2026*
