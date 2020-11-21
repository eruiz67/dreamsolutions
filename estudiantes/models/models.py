# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
from odoo.modules.module import get_module_resource
import base64
import re
from odoo.exceptions import ValidationError
from lxml import etree
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

# class estudiantes(models.Model):
#     _name = 'estudiantes.estudiantes'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class Estudiante(models.Model):
    _name = 'estudiantes.student'
    _description = 'Maneja la informacion de los estudiantes'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Nombre', required=True)
    identification = fields.Char(string='Carnet de Identidad', required =True, copy=False)
    _sql_constraints = [
        ('identification_unique',
         'UNIQUE(identification)',
         "Ya existe un estudiante con el mismo carnet de identidad"),
         ('cedula_check_lenght', 'check (LENGTH(identification) = 11)',
         "El carnet de identidad debe contener 11 números"),  
    ]
    gender = fields.Selection([
        ('male', 'Hombre'),
        ('female','Mujer')
    ], string='Genero', required=True, default='male')
    date_birthday = fields.Date(string='Fecha de nacimiento', required=True)
    email = fields.Char(string='Correo electrónico')
    phone = fields.Char(string='Celular')


    @api.constrains('date_birthday')
    def _constrains_birthday(self):
        for record in self:
            if record.date_birthday and record.date_birthday > fields.Date.today():
                raise ValidationError("La fecha de nacimiento debe ser anterior a la fecha actual")

    @api.constrains('email')
    def _check_email (self):
        # otra podria ser "[^@]+@[^@]+\.[^@]+"
        for record in self:
             if record.email and not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[a-zA-Z]$)", record.email):                
	             raise ValidationError("Debe seleccionar una dirección de correo válida")
    

    age = fields.Integer(compute='_compute_age', string='Edad')
    
    @api.one
    @api.depends('date_birthday')
    def _compute_age(self):
        for record in self:
            if record.date_birthday:    
                today = fields.Date.today()
                offset = int(self.date_birthday.replace(year=today.year) > today)  # int(True) == 1, int(False) == 0
                record.age = today.year - self.date_birthday.year - offset  
    
    subject_mark_ids = fields.One2many('estudiantes.student_subject_mark', 'student_id', string='Notas')

    qty_subject_mark = fields.Integer(compute='_compute_qty_subject_mark', string='Cantidad de evaluaciones')
    
    @api.multi
    @api.depends('subject_mark_ids')
    def _compute_qty_subject_mark(self):
        for record in self:
            record.qty_subject_mark = len(record.subject_mark_ids)
    
    avg_mark = fields.Float(compute='_compute_avg_mark', string='Nota promedio', digits=(3,2), store=True)
    
    @api.depends('subject_mark_ids')
    def _compute_avg_mark(self):
        for record in self:
            marks=0
            if len(record.subject_mark_ids)>0:
                for mark in record.subject_mark_ids:
                    marks = marks + mark.mark
            record.avg_mark = marks /len(record.subject_mark_ids) if len(record.subject_mark_ids)>0 else 0

    image = fields.Binary(
        "Foto",
        attachment=True,
        help=
        "Campo para la foto del estudiante, dimensión máxima 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True)
    image_small = fields.Binary("Small-sized photo", attachment=True)

    skill_ids = fields.Many2many('estudiantes.skill', string='Habilidades')

    group_ids = fields.Many2many('estudiantes.group', string='Grupos')
    @api.model
    def _get_default_image(self):
        image_path = get_module_resource('estudiantes',
                                         'static/src/img', 'default_image.png')
        with open(image_path, 'rb') as f:
            image = f.read()
        if image:
            image = tools.image_colorize(image)
        return tools.image_resize_image_big(
            base64.b64encode(image))

    @api.model
    def create(self, vals):
        if not vals.get('image'):
            vals['image'] = self._get_default_image()
        tools.image_resize_images(vals)
        return super(Estudiante, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        if not vals.get('image'):
            vals['image'] = self._get_default_image()
        """
        tools.image_resize_images(vals)
        res = super(Estudiante, self).write(vals)
        return res  

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Estudiante, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='date_birthday']"):
                node.set('options', "{'datepicker': {'maxDate': '%sT23:59:59'}}" % fields.Date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
            res['arch'] = etree.tostring(doc)
        return res  


class Subject(models.Model):
    _name = 'estudiantes.subject'
    _description = 'Permite la gestion de asignaturas'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripcion')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "No pueden existir dos asignaturas con el mismo nombre"),
    ]

class StudentSubjectMark(models.Model):
    _name = 'estudiantes.student_subject_mark'
    _description = 'Permite gestionar la nota de los estudiantes para cada asignatura'

    student_id = fields.Many2one('estudiantes.student', string='Estudiante')
    subject_id = fields.Many2one('estudiantes.subject', string='Asignatura', required=True)
                                
    mark = fields.Integer(string='Nota', required=True, size=1)
    
    _sql_constraints = [
        ('mark_check_gte2',
         'CHECK(mark >=2)',
         "La nota de una asignatura debe ser un valor entre 2 y 5"),
        ('mark_check_lte5',
         'CHECK(mark <=5)',
         "La nota de una asignatura debe ser un valor entre 2 y 5"),
    ]
    
class Skill(models.Model):
    _name = 'estudiantes.skill'
    _description = 'Lista las habilidades del estudiante'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripcion')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "No pueden existir dos habilidades con exactamente el mismo nombre"),
    ]   


class Groups(models.Model):
    _name = 'estudiantes.group'
    _description = 'Permite manejar los grupos a los que pertenecen los estudiantes'

    name = fields.Char(string='Grupo', required=True)
    description = fields.Char(string='Descripción')
    year = fields.Selection([
        ('1', '1ro'),
        ('2', '2do'),
        ('3', '3ro'),
        ('4', '4to'),
        ('5', '5to'),
        ('mixto', 'mixto')

    ], string='Año')

    manager_id = fields.Many2one('estudiantes.student',string='Responsable', domain="[('id','in',student_ids)]", help="El responsable se selecciona de entre los integrales actuales del grupo")
    student_ids = fields.Many2many('estudiantes.student', string='Estudiantes')

    qty_student = fields.Integer(compute='_compute_qty_student', string='Cantidad integrantes', store=True)
    
    @api.depends('student_ids')
    def _compute_qty_student(self):
        for rec in self:
            rec.qty_student = len(rec.student_ids)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "No pueden existir dos grupos con el mismo nombre"),
    ]

    @api.onchange('student_ids')
    def _onchange_student_ids(self):
            encontrado = False
            if self.manager_id.id:
                for member in self.student_ids:
                    if self.manager_id == member:
                        encontrado=True
                if not encontrado:
                    self.manager_id = False

    
    """
    date_birthday = fields.Date(string='Fecha de nacimiento')

    age = fields.Char(compute='_compute_age', string='Edad')
    
    @api.one
    @api.depends('date_birthday')
    def _compute_age(self):
        for record in self:
            if record.date_birthday:    
                today = fields.Date.today()
                offset = int(self.date_birthday.replace(year=today.year) > today)  # int(True) == 1, int(False) == 0
                record.age = today.year - self.date_birthday.year - offset  
    """

"""
class Subject(models.Model):
    _name = 'ej_estudiantes.subject'
    _description = 'Permite el manejo de las asignaturas'

    name = fields.Char(string='Asignatura')

class SubjectStudent(models.Model):
    _name = 'ej_estudiantes.student_subject'
    _description = 'Permite guardar la nota del estudiante para una asignatura en especifico'


    student = fields.Many2one('ej_estudiantes.student', string='Estudiante')
    subject = fields.Many2one('ej_estudiantes.subject', string='Asignatura', required=True)
    score = fields.Integer(string='Nota', size=2)

"""
    

    