"""Iconos SVG inline.

Se guarda solo el contenido interno del <svg>; el contenedor lo pone la
plantilla. Todos estan dibujados sobre un viewBox 0 0 24 24 y usan trazo
(`stroke="currentColor"`, `fill="none"`), asi heredan el color del texto.
"""

ICONS = {
    "shield": '<path d="M12 3l7 3v5c0 4.42-2.99 8.54-7 9.75C7.99 19.54 5 15.42 5 11V6l7-3z"/>',
    "alert": '<path d="M12 3l7 3v5c0 4.42-2.99 8.54-7 9.75C7.99 19.54 5 15.42 5 11V6l7-3z"/>'
             '<path d="M12 8v4"/><path d="M12 15h.01"/>',
    "bell": '<path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>'
            '<path d="M13.73 21a2 2 0 01-3.46 0"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 1118 0z"/>'
           '<circle cx="12" cy="10" r="3"/>',
    "users": '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>'
             '<path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>',
    "truck": '<path d="M1 3h15v13H1z"/><path d="M16 8h4l3 3v5h-7V8z"/>'
             '<circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "chart": '<path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>',
    "phone": '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "report": '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>'
              '<path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/>',
    "map": '<path d="M3 11l19-9-9 19-2-8-8-2z"/>',
    "building": '<path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/>'
                '<path d="M9 9h.01"/><path d="M9 13h.01"/><path d="M9 17h.01"/>',
    "radio": '<circle cx="12" cy="12" r="2"/>'
             '<path d="M16.24 7.76a6 6 0 010 8.49"/><path d="M7.76 16.24a6 6 0 010-8.49"/>'
             '<path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M4.93 19.07a10 10 0 010-14.14"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/>'
            '<path d="M7 11V7a5 5 0 0110 0v4"/>',
    "headset": '<path d="M3 18v-6a9 9 0 0118 0v6"/>'
               '<path d="M21 19a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3a2 2 0 012-2h3z"/>'
               '<path d="M3 19a2 2 0 002 2h1a2 2 0 002-2v-3a2 2 0 00-2-2H3z"/>',
}

ICON_CHOICES = [
    ("shield", "Escudo"),
    ("alert", "Escudo con alerta"),
    ("bell", "Campana / alerta"),
    ("pin", "Ubicacion"),
    ("users", "Comunidad"),
    ("truck", "Vehiculo / flota"),
    ("activity", "Telemetria"),
    ("chart", "Estadisticas"),
    ("phone", "Aplicacion movil"),
    ("clock", "Tiempo real / 24-7"),
    ("report", "Reportes"),
    ("map", "Rastreo / mapa"),
    ("building", "Entidad / empresa"),
    ("radio", "Boton fisico / transmision"),
    ("check", "Verificado"),
    ("lock", "Seguridad / privacidad"),
    ("headset", "Central de monitoreo"),
]
