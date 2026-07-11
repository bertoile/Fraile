
import streamlit as str
import pandas as pd
import plotly.express as px
import webbrowser

# Configuración de la página web interactiva
str.set_page_config(page_title="Sistema de Inteligencia Social - CyL", layout="wide", page_icon="📊")

str.title("📊 Sistema de Inteligencia Social e Intervención")
str.markdown("### Herramienta interactiva para el análisis de casos en riesgo de exclusión social")
str.write("Sube tu archivo CSV para activar el panel de control interactivo, realizar consultas automáticas y acceder a recursos oficiales.")

# 1. CARGA DEL ARCHIVO CSV
archivo_subido = str.file_uploader("📂 Arrastra o selecciona tu archivo CSV de casos anónimos", type=["csv"])

if archivo_subido is not None:
    # Leer los datos reales del usuario
    df = pd.read_csv(archivo_subido)
    
    # BARRA LATERAL: Filtros Interactivos
    str.sidebar.header("🎯 Filtros del Panel")
    provincias = ["Todas"] + list(df['Provincia'].unique())
    provincia_sel = str.sidebar.selectbox("Filtrar por Provincia de CyL:", provincias)
    
    # Aplicar filtro de provincia si corresponde
    if provincia_sel != "Todas":
        df_filtrado = df[df['Provincia'] == provincia_sel]
    else:
        df_filtrado = df

    # INDICADORES CLAVE (Métricas automáticas)
    str.markdown("---")
    col1, col2, col3, col4 = str.columns(4)
    with col1:
        str.metric("Total Casos Analizados", len(df_filtrado))
    with col2:
        str.metric("Ingreso Mensual Promedio", f"{round(df_filtrado['Ingresos_Mensuales_EUR'].mean(), 2)} €")
    with col3:
        casos_urgentes = len(df_filtrado[df_filtrado['Requiere_Intervencion_Urgente'] == 'Sí'])
        str.metric("⚠️ Intervenciones Urgentes", casos_urgentes)
    with col4:
        mayores_60 = len(df_filtrado[df_filtrado['Edad'] >= 60])
        str.metric("👴 Personas Mayores (≥60 años)", mayores_60)

    # 2. LOS 6 BOTONES DE PREGUNTAS PRECONFIGURADAS (Pestañas interactivas)
    str.markdown("## 🔍 Consultas Rápidas Preconfiguradas")
    str.write("Haz clic en las pestañas para responder instantáneamente a tus preguntas clave:")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = str.tabs([
        "📋 Resumen Perfil", 
        "🧠 Patrones", 
        "💼 Capacitación Laboral", 
        "🤝 Aislamiento y Grupos", 
        "🏠 Análisis Vivienda", 
        "⏱️ Alta y Seguimiento"
    ])
    
    with tab1:
        str.subheader("Resumen General del Perfil de los Casos")
        col_t1_1, col_t1_2 = str.columns(2)
        with col_t1_1:
            fig_genero = px.pie(df_filtrado, names='Genero', title='Distribución por Género', color_discrete_sequence=px.colors.qualitative.Pastel)
            str.plotly_chart(fig_genero, use_container_width=True)
        with col_t1_2:
            fig_edad = px.histogram(df_filtrado, x='Edad', nbins=15, title='Distribución de Edades', color_discrete_sequence=['#004080'])
            str.plotly_chart(fig_edad, use_container_width=True)
            
    with tab2:
        str.subheader("Patrones de Vulnerabilidad Detectados")
        str.write("Relación entre Situación Principal e Ingresos Mensuales:")
        fig_scatter = px.box(df_filtrado, x='Situacion_Principal', y='Ingresos_Mensuales_EUR', color='Situacion_Principal',
                             title="Dispersión de Ingresos según Problemática", color_discrete_sequence=px.colors.qualitative.Safe)
        str.plotly_chart(fig_scatter, use_container_width=True)
        
    with tab3:
        str.subheader("Personas en Edad Laboral para Talleres de Capacitación")
        # Filtrar personas entre 18 y 55 años en desempleo
        perfiles_laborales = df_filtrado[(df_filtrado['Edad'] >= 18) & (df_filtrado['Edad'] <= 55) & (df_filtrado['Situacion_Principal'] == 'Desempleo de larga duración')]
        str.write(f"Se han detectado **{len(perfiles_laborales)} personas** aptas para incorporarse a itinerarios de empleo y capacitación digital/textil.")
        if len(perfiles_laborales) > 0:
            str.dataframe(perfiles_laborales[['ID_Anonimo', 'Edad', 'Genero', 'Provincia', 'Ingresos_Mensuales_EUR']])
        
    with tab4:
        str.subheader("Aislamiento Social y Propuestas de Intervención")
        str.write("Casos detectados con Dependencia de Aseo o Situaciones de Aislamiento:")
        dependencia_aseo = df_filtrado[df_filtrado['Nivel_Autonomia_Aseo'].isin(['Dependencia Total', 'Dependencia Moderada'])]
        
        str.dataframe(dependencia_aseo[['ID_Anonimo', 'Edad', 'Provincia', 'Nivel_Autonomia_Aseo']])
        
        str.markdown("### 💡 Propuestas de Intervención Grupal Sugeridas:")
        str.info("1. **Taller de Apoyo Domiciliario Múltiple:** Agrupar casos de Dependencia Moderada en zonas cercanas para optimizar auxiliares del SAD.\n"
                 "2. **Cafés Vecinales de Envejecimiento Activo:** Para los perfiles identificados como 'Persona mayor viviendo sola'.")

    with tab5:
        str.subheader("Análisis de la Situación del Entorno y Necesidades")
        fig_sit = px.bar(df_filtrado, x='Situacion_Principal', color='Nivel_Autonomia_Aseo', 
                         title="Problemática Principal Cruzada con Nivel de Autonomía", barmode='group')
        str.plotly_chart(fig_sit, use_container_width=True)
        
    with tab6:
        str.subheader("Tiempo en Seguimiento y Alertas Críticas")
        # Mostrar tabla de los que requieren intervención urgente
        urgentes = df_filtrado[df_filtrado['Requiere_Intervencion_Urgente'] == 'Sí']
        str.error(f"¡Atención! Hay {len(urgentes)} casos que requieren priorización inmediata en la lista de asuntos sociales:")
        str.dataframe(urgentes)

    # 3. BUSCADOR INTERACTIVO DE AYUDAS Y RECURSOS
    str.markdown("---")
    str.markdown("## 🌐 Buscador Integrado de Ayudas (JCYL y Nacional)")
    str.write("Selecciona una problemática para obtener las palabras clave e instrucciones de tramitación oficial:")
    
    opcion_ayuda = str.selectbox("¿Qué recurso necesitas gestionar?", [
        "Personas Mayores de 60 años con falta de autonomía en aseo (Dependencia CyL)",
        "Inserción Laboral y Capacitación",
        "Ingreso Mínimo Vital y Renta de Ciudadanía"
    ])
    
    if "aseo" in opcion_ayuda.lower():
        str.warning("🚨 **Recurso Identificado:** Servicio de Ayuda a Domicilio (SAD) y Prestación Económica de la Ley de Dependencia.")
        str.write("**Pasos para tramitar:** El usuario debe acudir al CEAS (Centro de Acción Social) de su municipio en Castilla y León para solicitar la valoración del Grado de Dependencia.")
        
        # Enlaces de búsqueda simulados/reales
        str.markdown("[🔗 Buscar en Sede Electrónica JCYL (Dependencia)](https://www.tramitas.jcyl.es/)")
        str.markdown("[🔗 Enlace Oficial del IMSERSO (Nacional)](https://imserso.es)")

    elif "laboral" in opcion_ayuda.lower():
        str.info("💼 **Recurso Identificado:** Programas de fomento del empleo del ECYL (Servicio Público de Empleo de Castilla y León).")
        str.markdown("[🔗 Consultar Cursos de Capacitación ECYL](https://empleo.jcyl.es/)")

    else:
        str.success("💰 **Recurso Identificado:** Renta de Ciudadanía de CyL / Ingreso Mínimo Vital (Seguridad Social).")
        str.markdown("[🔗 Simulador del Ingreso Mínimo Vital (Nacional)](https://prestaciones.seg-social.es/)")

else:
    str.info("💡 Por favor, sube un archivo CSV en el panel central para visualizar toda la interactividad del programa.")
