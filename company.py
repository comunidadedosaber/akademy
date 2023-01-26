from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.pyson import Eval, If, Not, Bool
from trytond.pool import Pool, PoolMeta
from datetime import date, datetime
from trytond.transaction import Transaction
from .variables import sel_state_student

# extende o modulo company.employee adicionando alguns campos.

__all__ = ['Employee', 'CompanyStudent']
__metaclass__ = PoolMeta


class Employee(ModelSQL, ModelView):
    'Employee'
    __name__ = 'company.employee'
   
    employee = fields.Boolean(
        string=u'Funcionário', depends=['teacher'],
        states={
            'select': True, 
            'required': Bool(Eval('teacher'))
        }, help='A entidade será tratada como funcionário.')
    teacher = fields.Boolean(
        string=u'Docente', 
        states={
            'select': True
        }, help='A entidade será tratada como docente.')
    party = fields.Many2One(
        'party.party', 'Nome', 
        required=True, ondelete='CASCADE',
        help="Nome do discente.")
    school_chart = fields.One2Many(
        'akademy.school-chart', 'employee', 
        string=u'Função')
    classe_treacher = fields.One2Many(
        'akademy.classe-teacher', 'employee',
        string=u'Associar Turma')
    classes = fields.One2Many(
        'akademy.classes', 'coordenator_studyplan',
        string=u'Turma')

    @classmethod
    def default_start_date(cls):
        return datetime.now().date()

    @classmethod
    def default_employee(cls):
        return True
    

class CompanyStudent(ModelSQL, ModelView):
    'Student - Company'
    __name__ = 'company.student'
    #_rec_name = 'party'

    code = fields.Char(string=u'Nº de matrícula', size=20,
        help="Número de matrícula do discente.")
    start_date = fields.Date('Início',
        domain=[
            If(
                (Eval('start_date')) & (Eval('end_date')),
                ('start_date', '<=', Eval('end_date')),
                (),
            )
        ], depends=['end_date'],
        required=True, help="Início da formação.")
    end_date = fields.Date('Fim',
        domain=[
            If(
                (Eval('start_date')) & (Eval('end_date')),
                ('end_date', '>=', Eval('start_date')),
                (),
            )
        ], depends=['start_date'],
        help="Fim da formação.") 
    state = fields.Selection(
		selection=sel_state_student, string=u'Estado', 
		required=True, help="Escolha o estado da matrícula.")
    classe = fields.Many2One(
		model_name='akademy.classe', string=u'Classe', 
		help="Nome da classe.") 
    party = fields.Many2One(
        'party.party', 'Nome', 
        required=True, ondelete='CASCADE',
        #domain=([('is_person', '=', True)]),
        states={'is_person': True},
        help="Nome do discente.")
    company = fields.Many2One(
        'company.company', 'Instituição',
        required=True,
        help="Nome da instituição.")
    academiclevel = fields.Many2One(
        model_name='akademy.academic-level', string=u'Nível académico', 
        required=True)
    area = fields.Many2One(
        model_name='akademy.area', string=u'Área', 
        required=True, 
        domain=[
            ('academic_level', '=', Eval('academiclevel', -1))
        ], depends=['academiclevel'])
    course = fields.Many2One(
        model_name='akademy.course', string=u'Curso', 
        required=True, 
        domain=[
            ('area', '=', Eval('area', -1))
        ], depends=['area'])      
    student_transfer = fields.One2Many(
        'akademy.student-transfer', 'student', 
        string=u'Transferências')
    student = fields.One2Many(
        'akademy.classe-student', 'student',
        string=u'Marículas')
        
    @classmethod
    def default_start_date(cls):
        return date.today()

    def get_rec_name(self, name):
        return self.party.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('party.rec_name',) + tuple(clause[1:])]

    @classmethod
    def create_student(cls, student):
        Matriculation = Pool().get('company.student')
        StudentMatriculation = Matriculation(
            party = student,
            start_date = date.today()
            #end_date
            #company
        )
        StudentMatriculation.save()           
    
    @classmethod
    def __setup__(cls):
        super(CompanyStudent, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.party),
            u'Não foi possível cadastrar a nova entidade, por favor verifica se a entidade já existe')
        ]
        cls._order = [('party', 'ASC')]

