# Clinicapharma - Investigacion POS + inventario farmacia

Ultima revision: 2026-06-23

Este documento resume comparacion web rapida para validar que el flujo de Farmacia POS + Inventario cubre lo minimo necesario para entrega local.

## Fuentes revisadas

- Square POS Inventory: inventario en tiempo real, alertas de bajo stock, reportes/exportacion y barcode en Retail POS. https://squareup.com/us/en/point-of-sale/features/inventory-management
- Square Support Retail POS: busqueda por nombre/SKU o scanner y stock por ubicacion. https://squareup.com/help/us/en/article/6110-manage-inventory-with-the-retail-pos-app
- Shopify POS Inventory: tracking/ajuste de inventario en admin o POS para evitar vender mas stock del disponible e identificar necesidades de compra. https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management
- Shopify POS Transfers: recepcion de traslados con scanner para mantener stock actualizado. https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/receiving-transfers
- Odoo Inventory Expiration Dates: lotes/seriales con fecha de expiracion y agrupacion por vencimiento. https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/product_management/product_tracking/expiration_dates.html
- GPOS Pharmacy POS: batch/lote, vencimiento, notificaciones de expiracion y evitar vender productos vencidos. https://gposs.com/pharmacy-pos-software/

## Comparacion contra Clinicapharma

| Capacidad minima | Estado |
| --- | --- |
| Stock en tiempo real al vender | Cubierto: venta descuenta tienda. |
| Producto/SKU/barcode | Cubierto: producto y lote tienen codigos. |
| Ubicaciones | Cubierto: bodega, tienda y estante. |
| Lotes y vencimientos | Cubierto: `inventory_lots` guarda lote y vencimiento. |
| FEFO/FIFO | Cubierto: POS descuenta primero el vencimiento mas cercano y luego entrada mas antigua. |
| Bloqueo de vencidos en POS | Cubierto desde 2026-06-23: venta y scanner de lote solo usan lotes vigentes. |
| Alertas | Cubierto inicial: dashboard stock bajo, vencimientos y lotes estancados. |
| Trazabilidad | Cubierto: movimientos y asignacion de lotes por venta. |
| Caja | Cubierto inicial: apertura/cierre por modulo/cajero. |

## Mejora aplicada

El POS de farmacia ahora considera vendible solo un lote con `expires_at` nulo o con fecha mayor/igual a hoy. Si el lote esta vencido:

- No se usa para precio por lote.
- No se descuenta en venta automatica FEFO/FIFO.
- Si el cajero escanea especificamente ese lote, la venta se rechaza con mensaje operativo.
- La lista de traslado bodega-tienda no recomienda lotes vencidos.

## Proximos minimos recomendados

1. Vista de reporte por vencimiento con filtros 30/60/90 dias.
2. Accion formal para marcar lote vencido como merma o retiro.
3. Conteo fisico/ciclico por scanner y ajuste auditado.
4. Punto de reorden sugerido por producto usando stock minimo y ventas recientes.
5. Impresion/etiqueta de lote con barcode si el cliente maneja scanner.
