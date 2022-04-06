from enum import auto
from webbrowser import get
from django.http import JsonResponse
from django.http import Http404
from vroom.models import *
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import random
import json
from django.forms.models import model_to_dict


def ping(request):
    if (request.method=='GET'):
        return JsonResponse({
            'status': 'OK',
            'message': 'Conexión exitosa.',
        })

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def start_vr_exercise(request):
    getpin=request.GET.get('pin')
    
    try:
        pin = Pin.objects.get(pin=getpin)
    except:
        
        return Response({
            'status': 'ERROR',
            'message': 'Pin no encontrado.'
        })

    user = pin.usuario
    vr_exerciseid = pin.tarea.id
    minVer = Tarea.objects.get(id=vr_exerciseid).min_exercise_version
    if (minVer == None):
        minVer = None
    return Response({
        "status" : "OK",
        "username": user.first_name+" "+user.last_name,
        "VRexerciseID" :  vr_exerciseid,
        "minExerciseVersion" : minVer,
    })


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def finish_vr_exercise(request):

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    getpin=int(body['pin'])
    autograde=body['autograde']
    VRexerciseID=int(body['VRexerciseID'])
    exerciseVersionID=float(body['exerciseVersionID'])
    performance_data = body['performance_data']


    # Comprueba que el pin existe
    try:
        pin = Pin.objects.get(pin=getpin)
    except:
        return Response({
            'status': 'ERROR',
            'message': 'Pin no encontrado.'
        })


    # Comprueba que estan todos los parametros
    if getpin==None or autograde==None or VRexerciseID==None or exerciseVersionID==None or performance_data==None:
        return Response({
            'status': 'ERROR',
            'message': 'Faltan parametros.'
        })

    # Comprueba que el autograde es correcto
    try:
        autograde_passed_items = int(autograde['passed_items'])
        if not autograde_passed_items and not autograde_passed_items == 0:
            return Response({
                'status': 'ERROR',
                'message': 'Autograde: No se han pasado "passed_items".'
            })
        
        autograde_failed_items = int(autograde['failed_items'])
        if not autograde_failed_items and not autograde_failed_items == 0:
            return Response({
                'status': 'ERROR',
                'message': 'Autograde: No se han pasado "failed_items".'
            })

        autograde_score = float(autograde['score'])
        if not autograde_score and not autograde_score == 0:
            return Response({
                'status': 'ERROR',
                'message': 'Autograde: No se ha pasado "score".'
            })    
        
    except:
        return Response({
            'status': 'ERROR',
            'message': 'Autograde: Parametros incorrectos.'
        })

    try:
        comentario = str(autograde['comments'])
    except:
        comentario = ''

    auto_puntuacion = Auto_Puntuacion.objects.create(
        passed_items = autograde_passed_items,
        failed_items = autograde_failed_items,
        score = autograde_score,
        comments = comentario,
    )
   
    entrega = Entrega.objects.create(
        autor = pin.usuario,
        tarea = pin.tarea,
        fecha_publicacion = timezone.now(),
        fecha_edicion = timezone.now(),
        auto_puntuacion = auto_puntuacion,
        nota = None,
    )
    setattr(entrega, 'archivo', '/static/assets/archivos/performance_data-' + str(pin.usuario.id) + str(entrega.id) + '.json')
    entrega.save()
    try:

        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        performance_data_file = open(os.path.join(workpath,'../static/assets/archivos/performance_data-' + str(pin.usuario.id) + str(entrega.id) + '.json'), 'w+')
        performance_data_file.write(json.dumps(performance_data))
        performance_data_file.close()

    except:
        traceback.print_exc()
        
        entrega.delete()
        
        return Response({
            'status': 'ERROR',
            'message': 'Error al guardar performance_data.'
        })


    # Se borra el pin
    pin.delete()

    return Response({
        'status': 'OK',
        'message': 'Entrega guardada.'
    })



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pin_request(request):

    VRtaskID = request.GET.get('VRtaskID')

    try:
        tarea = Tarea.objects.get(id=VRtaskID)
    except:
        return Response({
            "status" : "ERROR",
            "message" : "Tarea no encontrado.",
        })


    while True:
        randomnum = random.randint(1000,9999)

        try:
            if(Pin.objects.filter(tarea=tarea, usuario=request.user).exists()):
                return Response({
                    "status" : "ERROR",
                    "message" : "Ya existe un pin para este usuario.",
                })
            Pin.objects.get(pin=randomnum)

        except:
            break




    new_pin = Pin.objects.create(
        pin = randomnum,
        tarea = tarea,
        usuario = request.user
    )

    new_pin.save()

    return Response({
        'status':'OK',
        'message': 'Pin generado.',
        'PIN': new_pin.pin
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_course_details(request):

    id_curso=request.GET.get('courseID')
    subscripcion_profesor = Tipo_Subscripcion.objects.get(nombre = "Profesor")


    
    try:
        curso = Curso.objects.get( id = id_curso)
    except:
        return Response({
            "status" : "ERROR",
            "message" : "Curso no encontrado.",
        })

    content = {"title": curso.titulo,"description": curso.descripcion,"courseID": curso.id,"institutionID": curso.centro.id,"status": curso.estado,'elements':{'links':[],'texts':[],'documents':[],'tasks':[]} }
    if(id_curso == None):
        return Response({
        "status" : 'ERROR',
        "message" : 'courseID is required.'
        })

    if(not request.user.is_superuser):        
        try:
            usuario = Usuario_Curso.objects.get(usuario = request.user, curso_id = id_curso)
        except:
            return Response({
                "status" : "ERROR",
                "message" : "Usuario no inscrito en el curso.",
            })
        


    links = Link.objects.filter(curso_id = id_curso)
    links_items = []
    for link in links:
        links_items.append({"linkID": link.id, "title": link.titulo, "link": link.link})   
    content['elements']['links'] = links_items
    
    textos = Texto.objects.filter(curso_id = id_curso)
    textos_items = []
    for texto in textos:
        textos_items.append({"textID": texto.id, "autorID":texto.autor.id, "title": texto.titulo, "texto": texto.texto})
    content['elements']['texts'] = textos_items
    
    documents = Documento.objects.filter(curso_id = id_curso)
    documents_items = []
    for document in documents:
        documents_items.append({"documentID": document.id, "autorID":document.autor.id, "file":document.archivo.url})
    content['elements']['documents'] = documents_items
    
    tasks = Tarea.objects.filter(curso_id = id_curso).all()
    tasks_items = []
    for task in tasks:
        tasks_items.append({"taskID": task.id, "title": task.titulo, "enunciado": task.enunciado, "maxQualification": task.nota_maxima})
    content['elements']['tasks'] = tasks_items
          
               
    return Response({
        "status" : 'OK',
        "course_list": content
    })

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_courses(request):

    cursos = Curso.objects.all()

    content = []
    subscripcion_profesor = Tipo_Subscripcion.objects.get(nombre = "Profesor")
    subscripcion_alumno = Tipo_Subscripcion.objects.get(nombre = "Alumno")

    for icurso in cursos:



        curso = Curso.objects.get(id = icurso.id)
        centro = Centro.objects.get(id = curso.centro.id)

        if (request.user == centro.administrador):

            

            curso_item ={"courseID": icurso.id, "title": icurso.titulo, "description": icurso.descripcion, "status": icurso.estado,"center": icurso.centro.id,'subscribers':{'teachers':[]}}      
            profesor_curso = Usuario_Curso.objects.filter( curso = icurso, tipo_subscripcion = subscripcion_profesor).all()

            print(profesor_curso)
            if(not profesor_curso == None):   
                for profesor in profesor_curso: 
                    curso_item['subscribers']['teachers'].append({"UserID": profesor.usuario.id, "username": profesor.usuario.username, "email":profesor.usuario.email})

            content.append(curso_item)
        
        else:
            try:
                usuario_curso = Usuario_Curso.objects.get(usuario = request.user, curso_id = icurso.id)
            except:
                continue


            curso_item ={"courseID": icurso.id, "title": icurso.titulo, "description": icurso.descripcion, "status": icurso.estado,"center": icurso.centro.id,'subscribers':{'teachers':[]}}      
            profesor_curso = Usuario_Curso.objects.filter( curso = icurso, tipo_subscripcion = subscripcion_profesor).all()

            print(profesor_curso)
            if(not profesor_curso == None):   
                for profesor in profesor_curso: 
                    curso_item['subscribers']['teachers'].append({"UserID": profesor.usuario.id, "username": profesor.usuario.username, "email":profesor.usuario.email})

            content.append(curso_item)

        
            
    return Response({
        "status" : 'OK',
        "course_list": content
        })
    
    ##except:
        #return Response({
         #   "status" : 'ERROR',
          #  "message": 'session_token is required'
           # })


#Api de deslogueo
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_usuario(request):

    request.user.auth_token.delete()
    
    content = {
        'status': 'OK',
        'message': 'Sesión cerrada.',
    }
    return Response(content)

@login_required
def usuario(request, id_usuario):
    if (request.method=='GET'):

        #proteccion: ser su profe, su admin, el usuario o el super
        subscripcion_profesor = Tipo_Subscripcion.objects.filter(nombre = "Profesor")
        subscripcion_alumno = Tipo_Subscripcion.objects.filter(nombre = "Alumno")
        cursos_alumno = Usuario_Curso.objects.filter(usuario = id_usuario, tipo_subscripcion__in = subscripcion_alumno).values('curso')
        cursos_profe = Usuario_Curso.objects.filter(usuario = request.user.id, tipo_subscripcion__in = subscripcion_profesor).values('curso')
        cursos_admin = Curso.objects.filter(centro__in = Centro.objects.filter(administrador = request.user.id)).values('id')
        cursos_con_profesor = Usuario_Curso.objects.filter(curso__in = cursos_alumno).filter(curso__in = cursos_profe)
        cursos_con_admin = Usuario_Curso.objects.filter(curso__in = cursos_alumno).filter(curso__in = cursos_admin)

        if (len(cursos_con_profesor) == 0 and len(cursos_con_admin) == 0 and not request.user.id == id_usuario and not request.user.is_superuser):
            raise PermissionDenied()     
        #fin proteccion   

        usuario = Usuario.objects.filter(id = id_usuario).values()

        if (len(usuario) == 0):
            raise Http404()
        
        return JsonResponse({
            'data': list(usuario)
        })


@login_required
def cursos(request, id_centro):
    if (request.method=='GET'):
        cursos = Curso.objects.filter(centro = id_centro).values()

        if (len(cursos) == 0):
            raise Http404()

        return JsonResponse({
            'data': list(cursos)
        })

@login_required
def curso(request, id_curso):
    if (request.method=='GET'):
        curso = Curso.objects.filter(id = id_curso).values()

        if (len(curso) == 0):
            raise Http404()

        return JsonResponse({
            'data': list(curso) 
        })

@login_required
def tareas(request, id_curso):
    if (request.method=='GET'):

        #proteccion: estar subscrito al curso, ser el admin del centro, o ser el super
        subscripcion = Usuario_Curso.objects.filter(usuario = request.user.id, curso = id_curso)
        admin_curso = Curso.objects.filter(centro__in = Centro.objects.filter(administrador = request.user.id), id = id_curso)

        if (len(subscripcion) == 0 and len(admin_curso) == 0 and not request.user.is_superuser):
            raise PermissionDenied()     
        #fin proteccion   

        tareas = Tarea.objects.filter(curso = id_curso).values()

        if (len(tareas) == 0):
            raise Http404()

        return JsonResponse({
            'data': list(tareas)
        })

@login_required
def tarea(request, id_tarea):
    if (request.method=='GET'):
        
        #proteccion: estar subscrito al curso, ser el admin del centro, o ser el super
        curso = Curso.objects.get(id = Tarea.objects.get(id = id_tarea).curso.id)
        subscripcion = Usuario_Curso.objects.filter(usuario = request.user.id, curso = curso.id)
        admin_curso = Curso.objects.filter(centro__in = Centro.objects.filter(administrador = request.user.id), id = curso.id)

        if (len(subscripcion) == 0 and len(admin_curso) == 0 and not request.user.is_superuser):
            raise PermissionDenied()     
        #fin proteccion
        
        tarea = Tarea.objects.filter(id = id_tarea).values()

        if (len(tarea) == 0):
            raise Http404()

        return JsonResponse({
            'data': list(tarea) 
        })

@login_required
def entregas(request, id_tarea):
    if (request.method=='GET'):

        alumno = Usuario.objects.get(id = request.GET.get("alumno"))

        #proteccion: ser profesor del curso, el alumno, el admin del centro o el super
        curso = Curso.objects.get(id = Tarea.objects.get(id = id_tarea).curso.id)
        profesor = Usuario_Curso.objects.filter(usuario = request.user.id, curso = curso.id, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))
        admin = Curso.objects.filter(centro__in = Centro.objects.filter(administrador = request.user.id), id = curso.id)

        if (len(profesor) == 0 and not alumno == request.user and len(admin) == 0 and not request.user.is_superuser):
            raise PermissionDenied()
        #fin proteccion

        entregas = Entrega.objects.filter(tarea = id_tarea, autor = alumno).values()
        for entrega in entregas:
            auto_puntuacion = model_to_dict(Auto_Puntuacion.objects.get(id = entrega['auto_puntuacion_id']))
            entrega['auto_puntuacion'] = auto_puntuacion

        return JsonResponse({
            'data': list(entregas)
        })

@login_required
@csrf_exempt
def entrega(request, id_entrega):
    if (request.method=='GET'):
        

        #proteccion: ser profesor del curso, ser el admin del centro, ser el autor de la entrega o ser el super
        entrega = Entrega.objects.get(id = id_entrega)
        curso = Curso.objects.get(id = Tarea.objects.get(id = entrega.tarea.id).curso.id)
        profesor = Usuario_Curso.objects.filter(usuario = request.user.id, curso = curso.id, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))
        admin = Curso.objects.filter(centro__in = Centro.objects.filter(administrador = request.user.id), id = curso.id)

        if (len(profesor) == 0 and len(admin) == 0 and not entrega.autor == request.user.id and not request.user.is_superuser):
            raise PermissionDenied()
        #fin proteccion

        entrega = Entrega.objects.filter(id = id_entrega).values()

        if (len(entrega) == 0):
            raise Http404()

        return JsonResponse({
            'data': list(entrega) 
        })


@csrf_exempt
@login_required
def entrega_alumno(request, tarea_id):
    if (request.method=='POST'):
        try:
            #proteccion: ser alumno en el curso del tarea o ser el super
            tarea = Tarea.objects.get(id = tarea_id)
            curso = tarea.curso
            try:
                alumno = Usuario_Curso.objects.get(usuario = request.user.id, curso = curso.id, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Alumno"))
            except:
                raise PermissionDenied()
            #fin proteccion

            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            comentario = str(body['comentario'])
            entrega_id = body['entrega_id']

            entrega = Entrega.objects.get(id = entrega_id)
            entrega.comentario_alumno = comentario
            entrega.save()
            return JsonResponse({"msg": "Comentario guardado", "tipo": "success"})
        except:
            return JsonResponse({"msg": "Error al guardar el comentario", "tipo": "warning"})


    


@login_required
def usuario_cursos(request, id_usuario):
    if (request.method=='GET'):

        #proteccion: es el usuario, es el super
        if (not request.user.id == id_usuario and not request.user.is_superuser):
            raise PermissionDenied()
        #fin proteccion

        cursos_id =  list(Usuario_Curso.objects.filter(usuario = id_usuario).values_list('curso', flat=True))
        cursos = Curso.objects.filter(id__in = cursos_id).values()

        for curso in cursos:
            if (not len(Usuario_Curso.objects.filter(usuario = id_usuario, curso = curso["id"], tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))) == 0):
                curso["rol"] =  "Profesor"
            else:
                curso["rol"] = "Alumno"

            print(len(Usuario_Curso.objects.filter(usuario = id_usuario, curso = curso["id"], tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))))

            

        if (len(cursos) == 0):
            raise Http404()

        return JsonResponse({
            'data': list(cursos)
        })

@login_required
def calificaciones(request, id_tarea):
    if (request.method=='GET'):

        #proteccion: ser profesor del curso del tarea o ser el super
        tarea = Tarea.objects.get(id = id_tarea)
        curso = tarea.curso
        profesor = Usuario_Curso.objects.filter(usuario = request.user.id, curso = curso.id, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))
        
        if len(profesor) == 0 and not request.user.is_superuser:
            raise PermissionDenied()
        #fin proteccion

        calificaciones = Calificacion.objects.filter(tarea = id_tarea).values()

        return JsonResponse({
            'data': list(calificaciones)
        })

import traceback

@csrf_exempt
@login_required
def calificacion(request, id_tarea):
    if (request.method=='POST'):
        try:

            #proteccion: ser profesor del curso del tarea o ser el super
            tarea = Tarea.objects.get(id = id_tarea)
            curso = tarea.curso
            profesor = Usuario_Curso.objects.filter(usuario = request.user.id, curso = curso.id, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))
            
            if len(profesor) == 0 and not request.user.is_superuser:
                raise PermissionDenied()
            #fin proteccion

            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            if (float(body['nota']) > tarea.nota_maxima):
                return JsonResponse({"msg": "La nota no puede ser mayor que la nota máxima", "tipo": "warning"})
            elif (float(body['nota']) < 0):
                return JsonResponse({"msg": "La nota no puede ser menor que 0", "tipo": "warning"})

            nueva = True

            try:
                calificacion = Calificacion.objects.get(tarea = tarea.id, alumno = Usuario.objects.get(id = body['alumno'])).delete()
                nueva = False
            except:
                pass
            
            calificacion = Calificacion.objects.create(tarea = tarea, alumno = Usuario.objects.get(id = body['alumno']), nota = body['nota'], comentario = body['comentario'], fecha_calificacion = timezone.now(),  profesor = request.user)

            if (nueva):
                return JsonResponse({"msg": "Calificacion creada", "tipo": "success"})
            else:
                return JsonResponse({"msg": "Calificacion actualizada", "tipo": "success"})

        except:
            traceback.print_exc()
            return JsonResponse({"msg": "Algo ha ido mal", "tipo": "danger"})
    
    elif (request.method=='GET'):

        #proteccion: ser profesor del curso de la tarea o ser el super
        tarea = Tarea.objects.get(id = id_tarea)
        curso = tarea.curso
        profesor = Usuario_Curso.objects.filter(usuario = request.user.id, curso = curso.id, tipo_subscripcion = Tipo_Subscripcion.objects.get(nombre = "Profesor"))
        
        if len(profesor) == 0 and not request.user.is_superuser:
            raise PermissionDenied()
        #fin proteccion

        try:
            alumno = Usuario.objects.get(id = request.GET.get('alumno'))
            calificacion = model_to_dict(Calificacion.objects.get(tarea = tarea, alumno = alumno))
            profesor = model_to_dict(Usuario.objects.get(id = calificacion['profesor']))
            calificacion['profesor'] = profesor["first_name"] + " " + profesor["last_name"]
        except:
            traceback.print_exc()
            calificacion = False

        return JsonResponse({
            'data': calificacion
        })