from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from .models import *


def index(request):
    return render(request, 'vroom/index.html')

@login_required
def entrega(request, id_curso, id_tarea, id_alumno):
    alumno = Usuario.objects.get(id=id_alumno)
    tarea = Tarea.objects.get(id=id_tarea)
    entregas = Entrega.objects.filter(tarea=tarea, autor=alumno).values()
    curso = Curso.objects.get(id=id_curso)
    todas_entregas = list(Entrega.objects.filter(tarea=tarea).values())

    lista_entregas = []
    for entrega in todas_entregas:
        if not entrega['autor_id'] in lista_entregas:
            lista_entregas.append(entrega['autor_id'])

    for entrega in entregas:
        auto_puntuacion = model_to_dict(Auto_Puntuacion.objects.get(id = entrega['auto_puntuacion_id']))
        entrega['auto_puntuacion'] = auto_puntuacion


    contexto = {
        "alumno": model_to_dict(alumno),
        "tarea": model_to_dict(tarea),
        "curso": model_to_dict(curso),
        "entregas": list(entregas),
        "lista_entregas": lista_entregas,
    }
    return render(request, 'vroom/entrega.html', contexto)

@login_required
def dashboard(request):
    return render(request, 'vroom/dashboard.html')

@login_required
def curso(request, id_curso):
    curso = Curso.objects.get(id = id_curso)

    tareas = list(Tarea.objects.filter(curso = id_curso).values())
    for tarea in tareas:
        tarea["tipo"] = "tarea"
    links = list(Link.objects.filter(curso = id_curso).values())
    for link in links:
        link["tipo"] = "link"
    textos = list(Texto.objects.filter(curso = id_curso).values())
    for texto in textos:
        texto["tipo"] = "texto"
    documentos = list(Documento.objects.filter(curso = id_curso).values())
    for documento in documentos:
        documento["tipo"] = "documento"
    
    contenidos = tareas+links+textos+documentos   
    contenidos = sorted(contenidos, key=lambda contenido: contenido.get("fecha_publicacion"))

    rol = Usuario_Curso.objects.get(usuario = request.user.id, curso = id_curso).tipo_subscripcion.nombre

    contexto = {
        "curso": curso,
        "contenidos": contenidos,
        "rol": rol
    }

    return render(request, 'vroom/curso.html', contexto)


@login_required
def tarea(request, id_tarea, id_curso):
    tarea = Tarea.objects.get(id = id_tarea)

    tarea_dict = model_to_dict(tarea)
    tarea_dict["curso_nombre"]= tarea.curso.titulo

    rol = Usuario_Curso.objects.get(usuario = request.user, curso = tarea.curso).tipo_subscripcion

    if (rol.nombre == "Alumno"):
        
        
        entregas = list(Entrega.objects.filter(tarea = tarea.id, autor = request.user).values())
        if len(entregas) == 0:
            entregas = False
        else:
            for entrega in entregas:
                auto_puntuacion = model_to_dict(Auto_Puntuacion.objects.get(id = entrega['auto_puntuacion_id']))
                entrega['auto_puntuacion'] = auto_puntuacion
            
        try:
            calificacion = model_to_dict(Calificacion.objects.get(tarea = tarea.id, alumno = request.user))
            profe = Calificacion.objects.get(tarea = tarea.id, alumno = request.user).profesor
            calificacion["profesor"] = profe.first_name + " " + profe.last_name
        except:
            calificacion = False
        

        contexto = {
            "tarea": tarea_dict,
            "entregas": entregas,
            "calificacion": calificacion,
        }

        return render(request, 'vroom/tarea_alumno.html', contexto)

    else:
        
        alumnos_curso = list(Usuario_Curso.objects.filter(curso = tarea.curso, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Alumno").id).values())

        alumnos = []
        for alumno in alumnos_curso:
            try:
                ultima_entrega = (Entrega.objects.filter(tarea = tarea.id, autor = alumno["usuario_id"]).latest('fecha_edicion')).fecha_edicion
            except:
                ultima_entrega = False
            id_alumno = alumno["usuario_id"]
            dict_alumno = model_to_dict(Usuario.objects.get(id = id_alumno))
            dict_alumno["ultima_entrega"] = ultima_entrega
            alumnos.append(dict_alumno)

        entregas = Entrega.objects.filter(tarea = tarea.id).values()
        for entrega in entregas:
            auto_puntuacion = model_to_dict(Auto_Puntuacion.objects.get(id = entrega['auto_puntuacion_id']))
            entrega['auto_puntuacion'] = auto_puntuacion
            
        contexto = {
            "tarea": tarea_dict,
            "alumnos": list(alumnos),
            "entregas": list(entregas)
        }

        return render(request, 'vroom/tarea_profesor.html', contexto)