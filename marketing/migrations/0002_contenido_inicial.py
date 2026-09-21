"""Carga el contenido inicial del sitio: funcionalidades y planes.

Todo lo que se crea aca es editable desde el admin. Los planes son
marcadores de posicion con nombres y caracteristicas razonables; los precios
quedan vacios porque el sitio muestra "Cotizar".

Es idempotente (get_or_create por slug / titulo) y la reversion no borra nada,
para no eliminar contenido que se haya editado despues.
"""

from django.db import migrations

FEATURES = [
    # (audiencia, icono, titulo, descripcion)
    (
        "app", "alert", "Alerta de emergencia",
        "Con un toque envias tu alerta a la central de monitoreo y a tus contactos, "
        "con tu ubicacion exacta y los datos de tu perfil.",
    ),
    (
        "app", "radio", "Boton de panico fisico",
        "Un dispositivo que llevas encima y dispara la misma alerta sin necesidad de "
        "desbloquear el telefono ni abrir la app.",
    ),
    (
        "app", "bell", "Recepcion de alertas",
        "Recibi las alertas de tu familia y de tu comunidad en el momento, y segui la "
        "situacion hasta que llega la ayuda.",
    ),
    (
        "app", "users", "Alertas comunitarias",
        "Avisa a tu barrio, condominio o grupo cuando ocurre algo, y enterate al instante "
        "de lo que sucede cerca tuyo.",
    ),
    (
        "app", "map", "Rastreo en tiempo real",
        "Comparti tu recorrido con quien vos elijas y deja que te acompanen en el trayecto "
        "hasta que llegues a destino.",
    ),
    (
        "app", "truck", "Telemetria vehicular",
        "Posicion en vivo, recorridos e historial de tu vehiculo, con alertas por velocidad "
        "y salidas de zona.",
    ),
    (
        "panel", "headset", "Monitoreo en tiempo real",
        "Todas las emergencias de tus abonados en un mapa en vivo, con su estado, su "
        "prioridad y el tiempo transcurrido.",
    ),
    (
        "panel", "alert", "Gestion de emergencias",
        "Atende, escala y cerra cada incidente con su historial completo de acciones y "
        "responsables.",
    ),
    (
        "panel", "pin", "Delegacion de unidades",
        "Asigna la unidad mas cercana al incidente y segui su desplazamiento hasta el lugar "
        "en tiempo real.",
    ),
    (
        "panel", "activity", "Telemetria de flota",
        "Estado, ubicacion y recorridos de todos tus moviles, con alertas automaticas por "
        "comportamiento anomalo.",
    ),
    (
        "panel", "report", "Reportes e historicos",
        "Reportes de emergencias por periodo, zona, operador y tiempo de respuesta, listos "
        "para exportar.",
    ),
    (
        "panel", "building", "Abonados y zonas",
        "Administra tus clientes, sus contactos, sus dispositivos y las zonas de cobertura "
        "que atiende cada delegacion.",
    ),
]

PLANS = [
    {
        "slug": "personas-personal",
        "audience": "personas",
        "name": "Personal",
        "tagline": "Para una persona",
        "description": "Proteccion individual con la app y monitoreo de la central.",
        "order": 1,
        "features": [
            "App movil para 1 usuario",
            "Alertas de emergencia ilimitadas",
            "Hasta 3 contactos de emergencia",
            "Ubicacion en tiempo real",
            "Atencion de la central 24/7",
        ],
    },
    {
        "slug": "personas-familiar",
        "audience": "personas",
        "name": "Familiar",
        "tagline": "Para toda la familia",
        "description": "Cubri a todo el grupo familiar y segui a cada integrante desde la app.",
        "badge": "Mas elegido",
        "is_featured": True,
        "order": 2,
        "features": [
            "App movil para hasta 5 usuarios",
            "Alertas de emergencia ilimitadas",
            "Contactos de emergencia ilimitados",
            "Seguimiento de trayectos en familia",
            "1 boton de panico fisico incluido",
            "Atencion de la central 24/7",
        ],
    },
    {
        "slug": "personas-comunidad",
        "audience": "personas",
        "name": "Comunidad",
        "tagline": "Para barrios y condominios",
        "description": "Alertas comunitarias para vecinos organizados, con panel de grupo.",
        "order": 3,
        "features": [
            "Usuarios segun el tamano del barrio",
            "Alertas comunitarias por zona",
            "Grupo de vecinos con administrador",
            "Botones de panico fisicos opcionales",
            "Reporte mensual de incidentes",
        ],
    },
    {
        "slug": "empresas-entidad-basica",
        "audience": "empresas",
        "name": "Entidad Basica",
        "tagline": "Para empresas que arrancan",
        "description": "El panel operativo con lo necesario para recibir y atender emergencias.",
        "order": 1,
        "features": [
            "Panel administrativo web",
            "Monitoreo de emergencias en tiempo real",
            "Hasta 3 operadores simultaneos",
            "Gestion de abonados",
            "Reportes basicos de incidentes",
            ("Telemetria de flota", False),
        ],
    },
    {
        "slug": "empresas-entidad-profesional",
        "audience": "empresas",
        "name": "Entidad Profesional",
        "tagline": "Para empresas en operacion",
        "description": "Operacion completa: delegacion de unidades, zonas y reportes avanzados.",
        "badge": "Recomendado",
        "is_featured": True,
        "order": 2,
        "features": [
            "Todo lo del plan Basico",
            "Operadores ilimitados",
            "Delegacion de unidades y seguimiento",
            "Zonas de cobertura y delegaciones",
            "Telemetria de flota incluida",
            "Reportes avanzados y exportacion",
        ],
    },
    {
        "slug": "empresas-corporativo",
        "audience": "empresas",
        "name": "Corporativo y Flotas",
        "tagline": "Para operaciones grandes",
        "description": "Multi-delegacion, integraciones a medida y acompanamiento dedicado.",
        "order": 3,
        "features": [
            "Todo lo del plan Profesional",
            "Multiples delegaciones y sedes",
            "Telemetria vehicular para toda la flota",
            "Integraciones y reportes a medida",
            "Ejecutivo de cuenta dedicado",
            "Acuerdo de nivel de servicio (SLA)",
        ],
    },
]


def cargar_contenido(apps, schema_editor):
    Feature = apps.get_model("marketing", "Feature")
    Plan = apps.get_model("marketing", "Plan")
    PlanFeature = apps.get_model("marketing", "PlanFeature")

    for order, (audience, icon, title, description) in enumerate(FEATURES, start=1):
        Feature.objects.get_or_create(
            audience=audience,
            title=title,
            defaults={
                "icon": icon,
                "description": description,
                "order": order,
                "is_active": True,
            },
        )

    for entry in PLANS:
        features = entry.pop("features")
        slug = entry.pop("slug")
        plan, created = Plan.objects.get_or_create(slug=slug, defaults=entry)
        if not created:
            continue
        for order, feature in enumerate(features, start=1):
            text, is_included = feature if isinstance(feature, tuple) else (feature, True)
            PlanFeature.objects.create(
                plan=plan, text=text, is_included=is_included, order=order
            )


class Migration(migrations.Migration):

    dependencies = [
        ("marketing", "0001_initial"),
    ]

    operations = [
        # La reversion es un no-op a proposito: revertir no debe borrar
        # contenido que se haya editado desde el admin.
        migrations.RunPython(cargar_contenido, migrations.RunPython.noop),
    ]
