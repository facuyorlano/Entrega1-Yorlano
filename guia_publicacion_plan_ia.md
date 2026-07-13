# IA/360 Avanzado — publicación y sincronización

## Estado actual

El sitio está cargado en `facuyorlano/Entrega1-Yorlano` y tiene un workflow de GitHub Actions preparado para publicarlo en GitHub Pages.

## Activar GitHub Pages por primera vez

1. Abrí el repositorio en GitHub.
2. Entrá a **Settings → Pages**.
3. En **Build and deployment → Source**, elegí **GitHub Actions**.
4. Volvé a la pestaña **Actions** y abrí el workflow **Publicar IA360 en GitHub Pages**.
5. Si no se inició automáticamente, elegí **Run workflow → Run workflow**.
6. Al terminar, el sitio quedará disponible en la URL de GitHub Pages del repositorio.

Después de esa activación inicial, cada cambio en la rama `main` se publica automáticamente.

## Sincronización con Supabase

La sincronización usa:

- Supabase Auth para la cuenta del estudiante.
- PostgreSQL para guardar un único documento JSON de progreso por usuario.
- Row Level Security para impedir que una cuenta acceda al progreso de otra.

La configuración recomendada es:

1. Crear un proyecto independiente llamado `ia360-avanzado` en la región de São Paulo (`sa-east-1`).
2. Aplicar `configurar_sincronizacion_supabase.sql`.
3. Obtener la **Project URL** y una **Publishable key** habilitada.
4. Crear `supabase-config.json` en este repositorio con esos dos valores públicos.
5. En Supabase, entrar a **Authentication → URL Configuration** y agregar la URL publicada como **Site URL** y **Redirect URL**.
6. Abrir IA/360, crear la cuenta, confirmar el correo e ingresar.
7. La primera vez, seleccionar **Subir local** para conservar cualquier avance ya registrado en el navegador.

## Seguridad

- La Publishable key puede estar en un frontend público porque no otorga privilegios administrativos y el acceso a las filas está limitado por RLS.
- Nunca debe publicarse una secret key ni `service_role`.
- Conviene conservar exportaciones JSON periódicas como copia independiente.

## Renombrar el repositorio

Podés cambiar `Entrega1-Yorlano` por `ia-360-avanzado` desde **Settings → General → Repository name**. GitHub conserva redirecciones desde la URL anterior; después conviene revisar la URL configurada en Supabase Auth.
