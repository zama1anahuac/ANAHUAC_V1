# Atlas de Investigación | Yucatán — prototipo local V1

**NO PUBLICAR EN GITHUB POR AHORA.** La fase 01 está pendiente de dictamen docente y de permisos de difusión; la presente exportación es exclusivamente una vista técnica local de información heredada.

## Ejecución local

`python3 -m http.server 8000`

Abrir `http://localhost:8000/`. No abrir directamente `index.html` con `file://`, pues el navegador bloqueará las solicitudes JSON.

## Estructura

- `index.html`, `style.css`, `app.js`: exploradores A y B y ficha modal.
- `data/*.json`: snapshot local exportable, no autorizado para publicación.
- `data/investigaciones.csv`: CSV de revisión (no publicar todavía).
- `downloads/fichas/`: vacío de forma deliberada; no existen PDFs publicables.
- `scripts/build_from_master.py`: regeneración exclusivamente desde el Excel maestro ubicado fuera del repositorio.

## Seguridad

La presencia de contenido en ZIP no autoriza su difusión. No hay autenticación, libro, diapositivas, notas del profesor, ni archivos Excel internos dentro del sitio. GitHub Pages es público. No agregue claves secretas al JavaScript.

## Criterios de aceptación pendientes

Revisión de correspondencias y causalidad, autorización de datos, auditoría de derechos, despliegue independiente, pruebas desde la URL efectiva, comprobación de MIME y QR.
