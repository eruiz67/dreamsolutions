#dreamsolutions - Ernesto Ruiz

        Este módulo permite em manejo de estudiantes y las notas de sus asignaturas.
        Para cada estudiantes se maneja un conjunto de datos, incluido sus asignaturas con sus respectivas notas.
        - Se han realizado comprobaciones en los campos para garantizar la consistencia de datos tales como:
            - El nombre solo debe contener letras
            - El carnet solo debe contener numeros
            - La fecha de nacimiento no debe ser posterior a la fecha actual (se han desabilitado los dias posteriores en el widget)
            - Debe poseer un email valido
            - El carnet de identidad debe ser unico y poseer una longitud de 11 numeros
        - Se han implementado filtros de búsqueda
        - Se han implementado 2 vistas para los estudiantes: kanban, lista y formulario
        - Se han implementado dos reportes
                - Listado de estudiantes (disponible solamente desde la vista lista "tree"), permite obtener un listado con los datos fundamentales de los estudiantes
                - Ficha de estudiante (disponible en las vistas de lista y formulario), permite obtener datos mas detallados de los estudiantes
        - Se ha implementado la gestion de grupos, los estudiantes pertenecen a grupos, cada grupo podra contar con varios estudiantes y se podra seleccionar un responsable de entre sus integrantes.
        - Se han implementado filtros de busqueda tanto para estudiantes como para grupos