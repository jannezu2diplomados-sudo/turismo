# Proyecto 3 · Explorador de lugares y rutas

Interfaz renovada en Python y Flet 1.0.5. Diseño azul marino/blanco con acentos
verdes, tarjetas y adaptación a escritorio y móvil. No requiere clave API de Maps.

## Qué mejora

- Buscar lugares, direcciones o coordenadas mediante enlaces de Google Maps.
- Generar rutas a pie, en carro, en bicicleta o en transporte público.
- Intercambiar origen y destino.
- Atajos a lugares públicos y botón Limpiar.
- Validar campos vacíos, entradas muy largas y origen/destino idénticos.
- Deshabilitar enlaces antiguos si se cambian los datos o el modo de viaje.
- Generar con Enter en el campo de búsqueda o en el campo Destino.
- Historial visible de los últimos 10 enlaces únicos, con Abrir y Reutilizar.
- Confirmación antes de vaciar el historial; el contador total se conserva.
- No imprimir las direcciones consultadas en la consola.

## Archivos

```text
proyecto3/
├── main.py
├── azure_entry.py
├── requirements.txt
├── .gitignore
├── README.md
└── tests/
    └── test_app.py
```

No necesitas src/: main.py está en la raíz, igual que en la captura de tu proyecto.
Si ya tienes un repositorio, conserva su carpeta .github/workflows/ y su identidad
de despliegue. El ZIP no incluye configuraciones de autenticación de tu cuenta.
No copies el contenido sobre archivos personalizados sin guardar antes una copia.

## 1. Ejecutar localmente en Windows / VS Code

Abre ESTA carpeta en VS Code. Debes ver main.py y requirements.txt al mismo nivel.
Si ya tienes un entorno virtual activado, no necesitas crearlo de nuevo.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn azure_entry:app --host 127.0.0.1 --port 8000
```

Abre http://127.0.0.1:8000. Mantén la terminal abierta mientras pruebas.
Detén el servidor con Ctrl + C. Si el puerto está ocupado, usa --port 8001 y abre
http://127.0.0.1:8001.

Si PowerShell bloquea la activación, abre una terminal CMD y usa:

```cmd
venv\Scripts\activate.bat
```

No cambies la política global de seguridad para activar el entorno.
En Ctrl + Shift + P → Python: Select Interpreter elige venv\Scripts\python.exe.

## 2. ¿Para qué son requirements.txt y .gitignore?

requirements.txt indica qué paquetes instalar; está en la raíz para que Azure
App Service pueda encontrarlos. No es una carpeta ni debe terminar en .txt.txt.

.gitignore excluye venv/, .flet/, cachés y .env del repositorio. No es una
condición de Azure, pero evita subir archivos locales o credenciales por error.
No borra secretos previamente publicados; una credencial expuesta debe rotarse.

## 3. Uso y pruebas manuales

1. Pulsa Generar búsqueda: el botón Abrir lugar en Maps se habilita.
2. Cambia el texto: el enlace anterior se deshabilita; genera uno nuevo.
3. Pulsa Limpiar y Generar búsqueda: debe mostrar validación.
4. Elige un modo de viaje, genera la ruta y abre el enlace con un clic explícito.
5. Intercambia origen/destino: regenera antes de abrir la nueva ruta.
6. Usa Reutilizar en el historial: recupera los campos; genera para confirmar.
7. Abre Vaciar historial y prueba Cancelar; después confirma Vaciar.
8. Prueba el navegador a 390 px y en escritorio: las tarjetas se apilan en móvil.

Los enlaces se abren en una nueva pestaña o según el navegador/dispositivo.
La aplicación no solicita geolocalización ni intenta abrir Google automáticamente.
Si el navegador bloquea una apertura, revisa su aviso de ventanas emergentes.

## 4. Pruebas automatizadas

Desde la raíz, con el entorno activado:

```powershell
python -m unittest discover -s tests -v
```

Incluye 11 pruebas de codificación de URLs, límite de longitud, validación,
intercambio, cambio de modo, historial sin duplicados, recuperación y vaciado.
Se probaron además renderizado e interacciones en Chromium local en escritorio
(1440 px) y móvil (390 px). No se desplegó esta versión en tu cuenta Azure.

## 5. Publicar en Azure App Service Linux

Usa la ruta del laboratorio de App Service, no la de Static Web Apps:

- Python 3.13 (o una versión compatible comprobada).
- requirements.txt en la raíz.
- Variable de aplicación: SCM_DO_BUILD_DURING_DEPLOYMENT=1
- Comando de inicio, en una sola línea:

```text
python -m uvicorn azure_entry:app --host 0.0.0.0 --port 8000 --workers 1
```

azure_entry.py importa `from main import main`. No usa src/.
Conecta GitHub desde el Centro de implementación y utiliza la identidad OIDC
configurada por Azure. Conserva los identificadores del workflow generado.
No pegues claves ni perfiles de publicación en el código.

Para guardar cambios en un repositorio YA configurado, revisa primero git status:

```powershell
git add main.py azure_entry.py requirements.txt .gitignore README.md tests
git commit -m "Mejorar explorador de lugares y rutas"
git push origin main
```

Si es un repositorio nuevo, primero configúralo y conecta su origin como en el
laboratorio. No ejecutes remote add otra vez si origin ya existe.
Espera Actions verde y después verifica la URL HTTPS y las funciones.
No necesitas flet publish ni dist/ para este despliegue dinámico.

En Azure for Students conserva F1 si es el plan autorizado y está disponible.
F1 tiene recursos limitados y no ofrece Always On. No aumentes workers ni
actives un plan de pago automáticamente para intentar mejorar el arranque.

## 6. Límites y privacidad

El programa construye URLs; NO integra un mapa dentro de Flet, no confirma que
un lugar exista, ni consulta distancias, tráfico, costos o tiempos de viaje.
Google Maps decide los resultados y la disponibilidad de cada modo por región.
Usa lugares públicos: al pulsar Abrir se envían los parámetros a Google.

El historial es una lista de diccionarios en memoria POR SESIÓN: se pierde al
iniciar una sesión nueva o reiniciar el servidor. No hay base de datos ni cuentas.
La hora mostrada corresponde al servidor (en Azure podría ser UTC), no a una
zona horaria detectada en el dispositivo. Vaciar borra el historial visible;
los enlaces ya generados en los botones del formulario pueden seguir activos.
El contador representa generaciones válidas, no visitas ni lugares únicos.

Esta interfaz no envía solicitudes de Maps para generar enlaces. El runtime de
Flet/Flutter sigue teniendo un costo de descarga e inicio; el diseño no elimina
el arranque en frío del alojamiento.

## Referencias

- Google Maps URLs: https://developers.google.com/maps/documentation/urls/guide
- Flet dinámico/ASGI: https://flet.dev/docs/publish/web/dynamic-website/
- Python en App Service: https://learn.microsoft.com/en-us/azure/app-service/configure-language-python
