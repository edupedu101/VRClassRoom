# VRoom

Un lms para tareas de vr

## Descripcion

Una aplicación web que nos permite administrar, distribuir y evaluar actividades de formación VR y no VR programadas dentro de un proceso de enseñanza en línea

## Empezando

### Dependencias

Necesitaras [python3](https://www.python.org/) y pip instalados 

Una vez tengas python3 instalado haras los siguientes comandos:
- Para instalar los paquetes de python
```
pip install -r requirements.txt
```

- Para inicializar la base de datos:
```
python3 manage.py makemigrations
python3 manage.py migrate
```

- Para crear los grupos y modelos necesarios:
```
python3 manage.py initvroom
```
### Ejecutando el programa

```
python manage.py runserver
```

## Api

[Docuemtacion de la api](./DocumentationApi/documentacion.md)

## Ayuda

Para cualquier duda contactar con los autores

## Permisos

### Admin Centro
- Curso: añadir, borrar, modificar y ver.
- Documento: añadir, borrar, modificar y ver. 
- Tarea: añadir, borrar, modificar y ver.
- Auto puntuacion: añadir, borrar, modificar y ver.
- Entrega: añadir, borrar, modificar y ver.
- Invitacion: añadir, borrar, modificar y ver.
- Link: añadir, borrar, modificar y ver.
- Texto: añadir, borrar, modificar y ver.
- User: añadir, borrar, modificar y ver.
- Usuario curso: añadir, borrar, modificar y ver.

### Profesor
- Curso: modificar y ver
- Documento: añadir, borrar, modificar y ver. 
- Tarea: añadir, borrar, modificar y ver.
- Entrega: ver.
- Auto puntuacion: ver.
- Invitacion: añadir, borrar, modificar y ver.
- Link: añadir, borrar, modificar y ver.
- Texto: añadir, borrar, modificar y ver.
- Usuario curso: añadir, borrar, modificar y ver.

## Version History

* 0.1
    * Release inicial
* 0.2
* 0.3
* 1.0 Beta
    * First fully working app release

## Autores
  
[@EduValle](https://github.com/edupedu101/)
[@CarlosMuñoz](https://github.com/CarlosMunozRo/)
[@MartiLlorach](https://github.com/MartiLlorach/)

## Dedicaciones

A Antonio Calvo y a toda la clase de AWS2
