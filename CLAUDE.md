# Proyecto Django

## Stack
- Django
- Django REST Framework
- PostgreSQL
- Python
- Frontend: [indicar si existe]
- Autenticación: [indicar]

## Objetivo
Actualizar y ampliar el sistema existente sin romper funcionalidades actuales.

## Reglas
- No modificar funcionalidades existentes sin autorización.
- Antes de crear modelos, revisar modelos existentes.
- Reutilizar modelos, serializers y servicios existentes cuando sea posible.
- No crear archivos duplicados si ya existe una implementación equivalente.
- No hacer cambios masivos sin explicarlos primero.
- Ejecutar migraciones solamente después de revisar los modelos.
- Ejecutar tests después de cambios importantes.
- Mantener compatibilidad con las APIs existentes.
- No eliminar datos ni modelos existentes sin confirmación.

## Base de datos
SQLite3

## Forma de trabajo
1. Analizar antes de modificar.
2. Proponer arquitectura.
3. Implementar por módulos.
4. Ejecutar tests.
5. Revisar migraciones.
6. Continuar con el siguiente módulo.