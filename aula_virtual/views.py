from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Usuario, RegistroAsignatura, Asignatura, Token
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
import json
import secrets
import string
import uuid

def generar_contrasena(longitud):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contrasena = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    return contrasena

def obtener_usuarios(request):
    grupo_nombre = request.GET.get('rol', '')
    
    if grupo_nombre:
        try:
            grupo_apoderado = Group.objects.get(name=grupo_nombre)
            usuarios = list(Usuario.objects.filter(groups=grupo_apoderado).values('username', 'first_name', 'last_name'))
        except Group.DoesNotExist:
            usuarios = []  # En caso de que el grupo no exista, retornar una lista vacía
    else:
        usuarios = list(Usuario.objects.all().values('username', 'first_name', 'last_name'))
    
    return JsonResponse(usuarios, safe=False)

def obtener_usuario(request):
    nombre_usuario = request.GET.get('username', '')
    try:
        usuario = Usuario.objects.get(username=nombre_usuario)
        
        # Verificar pertenencia a grupos
        grupo_alumnos = Group.objects.get(name='Alumnos')
        grupo_profesores = Group.objects.get(name='Profesores')
        grupo_apoderados = Group.objects.get(name='Apoderados')
        
        usuario_data = {
            'username': usuario.username,
            'email': usuario.email,
            'tutor': usuario.tutor.username if usuario.tutor else None,
            'is_alumno': usuario.groups.filter(name='Alumnos').exists(),
            'is_profesor': usuario.groups.filter(name='Profesores').exists(),
            'is_apoderado': usuario.groups.filter(name='Apoderados').exists(),
        }
    except Usuario.DoesNotExist:
        usuario_data = {'error': 'Usuario no encontrado'}
    
    return JsonResponse(usuario_data, safe=False)


def index(request):
    #if request.user.is_authenticated:
    #    return redirect('home')
     
    data = {}
    data["titulo_de_pagina"] = "Inicio - Aula virtual"
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        recordarme = request.POST.get('recordarme') == 'on'

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not recordarme:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(None)  # Usa la duración predeterminada de la sesión
            messages.success(request, "Usuario autenticado")
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrecta.")

    return render(request, "aula_virtual/index.html", data)

@login_required
def nuevo_usuario(request):
    usuario_autenticado = request.user
    if usuario_autenticado.is_superuser == False:
        return render(request, 'aula_virtual/usuario-sin-permiso.html', {})
    flag_crear_usuario = False
    if request.method == 'POST':
        username = request.POST.get('username-registro', '')
        email = request.POST.get('email-registro', '')
        password = generar_contrasena(15)
        is_active = False
        is_staff = False
        is_superuser = False
        is_profesor = request.POST.get('isProfesor-registro', False) == 'on'
        is_alumno = request.POST.get('isAlumno-registro', False) == 'on'
        is_apoderado = request.POST.get('isApoderado-registro', False) == 'on'
        tutor_id = request.POST.get('tutor-asociado', '')

        try:
            # Intenta obtener el usuario existente
            usuario_nuevo = Usuario.objects.get(username=username)
            usuario_nuevo.email = email
            usuario_nuevo.set_password(password)  # Actualiza la contraseña si es necesario
            usuario_nuevo.is_active = is_active
            usuario_nuevo.is_staff = is_staff
            usuario_nuevo.is_superuser = is_superuser
        except Usuario.DoesNotExist:
            # Si el usuario no existe, créalo
            flag_crear_usuario = True
            usuario_nuevo = Usuario.objects.create(
                username=username,
                email=email,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            usuario_nuevo.set_password(password)

        # Guardar cambios en el usuario
        usuario_nuevo.save()

        # Eliminar grupos anteriores
        usuario_nuevo.groups.clear()

        # Asignar el usuario al grupo correspondiente y realizar acciones específicas
        if is_alumno:
            grupo_alumnos = Group.objects.get(name='Alumnos')
            usuario_nuevo.groups.add(grupo_alumnos)
            if tutor_id:
                try:
                    tutor = Usuario.objects.get(username=tutor_id)
                    usuario_nuevo.tutor = tutor
                    usuario_nuevo.save()
                    print(f'Este usuario se registrará como Alumno y su tutor es {tutor}')
                except Usuario.DoesNotExist:
                    print(f'Tutor con username {tutor_id} no encontrado.')

        if is_apoderado:
            grupo_apoderados = Group.objects.get(name='Apoderados')
            usuario_nuevo.groups.add(grupo_apoderados)
            print("Usuario es apoderado")
        
        if is_profesor:
            grupo_profesores = Group.objects.get(name='Profesores')
            usuario_nuevo.groups.add(grupo_profesores)
            print("Usuario es profesor")

# -------------------------------------------------------------------
    if flag_crear_usuario:
        token_autenticacion = uuid.uuid4()
        dead_time = timezone.now() + timezone.timedelta(days=7); # 7 Token valido por 7 dias
        nuevo_token = Token.objects.create(
            token_autenticacion = token_autenticacion,
            dead_time = dead_time,
            ID_usuario = usuario_nuevo,
        )

        nuevo_token.save();
    
        subject = 'Termina de configurar tu cuenta en Aula virutal TechZenith'
        message = f'Por favor, haz clic en el siguiente enlace para terminar de configurar tu cuenta: http://127.0.0.1:8000/configuracion-cuenta/{nuevo_token.token_autenticacion}/'
        from_email = 'saad11012002@gmail.com'
        recipient_list = [usuario_nuevo.email]
        send_mail(subject, message, from_email, recipient_list)
    
    return render(request, 'aula_virtual/new-user.html', {})

def configuracion_cuenta(request, token):
    try:
        token_obj = Token.objects.get(token_autenticacion = token)
        
        # Verificar si el token ha expirado
        if token_obj.is_expired():
            return render(request, 'aula_virtual/configurar-cuenta.html', {
                "expiro": True
            })
        
        usuario = token_obj.ID_usuario
        data = {"ok": True}
        
    except Token.DoesNotExist:
        return render(request, 'aula_virtual/configurar-cuenta.html', {
            "no_existe": True
        })

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first-name', '')
        usuario.last_name = request.POST.get('last-name', '')
        usuario.set_password(request.POST.get('password', ''))
        usuario.is_active = True
        usuario.save()
        token_obj.delete()
        data['ok'] = False
        data['exito'] = True

    return render(request, 'aula_virtual/configurar-cuenta.html', data)

@login_required
def mis_asignaturas(request):
    usuario = request.user
    registros = RegistroAsignatura.objects.filter(usuario = usuario)
    asignaturas = [registro.asignatura for registro in registros]
    return render(request, 'aula_virtual/asignaturas.html',{'asignaturas': asignaturas})

