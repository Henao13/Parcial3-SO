#!/usr/bin/env python
#Santiago Henao Ramírez

marcos_libres = [0x0, 0x1, 0x2]
reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
segmentos = [
    ('.text',  0x00, 0x1A),
    ('.data',  0x40, 0x28),
    ('.heap',  0x80, 0x1F),
    ('.stack', 0xC0, 0x22),
]

# Cada página cubre 16 direcciones
PAGE_SIZE = 16

def procesar(segmentos, reqs, marcos_libres):
    """
    Simula el manejo de páginas con reemplazo LRU.

    Args:
        segmentos: lista de tripletas (nombre, base, limite).
        reqs: lista de direcciones virtuales (enteros).
        marcos_libres: lista de IDs de marcos disponibles.

    Returns:
        Lista de tuplas (req, dir_fisica, accion).
    """
    resultados = []
    # Copia defensiva de los marcos libres
    free = list(marcos_libres)
    # Páginas cargadas: key = (nombre_segmento, nro_página) -> marco_asignado
    loaded = {}
    # LRU: lista de keys en orden de uso (0 = menos reciente, -1 = más reciente)
    lru_order = []

    for req in reqs:
        # 1) Determinar segmento
        seg = next((s for s in segmentos if s[1] <= req < s[1] + s[2]), None)
        if seg is None:
            resultados.append((req, 0x1ff, "Segmention Fault"))
            break

        nombre, base, limite = seg
        offset      = req - base
        page_num    = offset // PAGE_SIZE
        page_offset = offset % PAGE_SIZE
        key = (nombre, page_num)

        # 2) Hit de página
        if key in loaded:
            marco = loaded[key]
            # actualizar LRU
            lru_order.remove(key)
            lru_order.append(key)
            dir_fisica = marco * PAGE_SIZE + page_offset
            resultados.append((req, dir_fisica, "Marco ya estaba asignado"))
        else:
            # 3) Miss de página
            if free:
                # asigna primero el marco más alto libre
                marco = free.pop()
                accion = "Marco libre asignado"
            else:
                # evict LRU
                evict_key = lru_order.pop(0)
                marco     = loaded.pop(evict_key)
                accion    = "Marco asignado"

            # cargar la nueva página
            loaded[key]    = marco
            lru_order.append(key)
            dir_fisica     = marco * PAGE_SIZE + page_offset
            resultados.append((req, dir_fisica, accion))

    return resultados

def print_results(results):
    for req, dir_fis, accion in results:
        print(f"Req: {req:#04x} Direccion Fisica: {dir_fis:#04x} Acción: {accion}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

