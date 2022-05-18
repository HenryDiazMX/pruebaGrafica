from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
import plotly.express as px



# Create your views here.
# Obtencion del Municipio de acuerdo al Estado en la vista de listas y graficas
from django.views.decorators.csrf import csrf_exempt

from cancerinfantil.models import Casostotalrepublica


@csrf_exempt
def municipio2(request):
    global listaMunicipios
    if request.method == 'POST':
        idEstado = request.POST['idEstado']
        municipios = Casostotalrepublica.objects.order_by('mun_resid').all().distinct('mun_resid').filter(ent_resid=idEstado)
        listaMunicipios = "<option value='TODOS'>TODOS</option>"
        for municipio in municipios:
            listaMunicipios = listaMunicipios + "<option value = '" + municipio.mun_resid + "'>" + municipio.mun_resid.upper() + "</option>"
    return HttpResponse(listaMunicipios)


# Obtencion de la Localidad de acuerdo al Municipio en la vista de listas y graficas
@csrf_exempt
def localidad2(request):
    global listaLocalidades
    if request.method == 'POST':
        idMunicipio = request.POST['idMunicipio']
        localidades = Casostotalrepublica.objects.order_by('loc_resid').all().distinct('loc_resid').filter(
            mun_resid=idMunicipio)
        listaLocalidades = "<option value='TODOS'>TODOS</option>"
        for localidad in localidades:
            listaLocalidades = listaLocalidades + "<option value = '" + localidad.loc_resid + "'>" + localidad.loc_resid.upper() + "</option>"
    return HttpResponse(listaLocalidades)


@csrf_exempt
def graficascancer(request):
    global fig1
    datos = Casostotalrepublica.objects.all().values('id','ent_resid','lista_mex','sexo','edad_abs','anio_regis','sitio_ocur','area_ur','agru_edad')
    estados = Casostotalrepublica.objects.distinct('ent_resid')
    anios = Casostotalrepublica.objects.distinct('anio_regis')
    agruedad = Casostotalrepublica.objects.distinct('agru_edad')
    df = None
    tipoGrafica = ['CANCER DOMINANTES','SITIO DE OCURRENCIA', 'TIPO DE ÁREA', 'GENERO', 'EDAD']
    fig = ""
    texto = ""
    div = ""
    defaultEstado = ""
    defaultTipo = ""
    defaultAnio = ""
    defaultRango = ""
    try:
        if request.method == 'POST':
            if request.POST['frmEstado'] != "TODOS":
                datos = datos.filter(ent_resid=request.POST['frmEstado'])
                defaultEstado = request.POST['frmEstado']
            if request.POST['frmAnio'] != "TODOS":
                datos = datos.filter(anio_regis=request.POST['frmAnio'])
                defaultAnio = request.POST['frmAnio']
            if request.POST['frmRangoEdad'] != "TODOS":
                datos = datos.filter(agru_edad=request.POST['frmRangoEdad'])
                defaultRango = request.POST['frmRangoEdad']

            df = pd.DataFrame(datos)

            if request.POST['frmTipo'] == "CANCER DOMINANTES":
                defaultTipo = request.POST['frmTipo']
                datos2 = (df[['anio_regis', 'lista_mex']])
                value_counts = datos2.value_counts()
                df_val_counts = pd.DataFrame(value_counts)
                datos3 = df_val_counts.reset_index()
                datos3.columns = ['Año', 'Tipo De Cancer', 'Conteo']  # change column names
                fig1 = px.pie(datos3, values='Conteo', names='Tipo De Cancer')
                fig1.update_traces(hoverinfo='label+percent', textposition='inside')
                fig1.update_layout(autosize=True, uniformtext_minsize=16, uniformtext_mode='hide',
                                   legend_itemsizing="constant")
                texto = "Gráfica de los tipos de Cáncer Dominantes"
            if request.POST['frmTipo'] == "GENERO":
                defaultTipo = request.POST['frmTipo']
                datos2 = (df[['anio_regis', 'sexo']])
                value_counts = datos2.value_counts()
                df_val_counts = pd.DataFrame(value_counts)
                datos3 = df_val_counts.reset_index()
                datos3.columns = ['AÑO', 'SEXO', 'CONTEO']  # change column names
                fig1 = px.bar(datos3, x="AÑO", y="CONTEO", color="SEXO", height=700)
                texto = "Gráficas por Año de Registro y Genero"
            if request.POST['frmTipo'] == "SITIO DE OCURRENCIA":
                defaultTipo = request.POST['frmTipo']
                datos2 = (df[['sitio_ocur']])
                value_counts = datos2.value_counts()
                df_val_counts = pd.DataFrame(value_counts)
                datos3 = df_val_counts.reset_index()
                datos3.columns = ['SITIO DE OCURRENCIA', 'CONTEO']  # change column names
                fig1 = px.bar(datos3, x="SITIO DE OCURRENCIA", y="CONTEO", color='SITIO DE OCURRENCIA', text="CONTEO",
                              height=700)
                fig1.update_traces(textposition='outside')
                fig1.update_layout(uniformtext_minsize=1, uniformtext_mode='hide', showlegend=False)
                texto = "Lugares de Ocurrencia"
            if request.POST['frmTipo'] == "TIPO DE ÁREA":
                defaultTipo = request.POST['frmTipo']
                datos2 = (df[['anio_regis', 'area_ur']])
                value_counts = datos2.value_counts()
                df_val_counts = pd.DataFrame(value_counts)
                datos3 = df_val_counts.reset_index()
                datos3.columns = ['AÑO', 'TIPO DE AREA', 'CONTEO']  # change column names
                fig1 = px.bar(datos3, x="AÑO", y="CONTEO", color="TIPO DE AREA", height=700)
                texto = "Tipo de Área donde Residía el Niño(a)"
            if request.POST['frmTipo'] == "EDAD":
                defaultTipo = request.POST['frmTipo']
                datos2 = (df[['edad_abs']])
                value_counts = datos2.value_counts()
                df_val_counts = pd.DataFrame(value_counts)
                datos3 = df_val_counts.reset_index()
                datos3.columns = ['EDAD', 'CONTEO']  # change column names
                fig1 = px.bar(datos3, x="EDAD", y="CONTEO", color='EDAD', text="CONTEO", height=700)
                fig1.update_traces(textposition='outside')
                fig1.update_layout(uniformtext_minsize=7, uniformtext_mode='hide', showlegend=False)
                texto = "Gráfica comparativa de edades en el Cáncer Infantil"

            fig = fig1.to_html()
    except:
        div = "Su consulta no tiene casos para mostrar, realice otra consulta"

    return render(request, "cancerinfantil/graficas.html",
                {"fig": fig, "texto": texto, "republica": estados, "anio": anios, "agruedad": agruedad,
                "df": df, "div": div, "defaultEstado": defaultEstado, "tipoGrafica": tipoGrafica, "defaultTipo": defaultTipo,
                "defaultAnio": defaultAnio, "defaultRango": defaultRango})

