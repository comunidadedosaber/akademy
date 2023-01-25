from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pyson import Eval, Not, Bool
from datetime import date
from .varibles import sel_state, sel_modality, sel_course_yaer, sel_position

__all__ = [
        'LectiveYear', 'SchoolChart', 'Quarter', 'Area', 'Course', 'Classe', 'CourseClasse', 'AcademicLevel',
        'TimeCourse', 'MetricAvaliation', 'Avaliation', 'AvaliationType', 'Discipline',  
        'ApplicationCriteria', 'Phase', 'ClasseRoom',
        'StudyPlan', 'StudyPlanDiscipline', 'DisciplinePrecedents', 'StudyPlanAvaliation']


class LectiveYear(ModelSQL, ModelView):
    'Lective Year'
    __name__ ='akademy.lective-year'

    code = fields.Char(string=u'Código', size=20,
        help="Código do ano lectivo.\nEx: 22/23")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome do ano lectivo.")
    start = fields.Date(string=u'Início', required=True,          
        help="Data de início do ano lectivo.")
    end = fields.Date(string=u'Término', required=True, 
        help="Data de término do ano lectivo.")
    description = fields.Text(string=u'Descrição')
    application_criteria = fields.One2Many(
        'akademy.application-criteria', 'lective_year', 
        string=u'Critério de admissão')
    student_transfer = fields.One2Many(
        'akademy.student-transfer', 'lective_year', 
        string=u'Transferências')
    classes = fields.One2Many(
        'akademy.classes', 'lective_year',
        string=u'Turma')
    student_grades = fields.One2Many(
        'akademy.classe_student-grades', 'lective_year',
        string=u'Discente nota')
    classes_grades = fields.One2Many(
		'akademy.classes-grades', 'lective_year', 
		string=u'Avaliações') 
    applications = fields.One2Many(
		'akademy.applications', 'lective_year', 
		string=u'Candidaturas')
    historic_grades = fields.One2Many(
		'akademy.historic-grades', 'lective_year', 
		string=u'Percuso académico') 
    quarter = fields.One2Many(
		'akademy.quarter', 'lective_year', 
		string=u'Trimestre')
    phase = fields.One2Many(
		'akademy.phase', 'lective_year', 
		string=u'Fase de admissão')
    applications_result = fields.One2Many(
		'akademy.applications-result', 'lective_year', 
		string=u'Candidaturas resultado')
    school_chart = fields.One2Many(
		'akademy.school-chart', 'lective_year', 
		string=u'Organograma') 

    @classmethod
    def default_start(cls):
        return date.today()

    @classmethod
    def __setup__(cls):
        super(LectiveYear, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name),
            u'Não foi possível cadastrar o novo ano lectivo, por favor verifica se o nome inserido já existe.'),
            ('code', Unique(table, table.code),
            u'Não foi possível cadastrar o novo ano lectivo, por favor verifica se o código inserido já existe.'),
            ('start_date', Check(table, table.start < table.end),
            u'Não foi possível cadastrar o novo ano lectivo, por favor verifica se a data de início é menor que a data de término.')
        ]


class SchoolChart(ModelSQL, ModelView):
    'School Chart'
    __name__ = 'akademy.school-chart'

    school_position = fields.Selection(selection=sel_position, 
        string=u'Presença') 
    employee = fields.Many2One(
        model_name='company.employee', string=u'Nome', 
        required=True, ondelete='CASCADE', 
        help="Nome do funcionário.")
    lective_year = fields.Many2One(
		model_name="akademy.lective-year", string=u'Ano lectivo', 
		required=True, ondelete='CASCADE',
		help="Nome do ano lectivo.")
    academiclevel = fields.Many2One(
        model_name='akademy.academic-level', 
        string=u'Nível académico')     
    area = fields.Many2One(
        model_name='akademy.area', 
        string=u'Área', 
        #required=True, 
        domain=[
            ('academic_level', '=', Eval('academiclevel', -1))
        ], 
        depends=['academiclevel'])
    course = fields.Many2One(
        model_name='akademy.course', string=u'Curso', 
        domain=[('area', '=', Eval('area', -1))], 
        depends=['area'])
    course_classe = fields.Many2One(
        'akademy.course-classe', string=u'Classe', 
        domain=[('course', '=', Eval('course', -1))], 
        depends=['course'])

    @classmethod
    def __setup__(cls):
        super(SchoolChart, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('discipline',
            Unique(table, table.employee, table.school_position, table.lective_year),
            u'Não foi possível cadastrar a disciplina neste critério de transição de classe, por favor verifica se a disciplina selecionada já existe.'),            
        ]


class Quarter(ModelSQL, ModelView):
    'Quarter'
    __name__ = 'akademy.quarter'
    
    code = fields.Char(string=u'Código', size=20,
        help="Código do Trimestre.\nEx: Trimestre-1")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome do trimestre.")
    start = fields.Date(string=u'Início', required=True,          
        help="Data de início do trimestre.")
    end = fields.Date(string=u'Término', required=True, 
        help="Data de término do trimestre.")
    description = fields.Text(string=u'Descrição')
    lective_year = fields.Many2One(
		model_name="akademy.lective-year", string=u'Ano lectivo', 
		required=True, ondelete='CASCADE',
		help="Nome do ano lectivo.")
    studyplan_discipline = fields.One2Many(
		'akademy.studyplan-discipline', 'quarter', 
		string=u'Disciplina do plano de estudo')
    studyplan_avaliations = fields.One2Many(
		'akademy.studyplan-avaliation', 'quarter', 
		string=u'Avaliação do plano de estudo')
    classe_student_grades = fields.One2Many(
		'akademy.classe_student-grades', 'quarter', 
		string=u'Avaliação')
    classe_grades = fields.One2Many(
		'akademy.classes-grades', 'quarter', 
		string=u'Pauta')

    @classmethod
    def default_start(cls):
        return date.today()

    @classmethod
    def __setup__(cls):
        super(Quarter, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.lective_year),
            u'Não foi possível cadastrar o novo trimestre, por favor verifica se o nome inserido já existe.'),
            ('start_date', Check(table, table.start < table.end),
            u'Não foi possível cadastrar o novo trimestre, por favor verifica se a data de início é menor que a data de término.')
        ]


class Area(ModelSQL, ModelView):
    'Area'
    __name__ = 'akademy.area'    

    code = fields.Char(string=u'Código', size=20,
        help="Código da área.")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome da área.")
    description = fields.Text(string=u'Descrição')
    academic_level  = fields.Many2One(
        model_name='akademy.academic-level', 
        string=u'Nível académico') 
    application_criteria = fields.One2Many(
        'akademy.application-criteria', 'area', 
        string=u'Critério de admissão')
    studyplan = fields.One2Many(
        'akademy.studyplan', 'area', 
        string=u'Plano de estudo')
    course = fields.One2Many(
        'akademy.course', 'area', 
        string=u'Curso', required=True)   
    student_transfer = fields.One2Many(
        'akademy.student-transfer', 'area', 
        string=u'Transferências') 
    candidates = fields.One2Many(
        'akademy.candidates', 'area', 
        string=u'Canndidatos')
    applications = fields.One2Many(
        'akademy.applications', 'area', 
        string=u'Canndidaturas')
    company_student = fields.One2Many(
		'company.student', 'area', 
		string=u'Discente')  

    @classmethod
    def __setup__(cls):
        super(Area, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar a nova área, por favor verifica se o nome ou o código inserido já existe.')
        ]
        cls._order = [('name', 'ASC')]
 

class Course(ModelSQL, ModelView):
    'Course'    
    __name__ = 'akademy.course'
    _rec_name = 'name'

    code = fields.Char(string=u'Código', size=20,
        help="Codigo do curso.")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome do curso.")
    duration = fields.Selection(selection=sel_course_yaer,
        string=u'Duração', required=True,
        help="Escolha a duração do curso em anos.")
    description = fields.Text(string=u'Descrição')        
    area = fields.Many2One(model_name='akademy.area', 
        string=u'Área', ondelete='CASCADE')
    course_classe = fields.One2Many(
        'akademy.course-classe', 'course', 
        string=u'Classe', required=True)    
    application_criteria = fields.One2Many(
        'akademy.application-criteria', 'course', 
        string=u'Critério de admissão')
    studyplan = fields.One2Many(
        'akademy.studyplan', 'course', 
        string=u'Plano de estudo')    
    student_transfer = fields.One2Many(
        'akademy.student-transfer', 'course', 
        string=u'Transferências')
    candidates = fields.One2Many(
        'akademy.candidates', 'course', 
        string=u'Candidatos')
    applications = fields.One2Many(
        'akademy.applications', 'course', 
        string=u'Candidaturas')
    company_student = fields.One2Many(
		'company.student', 'area', 
		string=u'Discente') 

    @classmethod
    def __setup__(cls):
        super(Course, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar o novo curso, por favor verifica se o nome ou o código inserido já existe.')
        ]
        cls._order = [('name', 'ASC')]


class Classe(ModelSQL, ModelView):
    'Classe'
    __name__ = 'akademy.classe'

    code = fields.Char(string=u'Código', size=20,
        help="Código da classe.\nEx: Classe-7"
    )
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome da classe")
    description = fields.Text(string=u'Descrição')
    course_classe = fields.One2Many(
        'akademy.course-classe', 'classe',     
        string=u'Course')
    classes = fields.One2Many(
        'akademy.classes', 'classe',
        string=u'Turma')
    student = fields.One2Many(
		'company.student', 'classe', 
		string=u'Discente')

    @classmethod
    def __setup__(cls):
        super(Classe, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name),
            u'Não foi possível cadastrar a nova classe, por favor verifica se o nome inserido já existe.'),
            ('code', Unique(table, table.code),
            u'Não foi possível cadastrar a nova classe, por favor verifica se o código inserido já existe.')            
        ]
        cls._order = [
            ('name', 'ASC'),
        ]
    

class CourseClasse(ModelSQL, ModelView):
    'Course Classe'
    __name__ = 'akademy.course-classe'
    #_rec_name = 'classe'

    description = fields.Text(string=u'Descrição')
    course_year = fields.Selection(selection=sel_course_yaer,
        string=u'Ano', required=True,
        help="Escolha o ano do curso.")
    classe = fields.Many2One(
        model_name='akademy.classe', 
        string=u'Classe', required=True)
    course = fields.Many2One(
        model_name='akademy.course', 
        string=u'Course', required=True)
    studyplan = fields.One2Many(
        'akademy.studyplan', 'classe', 
        string=u'Plano de estudo')    
    student_transfer = fields.One2Many(
        'akademy.student-transfer', 'course_classe', 
        string=u'Transferências')
    student_transfer_discipline = fields.One2Many(
        'akademy.student_transfer-discipline', 'course_classe', 
        string=u'Transferência disciplina')
    applications = fields.One2Many(
        'akademy.applications', 'course_classe', 
        string=u'Candidaturas')  
    application_criteria = fields.One2Many(
        'akademy.application-criteria', 'course_classe', 
        string=u'Critérios de admissão')
    school_chart = fields.One2Many(
        'akademy.school-chart', 'course_classe', 
        string=u'Classe')

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.classe.rec_name)
        return t1  

    @classmethod
    def __setup__(cls):
        super(CourseClasse, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('classe', Unique(table, table.classe, table.course),
            u'Não foi possível associar a classe ao curso, por favor verifica se classe e o curso já não se encontram associados.')            
        ]


class AcademicLevel(ModelSQL, ModelView):
    'Academic Level'
    __name__ = 'akademy.academic-level'

    code = fields.Char( string=u'Código', size=20,
        help="Codio do nível académico.")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome do nível académico.")
    description = fields.Text(string=u'Descrição')
    area = fields.One2Many(
        'akademy.area', 'academic_level', 
        string=u'Área')
    application_criteria = fields.One2Many(
        'akademy.application-criteria', 'academic_level', 
        string=u'Critério de admissão')    
    studyplan = fields.One2Many(
        'akademy.studyplan', 'academic_level', 
        string=u'Plano de estudo')
    student_transfer = fields.One2Many(
        'akademy.student-transfer', 'academic_level', 
        string=u'Transferências')
    candidates = fields.One2Many(
        'akademy.candidates', 'academic_level', 
        string=u'Candidatos')
    applications = fields.One2Many(
        'akademy.applications', 'academic_level', 
        string=u'Candidaturas')
    student = fields.One2Many(
        'company.student', 'academic_level', 
        string=u'Disciplina')

    @classmethod
    def __setup__(cls):
        super(AcademicLevel, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar o novo nível académico, por favor verifica se o nome ou o código inserido já existe.')
        ]


class TimeCourse(ModelSQL, ModelView):
    'Time Course'
    __name__ = 'akademy.time-course'

    code = fields.Char(string=u'Código', size=20,
        help="Código do período.")
    name = fields.Char(string=u'Período', required=True, 
        help="Nome do período.")
    description = fields.Text(string=u'Descrição')        
    start_time = fields.Time(string=u'Entrada', format='%H:%M',
        required=True, help=u'Hora de início da aula.')
    end_time = fields.Time(string=u'Saída', format='%H:%M', 
        required=True, help=u'Hora de término da aula.')
    classes = fields.One2Many(
        'akademy.classes', 'time_course',
        string=u'Turma')

    @classmethod
    def __setup__(cls):
        super(TimeCourse, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar o novo período lectivo, por favor verifica se o nome ou o código inserido já existe.'),            
            ('start_time', Check(table, table.start_time < table.end_time),
            u'Não foi possível cadastrar o novo período lectivo, por favor verifica se a hora de entrada é menor que a hora de saída.')
        ]


class MetricAvaliation(ModelSQL, ModelView):
    'Metric Avaliation'
    __name__ = 'akademy.metric-avaliation'
 
    name = fields.Char(string=u'Nome', required=True,
        help="Nome da métrica que corresponde a avaliação.")    
    avaliation = fields.Many2One(
        model_name='akademy.avaliation', string=u'Avaliação', 
        required=True, ondelete='CASCADE')  
    avaliation_type = fields.Many2One(
        model_name='akademy.avaliation-type', string=u'Tipo de avaliação', 
        required=True, ondelete='CASCADE') 
    studyplan_avaliation = fields.One2Many(
        'akademy.studyplan-avaliation', 'metric_avaliation', 
        string=u'Plano de estudo avaliação'
    )

    @classmethod
    def __setup__(cls):
        super(MetricAvaliation, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.name),
            u'Não foi possível cadastrar a nova métrica, por favor verifica se o nome inserido já existe.')
        ]


class Avaliation(ModelSQL, ModelView):
    'Avaliation'
    __name__ = 'akademy.avaliation'
    
    name = fields.Char(string='Nome', required=True,
        help="Nome da avaliação.")
    description = fields.Text(string=u'Descrição')     
    metric_avaliation = fields.One2Many(
        'akademy.metric-avaliation', 'avaliation', 
        string=u'Avaliação')    

    @classmethod
    def __setup__(cls):
        super(Avaliation, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name),
            u'Não foi possível cadastrar a nova avaliação, por favor verifica se o nome inserido já existe para esta métrica.')
        ]
    
 
class AvaliationType(ModelSQL, ModelView):
    'Avaliation Type'
    __name__ = 'akademy.avaliation-type'
    
    name = fields.Char(string='Nome', required=True, 
        help="Nome do tipo de avaliação.")
    description = fields.Text(string=u'Descrição')      
    metric_avaliation = fields.One2Many(
        'akademy.metric-avaliation', 'avaliation_type', 
        string=u'Tipo de avaliação') 

    @classmethod
    def __setup__(cls):
        super(AvaliationType, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name),
            u'Não foi possível cadastrar o novo tipo de avaliação, por favor verifica se o nome inserido já existe para esta métrica.')
        ]


class Discipline(ModelSQL, ModelView):
    'Discipline'
    __name__ = 'akademy.discipline'

    code = fields.Char(string=u'Código', size=20,
        help="Código da disciplina.")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome da disciplina.")
    lesson_teoric = fields.Boolean(
        string=u'Teóricas',
        states={
            'required': Not(Bool(Eval('lesson_pratic')))
        }, depends=['lesson_pratic'], 
        help="A disciplina tem aulas teóricas.")
    lesson_pratic = fields.Boolean(
        string=u'Práticas',
        states={
            'required': Not(Bool(Eval('lesson_teoric')))
        }, depends=['lesson_teoric'],
        help="A disciplina tem aulas praticas.")
    description = fields.Text(string=u'Descrição')
    studyplan_discipline = fields.One2Many(
        'akademy.studyplan-discipline', 'discipline', 
        string=u'Disciplina do plano de estudo')
    discipline_precentes = fields.One2Many(
        'akademy.discipline-precentes', 'discipline', 
        string=u'Disciplina antecedentes')  
    student_transfer_discipline = fields.One2Many(
        'akademy.student_transfer-discipline', 'discipline', 
        string=u'Disciplina')    

    @classmethod
    def default_lesson_teoric(cls):
        return True

    @classmethod
    def __setup__(cls):
        super(Discipline, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('code', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar a nova disciplina, por favor verifica se o nome ou código inserido já existe.')
        ]
        cls._order = [('name', 'ASC')]


class Phase(ModelSQL, ModelView):
    'Phase'
    __name__ = 'akademy.phase'

    code = fields.Char(string=u'Código', size=20,
        help="Código do fase.")
    name = fields.Char(string=u'Nome', required=True, 
        help="Nome da fase de admissão.")
    start = fields.Date(string=u'Início', required=True,          
        help="Data de início do ano lectivo.")
    end = fields.Date(string=u'Término', required=True, 
        help="Data de término do ano lectivo.")
    lective_year = fields.Many2One(
        model_name='akademy.lective-year',string=u'Ano Lectivo', 
        required=True, ondelete='CASCADE')
    application_criteria = fields.One2Many(
        'akademy.application-criteria', 'phase', 
        string=u'Critério de admissão')
    applications = fields.One2Many(
        'akademy.applications', 'phase', 
        string=u'Candidaturas')
    application_result = fields.One2Many(
        'akademy.applications-result', 'phase', 
        string=u'Candidaturas')
    
    @classmethod
    def default_start(cls):
        return date.today() 

    @classmethod
    def __setup__(cls):
        super(Phase, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar a nova fase de admissão, por favor verifica se o nome ou código inserido já existe.'),
            ('start_date', Check(table, table.start < table.end),
            u'Não foi possível cadastrar o novo ano lectivo, por favor verifica se a data de início é menor que a data de término.')
        ]


class ClasseRoom(ModelSQL, ModelView):
    'Classe Room'
    __name__ = 'akademy.classe-room'

    code = fields.Char(string=u'Código', size=20,
        help="Código da sala de aula.")
    name = fields.Char(string=u'Nome', required=True,
        help="Nome da sala de aula")
    lesson_teoric = fields.Boolean(
        string=u'Teóricas',
        states={
            'required': Not(Bool(Eval('lesson_pratic')))
        }, depends=['lesson_pratic'],
        help="Sala para aulas teórica.")
    lesson_pratic = fields.Boolean(
        string=u'Práticas',
        states={
            'required': Not(Bool(Eval('lesson_teoric')))
        },  depends=['lesson_teoric'],
        help="Sala para aulas práticas.")
    capacity = fields.Integer(string=u'Capacidade',
        help="Capacidade maxima da sala de aula.")
    description = fields.Text(string=u'Descrição')

    @classmethod
    def default_lesson_teoric(cls):
        return True

    @classmethod
    def __setup__(cls):
        super(ClasseRoom, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name),
            u'Não foi possível cadastrar a nova sala de aula, por favor verifica se o nome inserido já existe.'),
            ('capacity', Check(table, table.capacity > 0),
            u'Não foi possível cadastrar a nova sala de aula, por favor verifica se a capacidade.')            
        ] 
        cls._order = [('name', 'ASC')]   


class ApplicationCriteria(ModelSQL, ModelView):
    'Application Criteria'
    __name__ = 'akademy.application-criteria'
    
    code = fields.Char(string=u'Código', size=20,
        help="Código do critério de admissão.")
    name = fields.Char(string=u'Nome', required=True,
        help="Nome do critéio de admissão.")
    description = fields.Text(string=u'Descrição')
    age = fields.Integer(string=u'Idade', required=True, 
        help=u'Informe a idade maxima para admissão.')
    average = fields.Numeric(string=u'Média', digits=(2,1), 
        required=True, 
        help=u'Informe a média mínima para admissão.')
    student_limit = fields.Integer(string=u'Total de vagas', required=True, 
        help=u'Informe o limite de discentes por admitir.')
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo', 
        required=True)
    academic_level = fields.Many2One(
        model_name='akademy.academic-level', string=u'Nível académico', 
        required=True)
    area = fields.Many2One(
        model_name='akademy.area', string=u'Área', 
        required=True, domain=[('academic_level', '=', Eval('academic_level', -1))],
        depends=['academic_level'])    
    course = fields.Many2One(
        model_name='akademy.course', string=u'Curso', 
        required=True, domain=[('area', '=', Eval('area', -1))],
        depends=['area'])
    course_classe = fields.Many2One(
		model_name='akademy.course-classe', string=u'Classe', 
		required=True, domain=[('course', '=', Eval('course', -1))],
		depends=['course'], help="Nome da classe.")
    phase = fields.Many2One(
        model_name='akademy.phase', string=u'Fase',
        required=True)
    application_result = fields.One2Many(
        'akademy.applications-result', 'application_criteria', 
        string=u'Candidaturas')

    @classmethod
    def __setup__(cls):
        super(ApplicationCriteria, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('name', Unique(table, table.name, table.course, table.lective_year),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verifica se já existe um critério de admissão com este nome, para este curso e ano lectivo.'),
            ('age', Check(table, table.age >= 5),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verifica se a idade inserida.'),
            ('min_average', Check(table, table.average >= 10),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verifica se a média esta abaixo de 10 valores.'),
            ('max_average', Check(table, table.average <= 20),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verifica se a média esta acima de 20 valores.'),
            ('student', Check(table, table.student_limit > 0),
            u'Não foi possível cadastrar o novo critério de admissão, por favor verifica o limite de vagas disponivés.'),
        ]    
    

class StudyPlan(ModelSQL, ModelView):
    'StudyPlan'
    __name__ = 'akademy.studyplan'
    
    code = fields.Char(string=u'Código', size=25,
        help="Código do plano de estudo.")    
    name = fields.Char(string=u'Nome', required=True,
        help="Nnome do plano de estudo.")
    hours = fields.Integer(string=u'Total de horas', required=True,
        help="Informe a carga horária.")    
    academic_level = fields.Many2One(
        model_name='akademy.academic-level', string=u'Nível académico', 
        required=True
    )
    area = fields.Many2One(
        model_name='akademy.area', string=u'Área', 
        required=True, domain=[('academic_level', '=', Eval('academic_level', -1))],
        depends=['academic_level'])
    course = fields.Many2One(
        model_name='akademy.course', string=u'Curso', 
        required=True, domain=[('area', '=', Eval('area', -1))],
        depends=['area'])
    classe = fields.Many2One(
        model_name='akademy.course-classe', string=u'Classe', 
        required=True, domain=[('course', '=', Eval('course', -1))],
        depends=['course'])
    studyplan_discipline = fields.One2Many(
        'akademy.studyplan-discipline', 'studyplan', 
        string=u'Disciplina do plano de estudo'
    )
    classes = fields.One2Many(
        'akademy.classes', 'studyplan',
        string=u'Turma'
    )

    @classmethod
    def __setup__(cls):
        super(StudyPlan, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('Key', Unique(table, table.name, table.code),
            u'Não foi possível cadastrar o novo plano de estudo, por favor verifica se o nome ou código inserido já existe.')            
        ]    
      

class StudyPlanDiscipline(ModelSQL, ModelView):
    'StudyPlan Discipline'
    __name__ = 'akademy.studyplan-discipline'
    #_rec_name = 'discipline'
      
    description = fields.Text(string=u'Descrição')    
    state = fields.Selection(selection=sel_state, string=u'Estado', 
        required=True, help="Escolha o estado de frequência da disciplina.")
    modality = fields.Selection(selection=sel_modality, string=u'Modalidade',
        required=True, help="Escolha a modalidade de ensino da disciplina")
    quarter = fields.Many2One(
		model_name="akademy.quarter",  string=u'Trimestre', 
		required=True, help="Escolha o trimestre em que a disciplina será lecionada.")      
    hours = fields.Integer(string=u'Total de Horas', required=True,
        help="Carga horária da disciplina.")
    flaut = fields.Integer(string=u'Total de Faltas', required=True,
        help="Número máximo de faltas.")
    average = fields.Numeric(string=u'Média', digits=(2,2), 
        required=True, help='Média para aprovação.')
    studyplan = fields.Many2One(
        model_name='akademy.studyplan', string=u'Plano de estudo')
    discipline = fields.Many2One(
        model_name='akademy.discipline',  string=u'Disciplina', 
        required=True)
    studyplan_avaliations = fields.One2Many(
        'akademy.studyplan-avaliation', 'studyplan_discipline', 
        string=u'Disciplina avaliações')
    discipline_precedentes = fields.One2Many(
        'akademy.discipline-precedents', 'studyplan_discipline', 
        string=u'Disciplina precedentes')
    classe_student_discipline = fields.One2Many(
        'akademy.classe_student-discipline', 'studyplan_discipline',
        string=u'Plano de Estudo disciplina')
    classe_teacher_discipline = fields.One2Many(
        'akademy.classe_teacher-discipline', 'studyplan_discipline',
        string=u'Plano de Estudo Disciplina')
    student_grades = fields.One2Many(
		'akademy.classe_student-grades', 'studyplan_discipline', 
		string=u'Discente nota')
    historic_grades = fields.One2Many(
		'akademy.historic-grades',  'studyplan_discipline', 
		string=u'Discente nota')
    
    @classmethod
    def default_state(cls):
        return "Obrigatório"

    @classmethod
    def default_modality(cls):
        return "Presencial"    
    
    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.discipline.rec_name)
        return t1

    @classmethod
    def __setup__(cls):
        super(StudyPlanDiscipline, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('discipline', Unique(table, table.discipline, table.studyplan, table.quarter),
            u'Não foi possível cadastrar a disciplina neste plano de estudo, por favor verifica se a disciplina inserida já existe.'),
            ('hours', Check(table, table.hours >= 1),
            u'Não foi possível cadastrar a disciplina neste plano de estudo, por favor verifica a carga horária.'),
            ('average', Check(table, table.average <= 20),
            u'Não foi possível cadastrar a disciplina neste plano de estudo, por favor verifica se a média de aprovação esta acima de 20 valores.')
        ]     
    

class DisciplinePrecedents(ModelSQL, ModelView):
    'Discipline Precedents'
    __name__ = 'akademy.discipline-precedents'
    
    discipline = fields.Many2One(
        model_name='akademy.discipline', string=u'Disciplina', 
        required=True)   
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Disciplina do plano de estudo') 
    grade = fields.Numeric(
        string=u'Nota', digits=(2,1))

    @classmethod
    def default_grade(cls):
        return 0 
    
    #@classmethod
    #def default_state(cls):
    #    return "Obrigatório" 

    @classmethod
    def __setup__(cls):
        super(DisciplinePrecedents, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('discipline', Unique(table, table.discipline, table.studyplan_discipline),
            u'Não foi possível cadastrar a disciplina, por favor verifica se a disciplina inserida já existe.')            
        ]    
    

class StudyPlanAvaliation(ModelSQL, ModelView):
    'StudyPlan Avaliation'
    __name__ = 'akademy.studyplan-avaliation'

    description = fields.Text(string=u'Descrição') 
    state = fields.Selection(
        selection=sel_state,  string=u'Estado',
        required=True,
        help="Escolha o estado de frequência da disciplina.")
    perct_arithmetic = fields.Boolean(
        string='Média aritmética',
        depends=['perct_weighted'], 
        states={
            'invisible': Bool(Eval('perct_weighted')),
            'required': Not(Bool(Eval('perct_weighted')))
        },
        help=u'Calcula a média com base na operação artitmétrica.\n'+
        'Ex: Soma das avaliações, divido pelo número de avalições.')
    perct_weighted = fields.Boolean(
        string='Média ponderada',
        states={
            'invisible': Bool(Eval('perct_arithmetic')), 
            'required': Not(Bool(Eval('perct_arithmetic')))
        }, depends=['perct_arithmetic'], 
        help=u'Calcula a média com base na operação ponderada.\n'+
        'Ex: Soma da multiplicação das ponderações das avalições, divido pela soma das ponderações.')  
    percent = fields.Numeric(
        string=u'Percetagem', depends=['perct_weighted'],  
        states={
            'invisible': Not(Bool(Eval('perct_weighted'))), 
            'required': Bool(Eval('perct_weighted'))
        },
        help=u'A percetagem varia entre 1%'+' a 100%.')  
    metric_avaliation = fields.Many2One(
        model_name='akademy.metric-avaliation', string=u'Avaliação',        
        required=True,
        help="Nome da avaliação.")
    quarter = fields.Many2One(
		model_name="akademy.quarter", string=u'Trimestre', 
		required=True, 
		help="Escolha o trimestre em que a avaliação será lecionada.")
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', 
        string=u'Disciplina do plano de estudo') 
    stundent_grades = fields.One2Many(
		'akademy.classe_student-grades', 'studyplan_avaliation', 
		string=u'Discente nota')

    @classmethod
    def default_perct_arithmetic(cls):
        return True  
    
    @classmethod
    def default_state(cls):
        return "Obrigatório"

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.metric_avaliation.rec_name)
        return t1

    @classmethod
    def __setup__(cls):
        super(StudyPlanAvaliation, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key',
            Unique(table, table.metric_avaliation, table.quarter, table.studyplan_discipline),
            u'Não foi possível cadastrar avaliação, por favor verifica se já existe uma avaliação, neste nível trimestre.'),
            ('percent_max',
            Check(table, table.percent <= 100),
            u'Não foi possível cadastrar avaliação neste plano de estudo, por favor verifica se a percetagem é superior a 100%.'),
            ('percent_min',
            Check(table, table.percent > 0),
            u'Não foi possível cadastrar avaliação neste plano de estudo, por favor verifica se a percetagem é inferior ou igual a 0%.')
        ]   

