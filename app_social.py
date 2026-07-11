import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página web interactiva utilizando el alias correcto 'st'
st.set_page_config(page_title="Sistema de Inteligencia Social - CyL", layout="wide", page_icon="📊")

st.title("📊 Sistema de Inteligencia Social e Intervención")
st.markdown("### Herramienta interactiva para el análisis de casos en riesgo de exclusión social")
st.write("Sube tu archivo CSV para activar el panel de control interactivo, realizar consultas automáticas y acceder a recursos oficiales.")

# 1. CARGA DEL ARCHIVO CSV
archivo_subido = st.file_uploader("📂 Arrastra o selecciona tu archivo CSV de casos anónimos", type=["csv"])

if archivo_subido is not None:
    try:
        # DETECTAR EL SEPARADOR AUTOMÁTICAMENTE (por si es coma o punto y coma de Excel)
        primera_linea = archivo_subido.readline().decode("utf-8")
        archivo_subido.seek(0) # Volvemos al principio del archivo
        
        if ";" in primera_linea:
            df = pd.read_csv(archivo_subido, sep=";")
        else:
            df = pd.read_csv(archivo_subido, sep=",")
        
        # LIMPIAR COLUMNAS (Quitamos espacios invisibles y unificamos mayúsculas/minúsculas)
        df.columns = df.columns.str.strip()
        
        # Mapeo inteligente para asegurar que detecte la columna 'Provincia'
        columnas_mapeo = {col: 'Provincia' for col in df.columns if col.lower() in ['provincia', 'província', 'region', 'región']}
        df = df.rename(columns=columnas_mapeo)
        
        # BARRA LATERAL: Filtros Interactivos
        st.sidebar.header("🎯 Filtros del Panel")
        
        if 'Provincia' in df.columns:
            provincias = ["Todas"] + list(df['Provincia'].dropna().unique())
            provincia_sel = st.sidebar.selectbox("Filtrar por Provincia de CyL:", provincias)
            if provincia_sel != "Todas":
                df_filtrado = df[df['Provincia'] == provincia_sel]
            else:
                df_filtrado = df
        else:
            st.sidebar.warning("⚠️ No se encontró la columna 'Provincia' en el CSV. Mostrando todos los datos.")
            df_filtrado = df

        # INDICADORES CLAVE (Métricas automáticas)
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Casos Analizados", len(df_filtrado))
        with col2:
            if 'Ingresos_Mensuales_EUR' in df_filtrado.columns:
                ingreso_medio = round(df_filtrado['Ingresos_Mensuales_EUR'].mean(), 2)
                st.metric("Ingreso Mensual Promedio", f"{ingreso_medio} €")
            else:
                st.metric("Ingreso Mensual Promedio", "No encontrada col. Ingresos")
        with col3:
            if 'Requiere_Intervencion_Urgente' in df_filtrado.columns:
                casos_urgentes = len(df_filtrado[df_filtrado['Requiere_Intervencion_Urgente'] == 'Sí'])
                st.metric("⚠️ Intervenciones Urgentes", casos_urgentes)
            else:
                st.metric("⚠️ Intervenciones Urgentes", "N/D")
        with col4:
            if 'Edad' in df_filtrado.columns:
                mayores_60 = len(df_filtrado[df_filtrado['Edad'] >= 60])
                st.metric("👴 Personas Mayores (≥60 años)", mayores_60)
            else:
                st.metric("👴 Personas Mayores (≥60 años)", "N/D")

        # 2. LOS 6 BOTONES DE PREGUNTAS PRECONFIGURADAS (Pestañas interactivas)
        st.markdown("## 🔍 Consultas Rápidas Preconfiguradas")
        st.write("Haz clic en las pestañas para responder instantáneamente a tus preguntas clave:")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📋 Resumen Perfil", 
            "🧠 Patrones", 
            "💼 Capacitación Laboral", 
            "🤝 Aislamiento y Grupos", 
            "🏠 Análisis Vivienda", 
            "⏱️ Alta y Seguimiento"
        ])
        
        with tab1:
            st.subheader("Resumen General del Perfil de los Casos")
            col_t1_1, col_t1_2 = st.columns(2)
            with col_t1_1:
                if 'Genero' in df_filtrado.columns:
                    fig_genero = px.pie(df_filtrado, names='Genero', title='Distribución por Género', color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_genero, use_container_width=True)
                else:
                    st.warning("No se encontró la columna 'Genero' para el gráfico.")
            with col_t1_2:
                if 'Edad' in df_filtrado.columns:
                    fig_edad = px.histogram(df_filtrado, x='Edad', nbins=15, title='Distribución de Edades', color_discrete_sequence=['#004080'])
                    st.plotly_chart(fig_edad, use_container_width=True)
                else:
                    st.warning("No se encontró la columna 'Edad' para el gráfico.")
                
        with tab2:
            st.subheader("Patrones de Vulnerabilidad Detectados")
            if 'Situacion_Principal' in df_filtrado.columns and 'Ingresos_Mensuales_EUR' in df_filtrado.columns:
                st.write("Relación entre Situación Principal e Ingresos Mensuales:")
                fig_scatter = px.box(df_filtrado, x='Situacion_Principal', y='Ingresos_Mensuales_EUR', color='Situacion_Principal',
                                     title="Dispersión de Ingresos según Problemática", color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("Faltan las columnas 'Situacion_Principal' o 'Ingresos_Mensuales_EUR' para este análisis.")
            
        with tab3:
            st.subheader("Personas en Edad Laboral para Talleres de Capacitación")
            if 'Edad' in df_filtrado.columns and 'Situacion_Principal' in df_filtrado.columns:
                perfiles_laborales = df_filtrado[(df_filtrado['Edad'] >= 18) & (df_filtrado['Edad'] <= 55) & (df_filtrado['Situacion_Principal'] == 'Desempleo de larga duración')]
                st.write(f"Se han detectado **{len(perfiles_laborales)} personas** aptas para incorporarse a itinerarios de empleo y capacitación digital/textil.")
                if len(perfiles_laborales) > 0:
                    st.dataframe(perfiles_laborales)
            else:
                st.warning("Faltan las columnas 'Edad' o 'Situacion_Principal' para calcular perfiles laborales.")
            
        with tab4:
            st.subheader("Aislamiento Social y Propuestas de Intervención")
            if 'Nivel_Autonomia_Aseo' in df_filtrado.columns:
                st.write("Casos detectados con Dependencia de Aseo o Situaciones de Aislamiento:")
                dependencia_aseo = df_filtrado[df_filtrado['Nivel_Autonomia_Aseo'].isin(['Dependencia Total', 'Dependencia Moderada'])]
                st.dataframe(dependencia_aseo)
            else:
                st.warning("No se encontró la columna 'Nivel_Autonomia_Aseo'.")
            
            st.markdown("### 💡 Propuestas de Intervención Grupal Sugeridas:")
            st.info("1. **Taller de Apoyo Domiciliario Múltiple:** Agrupar casos de Dependencia Moderada en zonas cercanas para optimizar auxiliares del SAD.\n\n"
                     "2. **Cafés Vecinales de Envejecimiento Activo:** Para los perfiles identificados como 'Persona mayor viviendo sola'.")

        with tab5:
            st.subheader("Análisis de la Situación del Entorno y Necesidades")
            if 'Situacion_Principal' in df_filtrado.columns and 'Nivel_Autonomia_Aseo' in df_filtrado.columns:
                fig_sit = px.bar(df_filtrado, x='Situacion_Principal', color='Nivel_Autonomia_Aseo', 
                                 title="Problemática Principal Cruzada con Nivel de Autonomía", barmode='group')
                st.plotly_chart(fig_sit, use_container_width=True)
            else:
                st.warning("Faltan columnas de Situación o Autonomía para este gráfico.")
            
        with tab6:
            st.subheader("Tiempo en Seguimiento y Alertas Críticas")
            if 'Requiere_Intervencion_Urgente' in df_filtrado.columns:
                urgentes = df_filtrado[df_filtrado['Requiere_Intervencion_Urgente'] == 'Sí']
                st.error(f"¡Atención! Hay {len(urgentes)} casos que requieren priorización inmediata en la lista de asuntos sociales:")
                st.dataframe(urgentes)
            else:
                st.warning("No se encontró la columna 'Requiere_Intervencion_Urgente'. Mapeando toda la tabla de datos:")
                st.dataframe(df_filtrado)

        # 3. BUSCADOR INTERACTIVO DE AYUDAS Y RECURSOS
        st.markdown("---")
        st.markdown("## 🌐 Buscador Integrado de Ayudas (JCYL y Nacional)")
        st.write("Selecciona una problemática para obtener las palabras clave e instrucciones de tramitación oficial:")
        
        opcion_ayuda = st.selectbox("¿Qué recurso necesitas gestionar?", [
            "Personas Mayores de 60 años con falta de autonomía en aseo (Dependencia CyL)",
            "Inserción Laboral y Capacitación",
            "Ingreso Mínimo Vital y Renta de Ciudadanía"
        ])
        
        if "aseo" in opcion_ayuda.lower():
            st.warning("🚨 **Recurso Identificado:** Servicio de Ayuda a Domicilio (SAD) y Prestación Económica de la Ley de Dependencia.")
            st.write("**Pasos para tramitar:** El usuario debe acudir al CEAS (Centro de Acción Social) de su municipio en Castilla y León para solicitar la valoración del Grado de Dependencia.")
            st.markdown("[🔗 Buscar en Sede Electrónica JCYL (Dependencia)](https://www.tramitas.jcyl.es/)")
            st.markdown("[🔗 Enlace Oficial del IMSERSO (Nacional)](https://imserso.es)")

        elif "laboral" in opcion_ayuda.lower():
            st.info("💼 **Recurso Identificado:** Programas de fomento del empleo del ECYL (Servicio Público de Empleo de Castilla y León).")
            st.markdown("[🔗 Consultar Cursos de Capacitación ECYL](https://empleo.jcyl.es/)")

        else:
            st.success("💰 **Recurso Identificado:** Renta de Ciudadanía de CyL / Ingreso Mínimo Vital (Seguridad Social).")
            st.markdown("[🔗 Simulador del Ingreso Mínimo Vital (Nacional)](https://prestaciones.seg-social.es/)")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo CSV: {e}")
        st.info("Por favor, asegúrate de que el archivo no esté corrupto y tenga un formato estándar.")
else:
    st.info("💡 Por favor, sube un archivo CSV en el panel central para activar el programa interactivo.")
