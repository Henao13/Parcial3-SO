#!/usr/bin/env python
# Santiago Henao Ramírez

marcos_libres = [0x0, 0x1, 0x2]
reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
segmentos = [
    ('.text',  0x00, 0x1A),
    ('.data',  0x40, 0x28),
    ('.heap',  0x80, 0x1F),
    ('.stack', 0xC0, 0x22),
]

# Cada página cubre 16 palabras de 2 bytes cada una
WORD_SIZE       = 2     # bytes por palabra
WORDS_PER_PAGE  = 16    # palabras por página
PAGE_SIZE       = WORD_SIZE * WORDS_PER_PAGE  # = 32 bytes por página

def procesar(segmentos, reqs, marcos_libres):
    PAGE_SIZE = 16
    results = []
    page_table = {}     # (segmento, página) -> marco
    last_used = {}      # (segmento, página) -> timestamp
    time = 0

    for req in reqs:
        time += 1
        # 1. Determinar segmento
        seg = None
        for name, base, limit in segmentos:
            if base <= req < base + limit:
                seg = (name, base)
                break
        if seg is None:
            results.append((req, 0x1ff, "Segmentation Fault"))
            break

        name, base = seg
        offset = req - base
        page = offset // PAGE_SIZE
        offset_in_page = offset % PAGE_SIZE
        key = (name, page)

        # 2. Página ya cargada?
        if key in page_table:
            frame = page_table[key]
            results.append((req,
                            frame * PAGE_SIZE + offset_in_page,
                            "Marco ya estaba asignado"))
            last_used[key] = time
            continue

        # 3. Página nueva: ¿hay marcos libres?
        if marcos_libres:
            frame = marcos_libres.pop()        
            action = "Marco libre asignado"
        else:
            # Evicción LRU
            victim = min(last_used, key=lambda k: last_used[k])
            frame = page_table.pop(victim)
            last_used.pop(victim)
            action = "Marco asignado"

        # 4. Asignar la página
        page_table[key] = frame
        last_used[key] = time
        phys = frame * PAGE_SIZE + offset_in_page
        results.append((req, phys, action))

    return results

def print_results(results):
    for req, dir_fis, accion in results:
        print(f"Req: {req:#04x} Direccion Fisica: {dir_fis:#04x} Acción: {accion}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

