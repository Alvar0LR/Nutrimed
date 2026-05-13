from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import CalculoEnergeticoForm
from .models import CalculoEnergetico
from .repositories import CalculoEnergeticoRepository
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io


FACTOR_ACTIVIDAD = {
    'sedentario': 1.0,
    'baja': 1.1,
    'activo': 1.27,
    'muy_activo': 1.54,
}


def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    if imc < 18.5:
        clasificacion = 'Bajo peso'
    elif imc < 25:
        clasificacion = 'Normopeso'
    elif imc < 30:
        clasificacion = 'Sobrepeso'
    elif imc < 35:
        clasificacion = 'Obesidad grado I'
    elif imc < 40:
        clasificacion = 'Obesidad grado II'
    else:
        clasificacion = 'Obesidad grado III'
    return round(imc, 2), clasificacion


def calcular_tmb_mifflin(sexo, peso, altura_cm, edad):
    """Fórmula Mifflin-St Jeor (1990) - precisión 79%"""
    if sexo == 'H':
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad + 5
    else:
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad - 161
    return round(tmb, 2)


def calcular_macros(get_kcal):
    """Distribución según PDF UA: HC 55%, Proteínas 15%, Grasas 30%"""
    proteinas_kcal = get_kcal * 0.15
    hidratos_kcal = get_kcal * 0.55
    grasas_kcal = get_kcal * 0.30
    proteinas_g = round(proteinas_kcal / 4, 2)
    hidratos_g = round(hidratos_kcal / 4, 2)
    grasas_g = round(grasas_kcal / 9, 2)
    return proteinas_g, hidratos_g, grasas_g


@login_required
def calculadora(request):
    repo = CalculoEnergeticoRepository(request.user)
    resultado = None
    historial = repo.get_historial(10)

    ver_id = request.GET.get('ver')
    if ver_id:
        resultado = repo.get_by_id(ver_id)
        form = CalculoEnergeticoForm(instance=resultado)
    else:
        form = CalculoEnergeticoForm()

    if request.method == 'POST':
        form = CalculoEnergeticoForm(request.POST)
        if form.is_valid():
            calculo = form.save(commit=False)
            calculo.usuario = request.user

            peso = float(calculo.peso)
            altura = int(calculo.altura)
            edad = int(calculo.edad)
            sexo = calculo.sexo
            actividad = calculo.actividad

            imc, clasificacion = calcular_imc(peso, altura)
            tmb = calcular_tmb_mifflin(sexo, peso, altura, edad)
            get = round(tmb * FACTOR_ACTIVIDAD[actividad], 2)
            proteinas_g, hidratos_g, grasas_g = calcular_macros(get)

            data = {
                'sexo': sexo,
                'edad': edad,
                'peso': peso,
                'altura': altura,
                'actividad': actividad,
                'imc': imc,
                'clasificacion_imc': clasificacion,
                'tmb': tmb,
                'get': get,
                'proteinas_g': proteinas_g,
                'hidratos_g': hidratos_g,
                'grasas_g': grasas_g,
            }
            resultado = repo.create(data)
            messages.success(request, 'Cálculo guardado correctamente.')
            historial = repo.get_historial(10)

    return render(request, 'calculadora/calculadora.html', {
        'form': form,
        'resultado': resultado,
        'historial': historial,
    })


@login_required
def eliminar_calculo(request, pk):
    repo = CalculoEnergeticoRepository(request.user)
    if request.method == 'POST':
        repo.delete(pk)
        messages.success(request, 'Cálculo eliminado correctamente.')
    return redirect('calculadora')


@login_required
def exportar_excel(request, pk):
    repo = CalculoEnergeticoRepository(request.user)
    c = repo.get_by_id(pk)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Informe NutriMed'

    # Estilos
    verde = '0F6E56'
    blanco = 'FFFFFF'
    gris = 'F5F5F5'

    header_font = Font(bold=True, color=blanco, size=12)
    header_fill = PatternFill(fill_type='solid', fgColor=verde)
    title_font = Font(bold=True, size=14, color=verde)
    center = Alignment(horizontal='center', vertical='center')

    # Título
    ws.merge_cells('A1:C1')
    ws['A1'] = 'NutriMed — Informe de Gasto Energético'
    ws['A1'].font = title_font
    ws['A1'].alignment = center

    ws.merge_cells('A2:C2')
    ws['A2'] = f"Usuario: {request.user.email} | Fecha: {c.fecha.strftime('%d/%m/%Y %H:%M')}"
    ws['A2'].alignment = center
    ws['A2'].font = Font(size=10, color='666666')

    ws.append([])

    # Cabecera sección datos personales
    ws.append(['DATOS PERSONALES', '', ''])
    ws['A4'].font = header_font
    ws['A4'].fill = header_fill
    ws['B4'].fill = header_fill
    ws['C4'].fill = header_fill

    datos = [
        ['Sexo', 'Hombre' if c.sexo == 'H' else 'Mujer', ''],
        ['Edad', f'{c.edad} años', ''],
        ['Peso', f'{c.peso} kg', ''],
        ['Altura', f'{c.altura} cm', ''],
        ['Nivel de actividad', c.get_actividad_display(), ''],
    ]
    for i, row in enumerate(datos):
        ws.append(row)
        if i % 2 == 0:
            for col in ['A', 'B', 'C']:
                ws[f'{col}{ws.max_row}'].fill = PatternFill(fill_type='solid', fgColor=gris.replace('#', ''))

    ws.append([])

    # Cabecera resultados
    fila_res = ws.max_row + 1
    ws.append(['RESULTADOS', '', ''])
    for col in ['A', 'B', 'C']:
        ws[f'{col}{fila_res}'].font = header_font
        ws[f'{col}{fila_res}'].fill = header_fill

    resultados = [
        ['IMC', f'{c.imc} kg/m²', c.clasificacion_imc],
        ['TMB (Metabolismo Basal)', f'{c.tmb} kcal/día', 'Fórmula Mifflin-St Jeor'],
        ['GET (Gasto Total)', f'{c.get} kcal/día', 'TMB × Factor actividad'],
    ]
    for i, row in enumerate(resultados):
        ws.append(row)
        if i % 2 == 0:
            for col in ['A', 'B', 'C']:
                ws[f'{col}{ws.max_row}'].fill = PatternFill(fill_type='solid', fgColor='E8F5F0')

    ws.append([])

    # Macros
    fila_mac = ws.max_row + 1
    ws.append(['DISTRIBUCIÓN DE MACRONUTRIENTES', '', ''])
    for col in ['A', 'B', 'C']:
        ws[f'{col}{fila_mac}'].font = header_font
        ws[f'{col}{fila_mac}'].fill = header_fill

    macros = [
        ['Hidratos de Carbono (55%)', f'{c.hidratos_g} g', f'{round(float(c.hidratos_g) * 4)} kcal'],
        ['Proteínas (15%)', f'{c.proteinas_g} g', f'{round(float(c.proteinas_g) * 4)} kcal'],
        ['Grasas (30%)', f'{c.grasas_g} g', f'{round(float(c.grasas_g) * 9)} kcal'],
    ]
    for i, row in enumerate(macros):
        ws.append(row)
        if i % 2 == 0:
            for col in ['A', 'B', 'C']:
                ws[f'{col}{ws.max_row}'].fill = PatternFill(fill_type='solid', fgColor='FFF3CD')

    ws.append([])
    ws.append(['* Calculado con fórmula Mifflin-St Jeor (1990). Distribución según guías FAO/WHO/ONU.', '', ''])
    ws[f'A{ws.max_row}'].font = Font(italic=True, size=9, color='888888')

    # Anchos de columna
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 25

    # Respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="nutrimed_calculo_{c.id}.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_pdf(request, pk):
    repo = CalculoEnergeticoRepository(request.user)
    c = repo.get_by_id(pk)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    verde = colors.HexColor('#0F6E56')
    rojo_oscuro = colors.HexColor('#A32D2D')

    estilo_titulo = ParagraphStyle('titulo', fontSize=18, textColor=verde,
                                   spaceAfter=6, fontName='Helvetica-Bold', alignment=1)
    estilo_subtitulo = ParagraphStyle('subtitulo', fontSize=10, textColor=colors.grey,
                                      spaceAfter=20, alignment=1)
    estilo_seccion = ParagraphStyle('seccion', fontSize=12, textColor=colors.white,
                                    fontName='Helvetica-Bold', spaceAfter=4)
    estilo_nota = ParagraphStyle('nota', fontSize=8, textColor=colors.grey,
                                 fontName='Helvetica-Oblique', spaceAfter=4)

    elementos = []

    # Título
    elementos.append(Paragraph('NutriMed', estilo_titulo))
    elementos.append(Paragraph('Informe de Gasto Energético', estilo_titulo))
    elementos.append(Paragraph(
        f"Usuario: {request.user.email} | Fecha: {c.fecha.strftime('%d/%m/%Y %H:%M')}",
        estilo_subtitulo
    ))
    elementos.append(Spacer(1, 0.3*cm))

    # Tabla datos personales
    datos_personales = [
        ['DATOS PERSONALES', '', ''],
        ['Sexo', 'Hombre' if c.sexo == 'H' else 'Mujer', ''],
        ['Edad', f'{c.edad} años', ''],
        ['Peso', f'{c.peso} kg', ''],
        ['Altura', f'{c.altura} cm', ''],
        ['Nivel de actividad', c.get_actividad_display(), ''],
    ]

    tabla_datos = Table(datos_personales, colWidths=[6*cm, 6*cm, 5*cm])
    tabla_datos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), verde),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F5F5F5'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_datos)
    elementos.append(Spacer(1, 0.5*cm))

    # Tabla resultados
    datos_resultados = [
        ['RESULTADOS', '', ''],
        ['IMC', f'{c.imc} kg/m²', c.clasificacion_imc],
        ['TMB (Metabolismo Basal)', f'{c.tmb} kcal/día', 'Fórmula Mifflin-St Jeor'],
        ['GET (Gasto Total Diario)', f'{c.get} kcal/día', 'TMB × Factor actividad'],
    ]

    tabla_resultados = Table(datos_resultados, colWidths=[6*cm, 6*cm, 5*cm])
    tabla_resultados.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), verde),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#E8F5F0'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_resultados)
    elementos.append(Spacer(1, 0.5*cm))

    # Tabla macros
    datos_macros = [
        ['DISTRIBUCIÓN DE MACRONUTRIENTES', '', ''],
        ['Hidratos de Carbono (55%)', f'{c.hidratos_g} g', f'{round(float(c.hidratos_g) * 4)} kcal'],
        ['Proteínas (15%)', f'{c.proteinas_g} g', f'{round(float(c.proteinas_g) * 4)} kcal'],
        ['Grasas (30%)', f'{c.grasas_g} g', f'{round(float(c.grasas_g) * 9)} kcal'],
    ]

    tabla_macros = Table(datos_macros, colWidths=[6*cm, 6*cm, 5*cm])
    tabla_macros.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), verde),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFF3CD'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_macros)
    elementos.append(Spacer(1, 0.8*cm))

    # Nota metodológica
    elementos.append(Paragraph(
        '* Calculado con fórmula Mifflin-St Jeor (1990). Distribución de macronutrientes según guías FAO/WHO/ONU. '
        'HC 55% · Proteínas 15% · Grasas 30%.',
        estilo_nota
    ))

    doc.build(elementos)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="nutrimed_calculo_{c.id}.pdf"'
    return response