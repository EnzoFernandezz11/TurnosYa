# TurnosYA
#### Video Demo:  <[URL HERE](https://www.youtube.com/watch?v=AvxF66cxqm0)>
#### Description:
### General Description:

Este proyecto funciona como una turnera dirigida hacia clientes y proveedores de servicios.
Por una parte los proveedores de servicios pueden elegir mediante un formulario su comienzo y fin de semana laboral,
el horario y el intervalos de los turnos que ofrecen. Luego tiene una seccion de perfil donde puede visualizar estos
datos y ademas ingresar el rubro de su negocio y el nombre, dentro de aqui se encuentra una seccion que indica
"Enviar ingreso de turno" que cuando se lo presiona genera una tabla dentro de la base de datos(si no existe)
que contiene todos los turnos de los dias,horas,intervalo elegido anteriormente por el mes actual.
Como cliente dentro de turnos("Enviar ingreso de turno") podremos ingresar nuestros datos y elegir un turno un dia
especifico con una cierta hora, estos estan realcionados con la base de datos creada anteriormente, y tambien cuenta
con verificacioens para saber si ese turno es valido.
Luego que el clietne ingrese el turno, el proveedor de servicios podra visualizar el turno y admeas tendra una
seccion donde podra ver todos los clientes que le solicitaron turno

### Technologies Used:

**Programming:** Python, with Flask and SQL libraries provided by CS50.
**Web Development:** HTML, CSS, JavaScript, Bootstrap5.

## Application Routes

### **Horarios** (Schedules)

In this route, the service provider can choose their working days, hours, and the interval for appointments. The process involves:

1. Obtaining data from the form.
2. Verifying that it is not blank.
3. Ensuring that the interval count aligns with the specified hours.
4. Storing the information in the schedules table.

### **Perfil** (Profile)

In this route, we utilize data stored in our tables to display useful information. Additionally, it allows the user to select the business category and name. This route is crucial because it contains the button to send the form link to the client.

### **Turnos** (Appointments)

Probably the most complex and critical route in this web app. Here:

1. We extract data from the form submitted by the client and verify it.
2. Auxiliary functions created in `functions.py` also come into play.
3. If appointments are not yet created, we detect this and generate appointments in a table based on the chosen days, hours, and intervals specified by the service provider.
4. We then extract relevant information to limit the available days (preventing selection of days outside the range) and check if the appointment is already taken or not.

### **Ver_turnos** (View Appointments) and **Clientes** (Clients)

These routes display information related to the original tables.

