# Techzenith
Benjamin Villouta
Historia de usuario: Ver asignaturas

Descripción
Editar Descripción
Como usuario de la plataforma con el rol de estudiante o profesor, quiero tener acceso a la asignatura en la que estoy registrado, para poder acceder al contenido de la misma dependiendo de mi rol como usuario.

 

Criterios de aceptación:

1.Escenario: Un alumno ingresa a la asignatura.

Dado que el usuario cuenta con rol de alumno y se encuentra registrado en la asignatura, cuando ingrese a la misma, entonces debería poder acceder al material subido por el profesor, las evaluaciones y sus calificaciones.

2.Escenario: Un profesor ingresa a su asignatura.

Dado que el usuario es el profesor que dicta la asignatura, cuando ingrese a la misma, entonces debería poder acceder y gestionar el contenido y las evaluaciones, así como gestionar las calificaciones (de la asignatura) de los alumnos registrados.

3.Escenario: Acceso a la asignatura con usuario no autorizado.

Dado que el usuario intenta acceder a una asignatura en la que no se encuentra registrado, cuando el usuario intenta ingresar a la asignatura, entonces el sistema mostrará un mensaje indicando que el usuario no se encuentra autorizado para acceder a la asignatura.

4.Escenario: Acceso a la asignatura con usuario no autenticado.

Dado que el usuario intenta acceder a una asignatura sin haber iniciado sesión en la plataforma, cuando intente acceder a la asignatura, entonces el sistema redirigirá al usuario a la página de inicio de sesión y mostrará un mensaje de error solicitando autenticación.