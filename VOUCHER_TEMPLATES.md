# 🎫 Guía de Plantillas de Vouchers

## Plantillas Disponibles

### 1. **voucher_template.html** (Actual - Completa)
Plantilla principal sin logo, con diseño completo y profesional.

**Características:**
- ✅ Sin logo (aprovecha todo el espacio)
- ✅ Código/Usuario destacado en el centro
- ✅ Información de tiempo y expiración
- ✅ Instrucciones de conexión
- ✅ Precio en el reverso (efecto hover)
- ✅ Diseño responsive para impresión

**Tamaño:** 8.5cm x 5.4cm (tarjeta de presentación)

---

### 2. **voucher_template_simple.html** (Alternativa - Minimalista)
Plantilla ultra simple con código más grande.

**Características:**
- ✅ Diseño minimalista
- ✅ Código PIN en tamaño extra grande (más legible)
- ✅ Información esencial solamente
- ✅ Precio en reverso con gradiente
- ✅ Ideal para impresión rápida

---

## 🎨 Características del Diseño

### Frente del Voucher
```
┌─────────────────────────┐
│   VOUCHER DE ACCESO     │
│      Internet WiFi      │
│                         │
│   ┌───────────────┐     │
│   │  CÓDIGO PIN   │     │
│   │   ABC123      │     │
│   └───────────────┘     │
│                         │
│ Tiempo: 1h  Exp: Auto  │
│ Conectar a: hotspot.lo  │
└─────────────────────────┘
```

### Reverso del Voucher (Hover)
```
┌─────────────────────────┐
│                         │
│       PRECIO            │
│                         │
│        $2.50            │
│                         │
│   Voucher de Internet   │
│                         │
└─────────────────────────┘
```

---

## 🖨️ Comportamiento de Impresión

### Vista Normal (Pantalla)
- Muestra el **frente** del voucher
- Al pasar el mouse: muestra el **reverso** (precio)

### Vista de Impresión
- Imprime **solo el frente** por defecto
- El precio NO se imprime (está en el reverso)

### Para Imprimir Ambos Lados
Si quieres imprimir frente y reverso, edita la plantilla y descomenta:

```css
/* En la sección @media print */
.voucher-back {
    display: flex !important;
    page-break-before: always;
}
```

---

## ✏️ Personalización

### Cambiar Colores

**Código PIN (azul):**
```html
text-blue-600  →  text-green-600  (verde)
bg-blue-50     →  bg-green-50
border-blue-200 → border-green-200
```

**Reverso (gradiente púrpura):**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Cambiar a verde: */
background: linear-gradient(135deg, #10b981 0%, #059669 100%);

/* Cambiar a rojo: */
background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
```

### Cambiar Tamaño del Voucher

```html
<!-- Actual: 8.5cm x 5.4cm (tarjeta de presentación) -->
style="width: 8.5cm; height: 5.4cm;"

<!-- Más grande: -->
style="width: 10cm; height: 6cm;"

<!-- Más pequeño: -->
style="width: 7cm; height: 4.5cm;"
```

### Cambiar Tamaño del Código

```html
<!-- PIN actual: -->
text-4xl  (muy grande)

<!-- Más grande: -->
text-5xl o text-6xl

<!-- Más pequeño: -->
text-3xl o text-2xl
```

---

## 🔄 Cambiar de Plantilla

### Opción 1: Reemplazar el Archivo
1. Renombra `voucher_template.html` a `voucher_template_backup.html`
2. Renombra `voucher_template_simple.html` a `voucher_template.html`
3. Recarga la aplicación

### Opción 2: Editar en el Editor Web
1. Ve a **Editor de Plantillas** en la aplicación
2. Copia el contenido de `voucher_template_simple.html`
3. Pégalo en el editor
4. Guarda los cambios

---

## 📐 Elementos Eliminados vs Versión Anterior

### ❌ Eliminado:
- Logo (ocupaba mucho espacio)
- Bordes decorativos excesivos
- Información redundante

### ✅ Mejorado:
- Código más grande y legible
- Mejor uso del espacio
- Diseño más limpio
- Precio separado en reverso
- Información esencial destacada

---

## 💡 Consejos de Impresión

### Para Mejor Calidad:
1. **Papel:** Usa papel de 180-250 gramos
2. **Impresora:** Láser o inyección de tinta de calidad
3. **Configuración:** 
   - Calidad: Alta
   - Escala: 100%
   - Márgenes: Mínimos

### Para Cortar:
- Usa una guillotina para cortes precisos
- O imprime en papel perforado para tarjetas
- Tamaño estándar: 8.5cm x 5.4cm

---

## 🎯 Casos de Uso

### Plantilla Completa (voucher_template.html)
- Negocios que necesitan información detallada
- Vouchers con múltiples opciones de tiempo
- Cuando necesitas instrucciones claras

### Plantilla Simple (voucher_template_simple.html)
- Impresión rápida y masiva
- Códigos PIN simples
- Diseño minimalista preferido
- Cuando el código debe ser MUY visible

---

## 🔧 Solución de Problemas

### El precio no se muestra
- El precio está en el **reverso**
- Pasa el mouse sobre el voucher para verlo
- En impresión, está oculto por defecto

### El código se ve muy pequeño
- Cambia `text-4xl` a `text-5xl` o `text-6xl`
- O usa la plantilla simple que tiene código más grande

### Los vouchers no caben en la página
- Ajusta los márgenes en la configuración de impresión
- Reduce el tamaño del voucher en el CSS
- Imprime en orientación horizontal

---

## 📝 Notas

- Las plantillas usan **Tailwind CSS** (ya incluido en la aplicación)
- Son totalmente editables desde el editor web
- Los cambios se aplican inmediatamente
- Puedes crear múltiples versiones y cambiar entre ellas

---

**¿Necesitas más personalización? Edita directamente en el Editor de Plantillas de la aplicación.**
