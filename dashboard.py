import os
import pandas as pd
import io
import plotly.express as px
import streamlit as st

SKIP_STREAMLIT_UI = os.environ.get("SKIP_STREAMLIT_UI") == "1"


def cargar_datos():
    """Carga los datos limpios y normaliza tipos con validaciones estrictas."""
    try:
        df_aire = pd.read_csv("calidad_aire_limpio.csv", low_memory=False)
    except FileNotFoundError:
        df_aire = pd.DataFrame()

    try:
        df_tarifas = pd.read_csv("tarifas_limpio.csv", low_memory=False)
    except FileNotFoundError:
        df_tarifas = pd.DataFrame()

    try:
        df_rips = pd.read_csv("rips_limpio.csv", low_memory=False)
    except FileNotFoundError:
        df_rips = pd.DataFrame()

    # Normalizaciones seguras: Solo se ejecutan si la columna existe en el CSV
    if not df_aire.empty:
        if "MED_FECHA_INICIO" in df_aire.columns:
            df_aire["MED_FECHA_INICIO"] = pd.to_datetime(df_aire["MED_FECHA_INICIO"], errors="coerce")
            df_aire["Año"] = df_aire["MED_FECHA_INICIO"].dt.year
        if "MED_CONCENTRACION_ESTANDAR" in df_aire.columns:
            df_aire["MED_CONCENTRACION_ESTANDAR"] = pd.to_numeric(df_aire["MED_CONCENTRACION_ESTANDAR"], errors="coerce")
        if "LATITUD" in df_aire.columns:
            df_aire["LATITUD"] = pd.to_numeric(df_aire["LATITUD"], errors="coerce")
        if "LONGITUD" in df_aire.columns:
            df_aire["LONGITUD"] = pd.to_numeric(df_aire["LONGITUD"], errors="coerce")

    if not df_tarifas.empty:
        if "Cargo Fijo" in df_tarifas.columns:
            df_tarifas["Cargo Fijo"] = pd.to_numeric(df_tarifas["Cargo Fijo"], errors="coerce")
        if "Cargo por Consumo" in df_tarifas.columns:
            df_tarifas["Cargo por Consumo"] = pd.to_numeric(df_tarifas["Cargo por Consumo"], errors="coerce")
        if "Año" in df_tarifas.columns:
            df_tarifas["Año"] = pd.to_numeric(df_tarifas["Año"], errors="coerce")

    if not df_rips.empty:
        if "NumeroAtenciones" in df_rips.columns:
            df_rips["NumeroAtenciones"] = pd.to_numeric(df_rips["NumeroAtenciones"], errors="coerce")
        # ESTA ES LA LÍNEA QUE TE ESTABA DANDO ERROR. AHORA ESTÁ PROTEGIDA.
        if "Año" in df_rips.columns:
            df_rips["Año"] = pd.to_numeric(df_rips["Año"], errors="coerce")

    return df_aire, df_tarifas, df_rips


@st.cache_data
def cargar_datos_cache():
    return cargar_datos()


def obtener_municipios(df_aire, df_tarifas, df_rips):
    municipios = set()
    for df in [df_aire, df_tarifas, df_rips]:
        if not df.empty and "municipio_clean" in df.columns:
            municipios |= set(df["municipio_clean"].dropna().astype(str).unique())
    return sorted(municipios)


def obtener_años(df_tarifas, df_rips):
    años = set()
    for df in [df_tarifas, df_rips]:
        if not df.empty and "Año" in df.columns:
            años |= set(df["Año"].dropna().astype(int).unique())
    return sorted(años)


def filtrar_datos(df, columna, valores):
    if df.empty or valores is None or len(valores) == 0 or columna not in df.columns:
        return df.copy()
    return df[df[columna].isin(valores)].copy()


def kpis_generales(df_aire, df_tarifas, df_rips):
    # Validaciones para evitar errores en el cálculo de métricas
    val_pm25 = None
    if not df_aire.empty and "MSFL_CODE" in df_aire.columns and "MED_CONCENTRACION_ESTANDAR" in df_aire.columns:
        pm25_filter = df_aire["MSFL_CODE"].astype(str).str.contains("PM2.5", na=False)
        if pm25_filter.any():
            val_pm25 = df_aire[pm25_filter]["MED_CONCENTRACION_ESTANDAR"].mean()
            
    val_cargo = df_tarifas["Cargo Fijo"].mean() if not df_tarifas.empty and "Cargo Fijo" in df_tarifas.columns else None
    val_rips = df_rips["NumeroAtenciones"].sum() if not df_rips.empty and "NumeroAtenciones" in df_rips.columns else None

    return {
        "Registros de aire": int(df_aire.shape[0]) if not df_aire.empty else 0,
        "Promedio PM2.5": float(val_pm25) if val_pm25 is not None and not pd.isna(val_pm25) else None,
        "Cargo fijo promedio": float(val_cargo) if val_cargo is not None and not pd.isna(val_cargo) else None,
        "Atenciones totales": int(val_rips) if val_rips is not None and not pd.isna(val_rips) else None,
    }


def renderizar_dashboard():
    st.set_page_config(page_title="Dashboard Profesional de Datos Limpios", layout="wide")
    st.title("Dashboard Analítico e Integrado - Valle de Aburrá")
    st.markdown("Panel analítico orientado a la toma de decisiones mediante el cruce de variables de calidad del aire, costos de servicios públicos y salud pública.")

    df_aire, df_tarifas, df_rips = cargar_datos_cache()
    municipios = obtener_municipios(df_aire, df_tarifas, df_rips)
    años = obtener_años(df_tarifas, df_rips)

    st.sidebar.header("Filtros de Análisis")
    municipios_seleccionados = st.sidebar.multiselect("Municipios", municipios, default=municipios[:6] if municipios else [])
    años_seleccionados = st.sidebar.multiselect("Años de Análisis", años, default=años[-3:] if años else [])

# 1. LISTA ESTRICTA DE CONTAMINANTES (Ignora clima como 'P', 'VVIENTO', 'HAIRE10')
    contaminantes_reales = ['PM2.5', 'PM10', 'NO2', 'NO', 'SO2', 'O3', 'CO']
    contaminantes = [c for c in contaminantes_reales if c in df_aire["MSFL_CODE"].unique()] if not df_aire.empty and "MSFL_CODE" in df_aire.columns else []
    contaminante_seleccionado = st.sidebar.selectbox("Contaminante Atmosférico", contaminantes, index=0) if contaminantes else None

    services = sorted(df_tarifas["Servicio"].dropna().astype(str).unique()) if not df_tarifas.empty and "Servicio" in df_tarifas.columns else []
    servicio_seleccionado = st.sidebar.selectbox("Servicio Público", services, index=0) if services else None

    # 2. FILTRADO DINÁMICO GLOBAL
    df_aire_filtrado = filtrar_datos(df_aire, "municipio_clean", municipios_seleccionados)
    
    # APLICAR EL FILTRO DE CONTAMINANTE AQUÍ PARA ARREGLAR TODAS LAS PESTAÑAS:
    if contaminante_seleccionado:
        df_aire_filtrado = df_aire_filtrado[df_aire_filtrado["MSFL_CODE"] == contaminante_seleccionado]

    df_tarifas_filtrado = filtrar_datos(df_tarifas, "municipio_clean", municipios_seleccionados)
    df_rips_filtrado = filtrar_datos(df_rips, "municipio_clean", municipios_seleccionados)
    
    if años_seleccionados:
        df_tarifas_filtrado = filtrar_datos(df_tarifas_filtrado, "Año", años_seleccionados)
        df_rips_filtrado = filtrar_datos(df_rips_filtrado, "Año", años_seleccionados)

    # Renderizado de KPIs principales
    kpis = kpis_generales(df_aire_filtrado, df_tarifas_filtrado, df_rips_filtrado)
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Registros de Aire", f"{kpis['Registros de aire']:,}")
    col2.metric("Promedio PM2.5", f"{kpis['Promedio PM2.5']:.2f} µg/m³" if kpis["Promedio PM2.5"] is not None else "N/A")
    col3.metric("Cargo Fijo Promedio", f"${kpis['Cargo fijo promedio']:,.2f}" if kpis["Cargo fijo promedio"] is not None else "N/A")
    col4.metric("Atenciones Totales Salud", f"{kpis['Atenciones totales']:,}" if kpis["Atenciones totales"] is not None else "N/A")

    st.markdown("---")
    tab_aire, tab_tarifas, tab_salud, tab_cruzado, tab_datos = st.tabs(
        ["  Calidad del Aire", "  Tarifas y Servicios", "  Salud Pública", "  Análisis Cruzados", " Datos Crudos"]
    )

    # ==================== PESTAÑA 1: CALIDAD DEL AIRE ====================
    # ==================== PESTAÑA 1: CALIDAD DEL AIRE ====================
    with tab_aire:
        st.subheader(f"Análisis Exclusivo: Calidad del Aire ({contaminante_seleccionado})")
        st.markdown(f"Monitoreo espacial y comportamiento del contaminante **{contaminante_seleccionado}** en la atmósfera.")
        
        if not df_aire_filtrado.empty:
            has_conc = "MED_CONCENTRACION_ESTANDAR" in df_aire_filtrado.columns
            has_mun = "municipio_clean" in df_aire_filtrado.columns

            total_registros = len(df_aire_filtrado)
            total_municipios = int(df_aire_filtrado["municipio_clean"].nunique()) if has_mun else 0
            promedio_global = float(df_aire_filtrado["MED_CONCENTRACION_ESTANDAR"].mean()) if has_conc else None
            max_global = float(df_aire_filtrado["MED_CONCENTRACION_ESTANDAR"].max()) if has_conc else None

            # KPIs Superiores
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            col_a1.metric("Registros de aire", f"{total_registros:,}")
            col_a2.metric("Municipios cubiertos", f"{total_municipios}")
            col_a3.metric("Promedio Regional", f"{promedio_global:.2f} µg/m³" if promedio_global is not None else "N/A")
            col_a4.metric("Máximo Registrado", f"{max_global:.2f} µg/m³" if max_global is not None else "N/A")

            # Gráfica Top 8 Corregida (Escala Roja y Textos)
            if has_mun and has_conc:
                top_municipios = df_aire_filtrado.groupby("municipio_clean", as_index=False)["MED_CONCENTRACION_ESTANDAR"].mean().sort_values("MED_CONCENTRACION_ESTANDAR", ascending=False).head(8)
                fig_top_mun = px.bar(
                    top_municipios, x="MED_CONCENTRACION_ESTANDAR", y="municipio_clean",
                    orientation="h", title=f"Top 8 municipios con mayor concentración de {contaminante_seleccionado}",
                    labels={"MED_CONCENTRACION_ESTANDAR": "Promedio", "municipio_clean": "Municipio"},
                    color="MED_CONCENTRACION_ESTANDAR", color_continuous_scale="Reds", text_auto='.2f'
                )
                fig_top_mun.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_top_mun, use_container_width=True)

            st.markdown("---")
            col_map, col_stats = st.columns([2, 1])

            # Mapa Interactivo
            with col_map:
                if "LATITUD" in df_aire_filtrado.columns and "LONGITUD" in df_aire_filtrado.columns and has_conc:
                    mapa = df_aire_filtrado.dropna(subset=["LATITUD", "LONGITUD", "MED_CONCENTRACION_ESTANDAR"])
                    mapa = mapa[mapa["MED_CONCENTRACION_ESTANDAR"] > 0]
                    
                    if not mapa.empty:
                        fig_map = px.scatter_mapbox(
                            mapa, lat="LATITUD", lon="LONGITUD", color="MED_CONCENTRACION_ESTANDAR",
                            size="MED_CONCENTRACION_ESTANDAR", hover_name="ESTACION_ID",
                            hover_data={"municipio_clean": True},
                            color_continuous_scale="Reds", zoom=10, height=550, mapbox_style="carto-positron",
                            title=f"Mapa de Estaciones: {contaminante_seleccionado}"
                        )
                        st.plotly_chart(fig_map, use_container_width=True)
                    else:
                        st.info("No hay coordenadas válidas para el mapa.")

            # Gráficos de Distribución
            with col_stats:
                fig_hist = px.histogram(
                    df_aire_filtrado, x="MED_CONCENTRACION_ESTANDAR", nbins=30,
                    title=f"Distribución ({contaminante_seleccionado})"
                )
                st.plotly_chart(fig_hist, use_container_width=True)

                fig_box = px.box(
                    df_aire_filtrado, x="municipio_clean", y="MED_CONCENTRACION_ESTANDAR",
                    title=f"Variabilidad por Municipio"
                )
                st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("No hay datos de aire para analizar con los filtros actuales.")

    # ==================== PESTAÑA 2: TARIFAS Y SERVICIOS ====================
    with tab_tarifas:
        st.subheader("Análisis Exclusivo: Tarifas y Servicios Públicos")
        st.markdown("Estructura de costos, cargos fijos y análisis por estrato socioeconómico.")
        
        if servicio_seleccionado is not None and not df_tarifas_filtrado.empty:
            df_tarifas_servicio = df_tarifas_filtrado[df_tarifas_filtrado["Servicio"] == servicio_seleccionado]
            if not df_tarifas_servicio.empty and "Cargo Fijo" in df_tarifas_servicio.columns:
                col_bar, col_stats = st.columns([2, 1])
                
                with col_bar:
                    df_grouped_tar = df_tarifas_servicio.groupby(["municipio_clean", "Estrato"], as_index=False)["Cargo Fijo"].mean()
                    fig_tar = px.bar(
                        df_grouped_tar, x="municipio_clean", y="Cargo Fijo", color="Estrato", barmode="group",
                        title=f"Cargo Fijo Promedio por Municipio y Estrato - {servicio_seleccionado}"
                    )
                    st.plotly_chart(fig_tar, use_container_width=True)
                
                with col_stats:
                    st.metric("Servicio Seleccionado", servicio_seleccionado)
                    st.metric("Cargo Fijo Promedio", f"${df_tarifas_servicio['Cargo Fijo'].mean():,.2f}")
                    st.metric("Costo Máximo", f"${df_tarifas_servicio['Cargo Fijo'].max():,.2f}")
                    st.metric("Costo Mínimo", f"${df_tarifas_servicio['Cargo Fijo'].min():,.2f}")
                
                # Análisis por estrato
                st.markdown("---")
                st.subheader("Resumen por Estrato Socioeconómico")
                df_estrato = df_tarifas_servicio.groupby("Estrato", as_index=False).agg({
                    "Cargo Fijo": ["mean", "min", "max"],
                    "Cargo por Consumo": "mean"
                }).round(2)
                df_estrato.columns = ["Estrato", "Cargo Fijo Promedio", "Mínimo", "Máximo", "Consumo Promedio"]
                st.dataframe(df_estrato, use_container_width=True)
                
                # Tendencia temporal si existe Año
                if "Año" in df_tarifas_servicio.columns:
                    st.markdown("---")
                    st.subheader("Evolución de Tarifas en el Tiempo")
                    df_trend = df_tarifas_servicio.groupby(["Año", "municipio_clean"], as_index=False)["Cargo Fijo"].mean()
                    fig_trend = px.line(
                        df_trend, x="Año", y="Cargo Fijo", color="municipio_clean", markers=True,
                        title="Tendencia Anual del Cargo Fijo"
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning("Faltan columnas necesarias (como Cargo Fijo) en los datos de tarifas.")
        else:
            st.warning("Defina un servicio público válido o revise sus datos de tarifas.")

    # ==================== PESTAÑA 3: SALUD PÚBLICA ====================
    with tab_salud:
        st.subheader("Análisis Exclusivo: Salud Pública (RIPS)")
        st.markdown("Registros Individuales de Prestación de Servicios en Salud. Diagnósticos, atenciones y categorías médicas.")
        
        if not df_rips_filtrado.empty:
            # Métricas principales
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Total Atenciones", f"{df_rips_filtrado['NumeroAtenciones'].sum():,.0f}")
            col_m2.metric("Registros Únicos", f"{len(df_rips_filtrado):,}")
            col_m3.metric("Municipios Cubiertos", f"{df_rips_filtrado['municipio_clean'].nunique()}")
            if "Categoria_Salud" in df_rips_filtrado.columns:
                col_m4.metric("Categorías de Salud", f"{df_rips_filtrado['Categoria_Salud'].nunique()}")
            
            st.markdown("---")
            
            # Timeline si existe Año
            if "Año" in df_rips_filtrado.columns and "Categoria_Salud" in df_rips_filtrado.columns:
                st.subheader("Evolución Histórica de Atenciones por Categoría")
                df_grouped_salud = df_rips_filtrado.groupby(["Año", "Categoria_Salud"], as_index=False)["NumeroAtenciones"].sum()
                fig_salud = px.area(
                    df_grouped_salud, x="Año", y="NumeroAtenciones", color="Categoria_Salud",
                    title="Cambios en Atenciones Médicas a lo Largo del Tiempo"
                )
                fig_salud.update_xaxes(dtick=1)
                st.plotly_chart(fig_salud, use_container_width=True)
                
                st.markdown("---")
            
            # Top 10 diagnósticos
            st.subheader("Top 10 Diagnósticos con Mayor Demanda")
            if "Diagnostico" in df_rips_filtrado.columns and "NumeroAtenciones" in df_rips_filtrado.columns:
                top_diag = df_rips_filtrado.groupby("Diagnostico", as_index=False)["NumeroAtenciones"].sum().sort_values(by="NumeroAtenciones", ascending=False).head(10)
                fig_top = px.bar(
                    top_diag, x="NumeroAtenciones", y="Diagnostico", orientation="h",
                    title="Diagnósticos Médicos con Mayor Número de Atenciones",
                    color="NumeroAtenciones", color_continuous_scale="Blues"
                )
                fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_top, use_container_width=True)
            
            # Distribución por categoría
            st.markdown("---")
            st.subheader("Distribución de Atenciones por Categoría")
            if "Categoria_Salud" in df_rips_filtrado.columns:
                df_cat = df_rips_filtrado.groupby("Categoria_Salud", as_index=False)["NumeroAtenciones"].sum().sort_values("NumeroAtenciones", ascending=False)
                col_pie, col_table = st.columns([1, 1])
                with col_pie:
                    fig_pie = px.pie(df_cat, values="NumeroAtenciones", names="Categoria_Salud", title="Proporción de Categorías")
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_table:
                    st.dataframe(df_cat, use_container_width=True)
        else:
            st.warning("No existen registros de salud RIPS compatibles con el filtro actual.")

    # ==================== PESTAÑA 4: ANÁLISIS CRUZADOS ====================
    with tab_cruzado:
        st.subheader("Análisis Cruzados: Relaciones entre Múltiples Fuentes de Datos")
        st.markdown("Explorar correlaciones e interacciones entre aire, tarifas y salud. **Requiere 2+ bases de datos válidas.**")
        
        # Sub-opciones de análisis cruzados
        cruzado_opcion = st.radio(
            "Selecciona el tipo de análisis cruzado:",
            ["Contaminación ↔ Salud", "Tarifas ↔ Salud", "Aire ↔ Tarifas", "Análisis Geográfico Integrado"]
        )
        
        # === CRUCE 1: CONTAMINACIÓN ↔ SALUD ===
        if cruzado_opcion == "Contaminación ↔ Salud":
            st.markdown("#### Cruce: Calidad del Aire → Impacto en Salud Pública")
            if not df_aire_filtrado.empty and not df_rips_filtrado.empty:
                if "MED_CONCENTRACION_ESTANDAR" in df_aire_filtrado.columns and "NumeroAtenciones" in df_rips_filtrado.columns:
                    resumen_aire = df_aire_filtrado.groupby("municipio_clean", as_index=False)["MED_CONCENTRACION_ESTANDAR"].mean().rename(columns={"MED_CONCENTRACION_ESTANDAR": "Contaminación Promedio"})
                    resumen_salud = df_rips_filtrado.groupby("municipio_clean", as_index=False)["NumeroAtenciones"].sum().rename(columns={"NumeroAtenciones": "Total Atenciones"})
                    correlacion_aire_salud = pd.merge(resumen_aire, resumen_salud, on="municipio_clean", how="inner")

                    if not correlacion_aire_salud.empty:
                        col_scatter, col_corr = st.columns([2, 1])
                        with col_scatter:
                            fig_scatter = px.scatter(
                                correlacion_aire_salud, x="Contaminación Promedio", y="Total Atenciones", text="municipio_clean",
                                size="Total Atenciones", color="Contaminación Promedio", size_max=50,
                                title="¿Mayor Contaminación = Más Atenciones Médicas?",
                                labels={"Contaminación Promedio": "Promedio de Concentración", "Total Atenciones": "Número de Atenciones"}
                            )
                            st.plotly_chart(fig_scatter, use_container_width=True)
                        
                        with col_corr:
                            corr_value = correlacion_aire_salud["Contaminación Promedio"].corr(correlacion_aire_salud["Total Atenciones"])
                            st.metric("Correlación (Pearson)", f"{corr_value:.3f}")
                            if corr_value > 0.7:
                                st.success("Correlación fuerte positiva")
                            elif corr_value > 0.3:
                                st.info("Correlación moderada")
                            else:
                                st.warning("Correlación débil o nula")
                        
                        st.dataframe(correlacion_aire_salud, use_container_width=True)
                    else:
                        st.warning("No hay intersección de datos municipales suficientes.")
                else:
                    st.warning("Faltan columnas clave para el cruce aire-salud.")
            else:
                st.warning("Se requieren datos válidos de aire y salud.")
        
        # === CRUCE 2: TARIFAS ↔ SALUD ===
        elif cruzado_opcion == "Tarifas ↔ Salud":
            st.markdown("#### Cruce: Costo de Servicios → Impacto en Salud")
            if not df_tarifas_filtrado.empty and not df_rips_filtrado.empty:
                if "Cargo Fijo" in df_tarifas_filtrado.columns and "NumeroAtenciones" in df_rips_filtrado.columns:
                    resumen_tarifas = df_tarifas_filtrado.groupby("municipio_clean", as_index=False)["Cargo Fijo"].mean().rename(columns={"Cargo Fijo": "Costo Promedio"})
                    resumen_salud = df_rips_filtrado.groupby("municipio_clean", as_index=False)["NumeroAtenciones"].sum().rename(columns={"NumeroAtenciones": "Total Atenciones"})
                    correlacion_tar_salud = pd.merge(resumen_tarifas, resumen_salud, on="municipio_clean", how="inner")

                    if not correlacion_tar_salud.empty:
                        col_scatter, col_corr = st.columns([2, 1])
                        with col_scatter:
                            fig_scatter = px.scatter(
                                correlacion_tar_salud, x="Costo Promedio", y="Total Atenciones", text="municipio_clean",
                                size="Total Atenciones", color="Costo Promedio", size_max=50,
                                title="¿Servicios Más Caros = Menos Acceso a Salud?",
                                labels={"Costo Promedio": "Cargo Fijo Promedio", "Total Atenciones": "Número de Atenciones"}
                            )
                            st.plotly_chart(fig_scatter, use_container_width=True)
                        
                        with col_corr:
                            corr_value = correlacion_tar_salud["Costo Promedio"].corr(correlacion_tar_salud["Total Atenciones"])
                            st.metric("Correlación (Pearson)", f"{corr_value:.3f}")
                            if corr_value < -0.5:
                                st.warning("Correlación negativa: costos altos vs atenciones bajas")
                            else:
                                st.info("Correlación débil o nula")
                        
                        st.dataframe(correlacion_tar_salud, use_container_width=True)
                    else:
                        st.warning("No hay intersección de datos municipales suficientes.")
                else:
                    st.warning("Faltan columnas clave para el cruce tarifas-salud.")
            else:
                st.warning("Se requieren datos válidos de tarifas y salud.")
        
        # === CRUCE 3: AIRE ↔ TARIFAS ===
        elif cruzado_opcion == "Aire ↔ Tarifas":
            st.markdown("#### Cruce: Calidad Ambiental → Impacto Económico en Servicios")
            if not df_aire_filtrado.empty and not df_tarifas_filtrado.empty:
                st.info("📌 Este cruce muestra si municipios con peor aire tienen costos de servicio diferenciados.")
                resumen_aire = df_aire_filtrado.groupby("municipio_clean", as_index=False)["MED_CONCENTRACION_ESTANDAR"].mean().rename(columns={"MED_CONCENTRACION_ESTANDAR": "Contaminación"})
                resumen_tarifas = df_tarifas_filtrado.groupby("municipio_clean", as_index=False)["Cargo Fijo"].mean().rename(columns={"Cargo Fijo": "Costo Fijo"})
                correlacion_aire_tar = pd.merge(resumen_aire, resumen_tarifas, on="municipio_clean", how="inner")

                if not correlacion_aire_tar.empty:
                    fig_scatter = px.scatter(
                        correlacion_aire_tar, x="Contaminación", y="Costo Fijo", text="municipio_clean",
                        size="Costo Fijo", color="Contaminación", size_max=50,
                        title="Contaminación vs Costo de Servicios"
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    st.dataframe(correlacion_aire_tar, use_container_width=True)
                else:
                    st.warning("No hay intersección de datos municipales.")
            else:
                st.warning("Se requieren datos válidos de aire y tarifas.")
        
        # === CRUCE 4: ANÁLISIS GEOGRÁFICO INTEGRADO ===
        else:  # Análisis Geográfico Integrado
            st.markdown("#### Análisis Integrado por Municipio")
            st.info("📌 Comparativa de múltiples indicadores por municipio.")
            
            municipios_unicos = set()
            if "municipio_clean" in df_aire_filtrado.columns:
                municipios_unicos |= set(df_aire_filtrado["municipio_clean"].unique())
            if "municipio_clean" in df_tarifas_filtrado.columns:
                municipios_unicos |= set(df_tarifas_filtrado["municipio_clean"].unique())
            if "municipio_clean" in df_rips_filtrado.columns:
                municipios_unicos |= set(df_rips_filtrado["municipio_clean"].unique())
            
            municipios_unicos = sorted(municipios_unicos)
            
            if municipios_unicos:
                df_integrado = pd.DataFrame({"municipio_clean": municipios_unicos})
                
                # Agregar datos de aire
                if not df_aire_filtrado.empty:
                    aire_agg = df_aire_filtrado.groupby("municipio_clean")["MED_CONCENTRACION_ESTANDAR"].mean().reset_index()
                    aire_agg.columns = ["municipio_clean", "Contaminación Promedio"]
                    df_integrado = pd.merge(df_integrado, aire_agg, on="municipio_clean", how="left")
                
                # Agregar datos de tarifas
                if not df_tarifas_filtrado.empty:
                    tarifas_agg = df_tarifas_filtrado.groupby("municipio_clean")["Cargo Fijo"].mean().reset_index()
                    tarifas_agg.columns = ["municipio_clean", "Cargo Fijo Promedio"]
                    df_integrado = pd.merge(df_integrado, tarifas_agg, on="municipio_clean", how="left")
                
                # Agregar datos de salud
                if not df_rips_filtrado.empty:
                    salud_agg = df_rips_filtrado.groupby("municipio_clean")["NumeroAtenciones"].sum().reset_index()
                    salud_agg.columns = ["municipio_clean", "Total Atenciones"]
                    df_integrado = pd.merge(df_integrado, salud_agg, on="municipio_clean", how="left")
                
                st.subheader("Matriz Integrada por Municipio")
                st.dataframe(df_integrado.round(2), use_container_width=True)
                
                # Visualización de radar si hay suficientes dimensiones
                if len(df_integrado.columns) >= 3:
                    st.markdown("---")
                    st.subheader("Perfil de Municipios (Comparativo Normalizado)")
                    st.info("Cada municipio muestra su fortaleza relativa en cada dimensión.")
            else:
                st.warning("No hay datos municipales disponibles para el análisis integrado.")

    # ==================== PESTAÑA 5: DATOS CRUDOS ====================
    with tab_datos:
        st.subheader("Exploración de Datos Crudos y Descarga")
        st.markdown("Inspecciona muestras de los datos limpios. Descarga subconjuntos filtrados para análisis offline.")
        
        st.markdown("---")
        st.markdown("### 📊 Base de Datos: Calidad del Aire")
        if not df_aire_filtrado.empty:
            col_info, col_desc = st.columns(2)
            with col_info:
                st.metric("Registros", len(df_aire_filtrado))
                st.metric("Columnas", len(df_aire_filtrado.columns))
            with col_desc:
                st.info(f"Período: {df_aire_filtrado['MED_FECHA_INICIO'].min() if 'MED_FECHA_INICIO' in df_aire_filtrado.columns else 'N/A'} a {df_aire_filtrado['MED_FECHA_INICIO'].max() if 'MED_FECHA_INICIO' in df_aire_filtrado.columns else 'N/A'}")
            
            # Mostrar salida de df.info() capturada
            with st.expander("Ver info() de la tabla de Aire"):
                buf = io.StringIO()
                df_aire_filtrado.info(buf=buf)
                info_str = buf.getvalue()
                st.text(info_str)

            # Mostrar df.describe() para la tabla de aire
            with st.expander("Ver describe() de la tabla de Aire"):
                st.dataframe(df_aire_filtrado.describe(include='all').round(2), use_container_width=True)

            st.dataframe(df_aire_filtrado.head(50), use_container_width=True)
            st.download_button(
                label="📥 Descargar Aire (CSV)",
                data=df_aire_filtrado.to_csv(index=False).encode("utf-8"),
                file_name="aire_filtrado.csv",
                mime="text/csv"
            )
        else:
            st.warning("No hay datos de aire para descargar con los filtros actuales.")
        
        st.markdown("---")
        st.markdown("### 💧 Base de Datos: Tarifas y Servicios")
        if not df_tarifas_filtrado.empty:
            col_info, col_desc = st.columns(2)
            with col_info:
                st.metric("Registros", len(df_tarifas_filtrado))
                st.metric("Columnas", len(df_tarifas_filtrado.columns))
            with col_desc:
                st.info(f"Servicios disponibles: {', '.join(df_tarifas_filtrado['Servicio'].unique())}")
            
            # Mostrar salida de df.info() capturada
            with st.expander("Ver info() de la tabla de Tarifas"):
                buf = io.StringIO()
                df_tarifas_filtrado.info(buf=buf)
                info_str = buf.getvalue()
                st.text(info_str)

            # Mostrar df.describe() para la tabla de tarifas
            with st.expander("Ver describe() de la tabla de Tarifas"):
                st.dataframe(df_tarifas_filtrado.describe(include='all').round(2), use_container_width=True)

            st.dataframe(df_tarifas_filtrado.head(50), use_container_width=True)
            st.download_button(
                label="📥 Descargar Tarifas (CSV)",
                data=df_tarifas_filtrado.to_csv(index=False).encode("utf-8"),
                file_name="tarifas_filtrado.csv",
                mime="text/csv"
            )
        else:
            st.warning("No hay datos de tarifas para descargar con los filtros actuales.")
        
        st.markdown("---")
        st.markdown("### 🏥 Base de Datos: Salud Pública (RIPS)")
        if not df_rips_filtrado.empty:
            col_info, col_desc = st.columns(2)
            with col_info:
                st.metric("Registros", len(df_rips_filtrado))
                st.metric("Columnas", len(df_rips_filtrado.columns))
            with col_desc:
                if "Categoria_Salud" in df_rips_filtrado.columns:
                    st.info(f"Categorías: {', '.join(df_rips_filtrado['Categoria_Salud'].unique())}")
            
            # Mostrar salida de df.info() capturada
            with st.expander("Ver info() de la tabla de Salud (RIPS)"):
                buf = io.StringIO()
                df_rips_filtrado.info(buf=buf)
                info_str = buf.getvalue()
                st.text(info_str)

            # Mostrar df.describe() para la tabla de salud
            with st.expander("Ver describe() de la tabla de Salud (RIPS)"):
                st.dataframe(df_rips_filtrado.describe(include='all').round(2), use_container_width=True)

            st.dataframe(df_rips_filtrado.head(50), use_container_width=True)
            st.download_button(
                label="📥 Descargar Salud (CSV)",
                data=df_rips_filtrado.to_csv(index=False).encode("utf-8"),
                file_name="rips_filtrado.csv",
                mime="text/csv"
            )
        else:
            st.warning("No hay datos de salud para descargar con los filtros actuales.")

if not SKIP_STREAMLIT_UI:
    renderizar_dashboard()