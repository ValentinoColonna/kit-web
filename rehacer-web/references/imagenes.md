# Imágenes · de dónde salen, cómo se nombran, cómo se integran

La página siempre lleva marcos para fotos (hero, foto grande, banda de galería y catálogo). Las fotos pueden venir de tres lugares, en este orden de preferencia:

1. **Del dueño** (celular, Instagram, lo que tenga). Son las únicas que muestran su negocio de verdad.
2. **Con licencia libre para uso comercial**, etiquetadas como ilustrativas hasta que el dueño las reemplace: Pexels (licencia Pexels: uso gratis, comercial, sin atribución obligatoria) o Unsplash (licencia Unsplash). Anotá en `assets/CREDITOS.md` de dónde salió cada una. Nunca Google Imágenes, nunca fotos de otro negocio.
3. **Ninguna:** el marco muestra un panel del sistema con el nombre del archivo que falta. La página sigue viéndose diseñada.

## Nombres fijos (swap-ready)
El código apunta a estos archivos en `assets/`; reemplazar una foto es copiar otra con el mismo nombre.

| Archivo | Dónde va | Tamaño recomendado |
|---|---|---|
| `hero-salon.jpg` | Fondo del hero, enmascarado | 1920×1080, horizontal |
| `salon.jpg` | Foto grande que se revela | 1600×1200 (4:3) |
| `galeria-01.jpg` … `galeria-05.jpg` | Banda de galería (alternan vertical 3:4 y horizontal 4:3) | 1200 px el lado mayor |
| `catalogo-01.jpg` … `catalogo-NN.jpg` | Tarjetas del catálogo / carta / servicios | 1200×900 (4:3) |

## Catálogo, carta o servicios con foto (por rubro)
Mismo componente, distinto contenido: concesionaria → vehículos (marca, modelo, año, «consultar»); restaurante → platos (nombre, descripción corta, precio real); clínica → especialidades o profesionales; estética → servicios con precio; tienda → productos. Cada tarjeta: foto con velo de la paleta, título, una línea, y el CTA de WhatsApp con mensaje prearmado que nombra el ítem. Sin precios inventados: si el brief no tiene precio, «Consultar».

## Preparar las fotos en la Mac (sin instalar nada)
```
sips -Z 1600 -s formatOptions 80 foto-original.jpg --out assets/galeria-01.jpg   # achica al lado mayor 1600 px y comprime
```
Objetivo: cada foto por debajo de 300 KB. Sin metadatos de ubicación: `sips` los quita al reescribir.

## Reglas
- Toda foto con `alt` descriptivo (las decorativas, `alt=""`).
- Las fotos ilustrativas se marcan en el pie («foto ilustrativa») hasta que estén las reales.
- Nada de fotos con caras de clientes sin permiso.

## Antes de usar una foto de banco, mirala en grande
Una miniatura engaña. Abrí cada foto al tamaño final y descartá las que tengan: carteles o logos de otro negocio o marca (Hertz, otra concesionaria, un banco), patentes extranjeras, uniformes o vehículos oficiales, caras reconocibles, y escenas que no pasan en el rubro (un eléctrico cargando en una agencia de usados). Si el modelo que te ayuda revisa las fotos, pedile que las describa una por una: en la demo detectó cinco malas que la hoja de contactos había dejado pasar.
