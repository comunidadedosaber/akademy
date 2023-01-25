from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from trytond.model import Check, ModelSQL, ModelView, Unique, fields
from trytond.pool import Pool
from trytond.pyson import Bool, Eval, Not
from trytond.wizard import Button, StateTransition, StateView, Wizard
from .varibles import sel_reference, sel_result

__all__ = ['Candidates', 'Applications', 'ApplicationsResult',
        'StudentTransfer', 'StudentTransferDiscipline',
        'MatriculationCreateWzardStart', 'MatriculationCreateWzard']


class Candidates(ModelSQL, ModelView):
    'Candidates'
    __name__ = 'akademy.candidates'
    #_rec_name = 'party'

    code = fields.Char(string=u'Código', size=20,
        help="Código do candidato.")
    date_start = fields.Date(string=u'Data de matrícula',
        help="Data de início da formação.")
    date_end = fields.Date(string=u'Data de conclusão',
        help="Data de término da formação.") 
    average = fields.Numeric(
        string=u'Média', digits=(2,1), 
        required=True, help=u'Média adquirida no certificado.')
    party = fields.Many2One(
        model_name='party.party', string=u'Nome', 
        required=True, domain=[('is_person', '=', True)],
        ondelete='CASCADE', help="Nome do candidato.")   
    institution = fields.Many2One(
        model_name='company.company', string=u'Instituição', 
        required=True, ondelete='CASCADE',
        help="Nome da instituição de formação.")       
    area = fields.Many2One(
        model_name='akademy.area', string=u'Área', 
        required=True, domain=[('academic_level', '=', Eval('academiclevel', -1))], 
        depends=['academiclevel'])
    course = fields.Many2One(
        model_name='akademy.course', string=u'Curso', 
        required=True, domain=[('area', '=', Eval('area', -1))], 
        depends=['area'])
    academiclevel = fields.Many2One(
        model_name='akademy.academic-level', string=u'Nível académico', 
        required=True) 
    applications = fields.One2Many(
        'akademy.applications', 'candidate', 
        string=u'Candidaturas')
    
    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.party.rec_name)
        return t1 

    @classmethod
    def __setup__(cls):
        super(Candidates, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.party, table.academiclevel),
            u'Não foi possível cadastrar o novo candidato, por favor verifica se já existe um candidato, neste nível académico.'),
            ('duration', Check(table, table.date_start < table.date_end),
            u'Não foi possível cadastrar o novo candidato, por favor verifica a data de matrícula e conclusão da formação académico.'),
            ('student', Check(table, table.average >= 10),
            u'Não foi possível cadastrar o novo candidato, por favor verifica a média do certificado.'),
            ('max_average', Check(table, table.average <= 20),
            u'Não foi possível cadastrar o novo candidato, por favor verifica a média do certificado.')
        ]
        cls._order = [('party', 'ASC')]


class Applications(ModelSQL, ModelView):
    'Applications'
    __name__ = 'akademy.applications'
    #_rec_name = 'candidate'
            
    state = fields.Boolean(string=u'Avaliado')
    description = fields.Text(string=u'Descrição')
    reference = fields.Selection(selection=sel_reference, string=u'Referência', 
        required=True)
    age = fields.Function(
        fields.Integer(
            string=u'Idade'
        ), 'on_change_with_age')
    candidate = fields.Many2One(
        model_name='akademy.candidates', string=u'Candidato', 
        required=True)
    phase = fields.Many2One(
        model_name='akademy.phase', string=u'Fase', 
        required=True, help="Fase de inscrição da candidatura.")
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo', 
        required=True, ondelete='CASCADE',
        help="Ano lectivo que pretende se inscrever.")
    academic_level = fields.Many2One(
        model_name='akademy.academic-level', string=u'Nível académico', 
        required=True, help="Nível académico que pretende se inscrever.")
    area = fields.Many2One(
        model_name='akademy.area', string=u'Área', 
        required=True, domain=[('academic_level', '=', Eval('academic_level', -1))],
        depends=['academic_level'])    
    course = fields.Many2One(
        model_name='akademy.course', string=u'Curso', 
        required=True, domain=[('area','=',Eval('area', -1))],
        depends=['area'])
    result = fields.One2Many(
        'akademy.applications-result', 'application', 
        string=u'Resultado', states={'invisible': Not(Bool(Eval('state')))},
        depends=['state'])
    course_classe = fields.Many2One(
        model_name='akademy.course-classe', string=u'Classe',
        required=True, domain=[('course', '=', Eval('course', 1))],
        depends=['course'])

    @fields.depends('candidate')
    def on_change_with_age(self, name=None):
        if self.candidate:
            # Retorna a idade do candidato
            now = datetime.now()
            delta = relativedelta(now, self.candidate.party.date_birth)
            years_months_days = delta.years
            return years_months_days

    #Verifica a fase de acordo com a data da candidatura
    #def default_phase(cls):
    #    Phase = Pool().get('akademy.phase')
    #    phase_admission = Phase.search([('start', '<=', date.today()), ('end', '>=', date.today())])
        
    #    if len(phase_admission) > 0:
    #        return phase_admission[0]
    #    else:
    #        return None
    
    @classmethod
    def default_reference(cls):
        return "Particular"

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.candidate.rec_name)
        return t1
    
    #Ao clicar no botão avaliar candidatura
    @classmethod
    @ModelView.button
    def application_avaliation(cls, applications):
        Criteria = Pool().get('akademy.application-criteria')
        ApplicationResult = Pool().get('akademy.applications-result') 
        
        if len(applications) >= 1:
            application_sorted = []
            for value in applications:
                application_sorted.append(value)                

            #Ordena com base da idade e média do critério de admissão
            application_sort = sorted(application_sorted, key=lambda application_sort: [application_sort.age, application_sort.candidate.average])           
            
            for element in application_sort:                
                phase_admission = element.phase
                ApplicationCriteria = Criteria.search([('course', '=', element.course), ('phase', '=', phase_admission)])
                
                Result = ApplicationResult.search([
                    ('result', '=', 'Admitido'), 
                    ('application_criteria', '=', ApplicationCriteria[0]),
                    ('lective_year', '=', element.lective_year)
                ]) 
                                                
                #Verifica se exite pelomenos uma candidatura admitida e um critério de admissão para o curso
                limit = len(Result)
                if len(ApplicationCriteria) >= 1:
                    if ApplicationCriteria[0].student_limit >= limit: 
                        if len(element.result) <= 1:
                            Applications.application_admission_avaliation(ApplicationCriteria, element, ApplicationResult, element.lective_year)
                        else:
                            cls.raise_user_error("Não foi possível avaliar a candidatura do candidato "", por favor verifica se já existe uma candidatura avalida para o mesmo.")
                    else:
                        cls.raise_user_error("Não foi possível avaliar a candidatura, porque já execdeu o limit establecido pela instituição.")
                else:
                    cls.raise_user_error("Não foi possível avaliar a candidatura, por favor verifica se existe pelomenos um critério de admissão da "+element.phase.name+", para o curso de "
                        +element.course.name+".\nOu se o candidato(a) "
                        +element.candidate.party.name+", já têm uma candidatura para neste curso e neste ano lectivo.")
        
    #Avalia a candidatura
    @classmethod
    def application_admission_avaliation(cls, ApplicationCriteria, application, ApplicationResult, lective_year):           
        
        if (len(ApplicationCriteria) >= 1):
            for application_criteria in ApplicationCriteria:
                if ((application_criteria.academic_level == application.academic_level)
                and (application_criteria.lective_year == application.lective_year) 
                and (application_criteria.area == application.area) 
                and (application_criteria.course == application.course)
                and (application_criteria.phase >= application.phase)):
                                        
                    if ((application_criteria.average <= application.candidate.average)
                    and (application_criteria.age >= application.age)
                    and (application_criteria.phase >= application.phase)):
                        result_avaliation = 'Admitido'
                        Applications.application_admission(ApplicationResult, application, application_criteria, result_avaliation, lective_year) 
                    else:                   
                        result_avaliation = 'Não Admitido'
                        Applications.application_admission(ApplicationResult, application, application_criteria, result_avaliation, lective_year)
        else:
            cls.raise_user_error("Não foi possível avaliar a candidatura, por favor verifica se existe pelomenos um critério de admissão para o curso de "+application.course.name+".")

    #Cria um registro de discente para o candidato
    @classmethod
    def application_admission(cls, ApplicationResult, application, criteria, result_avaliation, lective_year):         
        #Busca a lista de candidaturas admitidas
        total_application_admission = ApplicationResult.search([('application_criteria', '=', criteria), ('result', '=', 'Admitido')]) 
        #Verifica se a lista de candidatos admitidos é menor que o limite de admissões 
        if criteria.student_limit > len(total_application_admission):              
            Result = ApplicationResult(
                result = result_avaliation,
                phase = criteria.phase,
                application = application,
                application_criteria = criteria,
                lective_year = lective_year
            )
            Result.save() 
            #Muda o estado da candidatura para Avaliado
            Applications.application_change_state(application, result_avaliation)
        else:
            cls.raise_user_error("Já antigui o limite maximo de vagas disponíveis.") 

    @classmethod
    def application_change_state(cls, application, result_avaliation):
        application.state = True
        application.save()   

        if result_avaliation == 'Admitido':
            MatriculationCreateWzard.student_candidate(application)

    @classmethod
    def __setup__(cls):
        super(Applications, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.candidate, table.course, table.phase, table.lective_year),
            u'Não foi possível matrícular os candidatos, porque o candidato já é discente desta instistuição, por favor verifique se o mesmo já têm um registro de matrícula.')
        ]
        cls._buttons.update({
            'application_avaliation':{
                'invisible': Eval('state')
            }
        })        
        cls._order = [('candidate', 'ASC')]               
                          	
    
class ApplicationsResult(ModelSQL, ModelView):
    'Applications'
    __name__ = 'akademy.applications-result'
    #_rec_name = 'application'
    
    result = fields.Selection(selection=sel_result, string=u'Resultado')  
    phase = fields.Many2One(model_name='akademy.phase', string=u'Fase', required=True)
    application = fields.Many2One(
        model_name='akademy.applications', string=u'Candidatura', 
        required=True, ondelete='CASCADE')
    application_criteria = fields.Many2One(
        model_name='akademy.application-criteria', string=u'Critério de Admissão', 
        required=True, ondelete='CASCADE')
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo', 
        required=True, ondelete='CASCADE')
    
    @classmethod
    def default_result(cls):
        return "Analizando"

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.application.rec_name)
        return t1

    #Ao clicar no botão esta acção executada
    @classmethod
    @ModelView.button
    def application_matriculation(cls, application):        
        #Cria um registro de estudante 
        StudentMatriculation = Pool().get('company.student')
        #Verifica se o estudante existe
        for matriculate_application in application:
            student = StudentMatriculation.search([('party', '=', matriculate_application.application.candidate.party)])
            if(len(student) < 1):
                    StudentMatriculation.create_student(matriculate_application.application.candidate.party)
            else:
                cls.raise_user_error("O candidato já foi matrículado.")
        
    @classmethod
    def __setup__(cls):
        super(ApplicationsResult, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.application, table.application_criteria),
            u'A candidatura já foi avalida.')
        ]     
        cls._order = [('application', 'ASC')] 
        cls._buttons.update({
            'application_matriculation': {
                'invisible': Eval('result') == 'Não Admitido',
                'depends': ['result'],
            },
        })


class StudentTransfer(ModelSQL, ModelView):
    'Student - Transfer'
    __name__ = 'akademy.student-transfer'
    #_rec_name = 'student'

    description = fields.Text(string=u'Descrição')
    internal = fields.Boolean(
        string=u'Interna',
        states={ 
            'invisible': Bool(Eval('external')), 
            'required': Not(Bool(Eval('external')))
        }, depends=['external'],
        help='Saindo da instituição.')
    external = fields.Boolean(
        string=u'Externa',
        states={
            'invisible': Bool(Eval('internal')), 
            'required': Not(Bool(Eval('internal')))
        }, depends=['internal'],
        help='Vindo de outra instituição.')
    lective_year = fields.Many2One(
		model_name='akademy.lective-year', string=u'Ano lectivo', 
        states={
            'required': Bool(Eval('external')), 
            'invisible': Not(Bool(Eval('external'))), 
        }, help="Nome do ano lectivo.")
    academic_level = fields.Many2One(
		model_name='akademy.academic-level', string=u'Nível académico', 
        states={
            'required': Bool(Eval('external')), 
            'invisible': Not(Bool(Eval('external'))), 
        }, help="Nome da nível académico.")
    area = fields.Many2One(
		model_name='akademy.area', string=u'Área', 
        states={
            'required': Bool(Eval('external')), 
            'invisible': Not(Bool(Eval('external'))), 
        },
		domain=[('academic_level', '=', Eval('academic_level', -1))], 
		depends=['academic_level'], help="Nome da área.")
    course = fields.Many2One(
		model_name='akademy.course', string=u'Curso', 
        states={
            'required': Bool(Eval('external')), 
            'invisible': Not(Bool(Eval('external'))), 
        },
		domain=[('area', '=', Eval('area', -1))],
		depends=['area'], help="Nome da curso.")
    course_classe = fields.Many2One(
		model_name='akademy.course-classe', string=u'Classe', 
        states={
            'required': Bool(Eval('external')), 
            'invisible': Not(Bool(Eval('external'))), 
        },
        domain=[('course', '=', Eval('course', -1))],
		depends=['course'], help="Nome da classe.")
    student = fields.Many2One(
		model_name='company.student', string=u'Discente', 
		required=True
	)
    student_transfer_discipline = fields.One2Many(
		'akademy.student_transfer-discipline', 'student_transfer', 
		string=u'Média Disciplina'
	)

    def get_rec_name(self, name):
        return self.student.rec_name
    
    @classmethod
    def __setup__(cls):
        super(StudentTransfer, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key',
            Unique(table, table.lective_year, table.academic_level, table.course, table.course_classe, table.student),
            u'Não foi possível cadastrar a transferência, por favor verifique se o discente já se encontra com uma transferência com estes dados.')
        ]  


class StudentTransferDiscipline(ModelSQL, ModelView):
    'Student Tranfer - Discipline'
    __name__ = 'akademy.student_transfer-discipline'

    course = fields.Function(
		fields.Integer(
			string=u'Curso',
		), 'on_change_with_course')
    average = fields.Numeric(string=u'Média', digits=(2,1), required=True) 
    student_transfer = fields.Many2One(
        model_name='akademy.student-transfer', 
        string=u'Discente', required=True)
    discipline = fields.Many2One(
        model_name = 'akademy.discipline', 
        string=u'Disciplina', required=True)   
    course_classe = fields.Many2One(
        model_name='akademy.course-classe', string=u'Classe', 
        required=True, domain=[('course.id', '=', Eval('course', -1))],
        depends=['course'], help="Nome da classe.")

    @fields.depends('student_transfer')
    def on_change_with_course(self, name=None):
        return self.student_transfer.course.id

    @classmethod
    def __setup__(cls):
        super(StudentTransferDiscipline, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('uniq_classes',
            Unique(table, table.student_transfer, table.discipline),
            u'Não foi possível associar está disciplina ao discente, por favor verifique se o mesmo já têm esta disciplina associada.')            
        ]



#Assistente
class MatriculationCreateWzardStart(ModelView):
    'Matriculation CreateStart'
    __name__ = 'akademy.wizmatriculation_create.start'

    is_candidate = fields.Boolean(
        string=u'Candidato', 
        states={
            'invisible':  Bool(Eval('is_transferred')) | Bool(Eval('is_student'))
        }, depends=['is_transferred', 'is_student'], 
        help='A entidade é uma pessoa.')
    is_transferred = fields.Boolean(
        string=u'Transferido', 
        states={
            'invisible':  Bool(Eval('is_candidate')) | Bool(Eval('is_student'))
        }, depends=['is_candidate', 'is_student'], 
        help='A entidade é uma instituição ou organização.')
    is_student = fields.Boolean(
        string=u'Discente', 
        states={
            'invisible':  Bool(Eval('is_candidate')) | Bool(Eval('is_transferred'))
        }, depends=['is_candidate', 'is_transferred'], 
        help='A entidade é uma instituição ou organização.')
    applications = fields.Many2One(
        model_name='akademy.applications-result', string=u'Candidato',
        states={
            'invisible': Not(Bool(Eval('is_candidate'))), 
            'required': Bool(Eval('is_candidate'))
        }, domain=[('result', '=', 'Admitido')], 
        help="Caro utilizador será feita a matrícula do discente.")
    transferred = fields.Many2One(
        model_name='akademy.student-transfer', string=u'Transferido',
        states={
            'invisible': Not(Bool(Eval('is_transferred'))), 
            'required': Bool(Eval('is_transferred'))
        }, domain=[('external', '=', True)],
        help="Caro utilizador será feita a matrícula do discente transfêrido.")
    student = fields.Many2One(
        model_name='company.student', string=u'Discente',
        states={
            'invisible': Not(Bool(Eval('is_student'))), 
            'required': Bool(Eval('is_student'))
        }, help="Caro utilizador será feita a matrícula do discente.")
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        states={
            'invisible': Not(Bool(Eval('is_student'))), 
            'required': Bool(Eval('is_student'))
        }, help="Informa o nome da turma.")
    
    
class MatriculationCreateWzard(Wizard):
    'Matriculation CreateWzard'
    __name__ = 'akademy.wizmatriculation_create'

    start_state = 'start'
    start = StateView(
        model_name='akademy.wizmatriculation_create.start', \
        view="akademy.act_matriculation_wizard_from", \
        buttons=[
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Matricular', state='matriculation', icon='tryton-save')
        ]
    )
    matriculation = StateTransition()

    def transition_matriculation(self):
       
        if (self.start.is_candidate == True):
            MatriculationCreateWzard.student_candidate(self.start.applications.application)
        if (self.start.is_transferred == True):
            MatriculationCreateWzard.student_transferred(self.start.transferred)
        if (self.start.is_student == True):
            MatriculationCreateWzard.matriculation_confirmation(self.start.student, self.start.classes)
                    
        return 'end'

    #Quando se tratar de matrícula por transferência
    @classmethod
    def student_transferred(cls, student):  
        Classes = Pool().get('akademy.classes')
        Studyplan = Pool().get('akademy.studyplan')
        ClasseStudent = Pool().get('akademy.classe-student')
        Student = Pool().get('company.student')
        
        get_studyplan = Studyplan.search(
            [
                ('area', '=', student.area),
                ('course', '=', student.course)
            ]
        )
                
        #PROCESSO DE EQUIVALENCIAS
        for studyplan in get_studyplan:
            discipline_required = []
            student_discipline_possitive = []
            get_student_transferred_discipline = []
            discipline_positive = []

            for studyplan_discipline in studyplan.studyplan_discipline:    
                # VERIFICA SE O DISCENTE TÊM DISCIPLINA, NA TRANSFÊRENCIA
                if len(student.student_transfer_discipline) > 0: 

                    for student_transfer_discipline in student.student_transfer_discipline:
                        #Verifica se a classe da disciplina transfêrida e a mesma classe do plano de estudo
                        if student_transfer_discipline.course_classe == studyplan.classe:
                            # Verifica se a disciplina do discente é a mesma do plano de estudo 
                            if (student_transfer_discipline.discipline ==  studyplan_discipline.discipline):
                                if (studyplan_discipline.average > student_transfer_discipline.average):                                
                                    get_student_transferred_discipline.append(studyplan_discipline)                                    
                                else:
                                    #Somente disciplinas com possitivas                                    
                                    student_discipline_possitive.append(student_transfer_discipline)                                    
                                    discipline_positive.append(studyplan_discipline)                                    
                else:
                    get_student_transferred_discipline.append(studyplan_discipline)

                #Verifica se a disciplina é de caractér obrigatório
                if studyplan_discipline.state == "Obrigatório":
                    discipline_required.append(studyplan_discipline)

            #Caso tenha aprovado na classe
            if len(discipline_required) == len(student_discipline_possitive):                            
                pass
            else:
                #Procura pelas disciplinas em falta no plano de estudo
                for studyplan_discipline in studyplan.studyplan_discipline: 
                    #Verifica se a disciplina já existe ou é positiva
                    if studyplan_discipline not in discipline_positive and studyplan_discipline not in get_student_transferred_discipline:                        
                        get_student_transferred_discipline.append(studyplan_discipline)
                
                #Visto que o discente tenha aprovado, será matrículado na proxima classe
                if len(student_discipline_possitive) == 0:
                    classe_matriculation = studyplan_discipline.studyplan.classe.classe
                else:
                    classe_matriculation = student_discipline_possitive[0].course_classe.classe
                
                #Procura pela turma em que na qual a matrícula será efectuado
                get_classes = Classes.search(
                    [
                        ('lective_year', '=', student.lective_year),
                        ('classe', '=', classe_matriculation),
                        ('studyplan', '=', studyplan)
                    ]
                )
                                
                #VERIFICA SE O DISCENTE JÁ ESTA MATRÍCULADO
                if len(student.student.student) > 0:
                    #cls.raise_user_error("Infelismente não é possivel matrícular o discente, porque o discente já está matriculado na turma, "+get_classes[0].name+".")
                    pass
                else:
                    #Verifica se há compatibilidade de planos de estuods
                    if len(get_classes) > 0:                        
                        get_class_student = ClasseStudent.search(
                            [
                                ('student', '=', student.student),
                                ('classes', '=', get_classes[0])
                            ]
                        ) 
                        #Verifica se o discente já é matrículado
                        if len(get_class_student) > 0:
                            cls.raise_user_error("O discente "+student.student.party.name+" já existe na instituição, por favor verifique a matrícula na "+get_class_student[0].classes.name+".")
                            #procura pelas disciplinas e efectua a matrícula em disciplinas nais quais o discente reprovou
                        else:
                            #Verifica se há vagas disponiveis na turma
                            if (get_classes[0].max_student != len(get_classes[0].classe_student)):
                                MatriculationCreateWzard.save_student_matriculation(student, ClasseStudent, 'Matrículado(a)', 'Transfêrido(a)', student.student, get_classes[0], get_classes[0].classe, 0)                                                        
                                student_matriculatio = Student.search(
                                    [
                                        ('party','=',student.student.party),
                                        ('academiclevel','=',student.student.academiclevel),
                                        ('area','=',student.student.area),
                                        ('course','=',student.student.course)
                                    ]
                                )
                                #Muda o estado da matrícula
                                if len(student_matriculatio) > 0:
                                    student_matriculatio[0].state = "Matrículado(a)"
                                    student_matriculatio[0].save()
                                
                                #Procurar pelas disciplinas no percurso académico
                                MatriculationCreateWzard.student_transferred_discipline(student.student.student, get_student_transferred_discipline, get_classes[0].studyplan)
                            else:
                                cls.raise_user_error("Infelismente não é possivel matrícular o discente, porque ja excedeu o limite de vagas disponiveis.")
                    else:
                        cls.raise_user_error("Infelismente não é possivel matrícular o discente, porque não foi encontrato um encontrado uma turma disponivel para ele(a).")           

    @classmethod
    def student_transferred_discipline(cls, student, discipline_negative, studyplan):
        
        if len(studyplan.studyplan_discipline) > 0:
            # Verifica se o discente têm disciplinas
            if len(discipline_negative) > 0:
                MatriculationCreateWzard.association_discipline(student, discipline_negative)
            else:
                cls.raise_user_error("Infelismente não é possivel associar disciplinas ao discente, porque não há negativas.")        
        else:
            cls.raise_user_error("Infelismente não é possivel associar disciplinas ao discente, porque não foi encontrado um plano de estudo compatível com o seu percurso académico.")
        
    @classmethod
    def association_discipline(cls, student, studyplan_discipline):
        StudentClasseDiscipline = Pool().get('akademy.classe_student-discipline') 
                
        if len(studyplan_discipline) > 0:
            for discipline in studyplan_discipline:
                #VERIFICA SE O DISCENTE JÁ ESTA MATRÍCULADO NESTA DISCIPLINA
                student_matriculation = StudentClasseDiscipline.search(
                    [
                        ('classe_student', '=', student[0]), 
                        ('studyplan_discipline', '=', discipline)
                    ]
                )                
                if len(student_matriculation) > 0:
                    pass
                else:    
                    MatriculationCreateWzard.save_student_discipline(StudentClasseDiscipline, student[0], 0, discipline, False, 'Matrículado(a)', 'Presencial')
                    
        else:
            cls.raise_user_error("Infelismente não é possivel associar disciplinas ao discente, porque o discente não reprovou a nenhuma discplina, frequentada na turma "+student[0].classes.name+" no ano lectivo de "+student[0].classes.lective_year.name+".\nOu já esta frequentar as disciplinas nesta turma.")

    #Quando se tratar de matrícula por candidatura
    @classmethod
    def student_candidate(cls, student):
        NewStudent = Pool().get('company.student')
        matriculation_type = 'Candidato(a)'

        # Quando o discente ja existir na instituição
        if len(student.candidate.party.student) > 0:
            MatriculationCreateWzard.candidate_matriculation(student, student.candidate.party.student[0], matriculation_type)          
        # Quando for um novo estudante
        else:
            student_matriculatio = NewStudent.search(
                [
                    ('party','=',student.candidate.party),
                    ('academiclevel','=',student.academic_level),
                    ('area','=',student.area),
                    ('course','=',student.course)
                ]
            )
            
            if len(student_matriculatio) > 0:
                pass
            else:
                Matriculation = NewStudent(
                    #start_date
                    #end_date 
                    #party
                    state = 'Matrículado(a)',
                    course = student.course,
                    area = student.area,
                    academiclevel = student.academic_level,
                    party = student.candidate.party,
                    #candidates = student.application.candidate,
                )
                Matriculation.save()

                MatriculationCreateWzard.candidate_matriculation(student, Matriculation, matriculation_type)        
        
    @classmethod
    def candidate_matriculation(cls, student, matriculation, matriculation_type):
        ClasseStudent = Pool().get('akademy.classe-student')
        Classes = Pool().get('akademy.classes')

        get_classes = Classes.search(
            [
                ('lective_year', '=', student.lective_year),
                ('classe', '=', student.course_classe.classe),
                ('studyplan', '=', student.area.studyplan[0]),
                #('studyplan.course', '=', student.application.candidate.course)
            ]
        )

        if len(get_classes) > 0:
            #Verifica se há vagas disponiveis na turma
            if (get_classes[0].max_student != len(get_classes[0].classe_student)):
                state = 'Matrículado(a)'
                MatriculationStudent = MatriculationCreateWzard.save_student_matriculation(student, ClasseStudent, state, matriculation_type, matriculation, get_classes[0], get_classes[0].classe, 0)
                
                MatriculationCreateWzard.discipline_matriculation(MatriculationStudent, student.area.studyplan[0].studyplan_discipline)  
            else:
                cls.raise_user_error("Infelismente não é possivel matrícular o discente, porque ja excedeu o limite de vagas disponiveis.")
        else:
            cls.raise_user_error("Não foi possivél efectuar a matrícula do estudante ou candidato, porque ainda não existe uma turma criada.")              

    @classmethod
    def discipline_matriculation(cls, student, studyplan_discipline):
        StudentClasseDiscipline = Pool().get('akademy.classe_student-discipline')        
        
        if len(studyplan_discipline) > 0:
            for discipline in studyplan_discipline:
                #VERIFICA SE O DISCENTE JÁ ESTA MATRÍCULADO NESTA DISCIPLINA
                student_matriculation = StudentClasseDiscipline.search(
                    [
                        ('classe_student', '=', student), 
                        ('studyplan_discipline', '=', discipline)
                    ]
                )                
                if len(student_matriculation) > 0:
                    pass
                else:
                    MatriculationCreateWzard.save_student_discipline(StudentClasseDiscipline, student, 0, discipline, True, "Matrículado(a)", "Presencial")                    
        else:
            cls.raise_user_error("Infelismente não é possivel associar disciplinas ao discente, porque o discente não reprovou a nenhuma discplina, frequentada na turma "+student[0].classes.name+" no ano lectivo de "+student[0].classes.lective_year.name+".\nOu já esta frequentar as disciplinas nesta turma.")

    #Confirmação de matrícula
    @classmethod
    def matriculation_confirmation(cls, company_student, classes):
        student = []
        ClasseStudent = Pool().get('akademy.classe-student')
        Student_Discipline = Pool().get('akademy.classe_student-discipline')
        CourseYear = Pool().get('akademy.course-classe')  

        student_has_matriculation = ClasseStudent.search([('student', '=', company_student)])
        classes_classe_year = CourseYear.search([('classe', '=', classes.classe), ('course', '=', classes.studyplan.course)])
        not_update = 0

        #Verificar se têm matrícula
        if len(student_has_matriculation) > 0:
            #Pega a ultima matricula do discente
            classe_student = student_has_matriculation[len(student_has_matriculation) -1]
            student_classe_year = CourseYear.search([('classe', '=', classe_student.classes.classe), ('course', '=', classe_student.classes.studyplan.course)])        
            verify_year = int(classes_classe_year[0].course_year) - int(student_classe_year[0].course_year)
            
            for student in student_has_matriculation:
                #Verifica se o discente já têm matrícula nesta turma
                student_matriculation = ClasseStudent.search([('student', '=', student.student), ('classes', '=', classes)])
                if len(student_matriculation) == 0:
                    #Verificar se já têm matrícula neste ano curricular            
                    if verify_year == 0:
                        if student.state in ["Matrículado(a)", "Aprovado(a)"]:
                            cls.raise_user_error("O discente "+company_student.party.name+", não pode frequentar a classe "+classes.classe.name+", na turma "+classes.name+", pois o mesmo já têm matrícula nesta classe e turma.")
                        #Efectua a matrícula
                        if student.state == "Reprovado(a)":
                            MatriculationCreateWzard.student_classe_matriculation(student, ClasseStudent, company_student, classes, Student_Discipline, not_update)                            
                    #Verificar se é transição de ano curricular
                    elif verify_year == 1:                
                            #Efectua a matrícula do discente
                            if student.state == "Aprovado(a)":
                                MatriculationCreateWzard.student_classe_matriculation(student, ClasseStudent, company_student, classes, Student_Discipline, not_update)                                                        
                            if student.state == ["Matrículado(a)", "Reprovado(a)"]:
                                cls.raise_user_error("O discente "+company_student.party.name+", não pode frequentar a classe "+classes.classe.name+", na turma "+classes.name+", pois o mesmo já têm matrícula na classe "+company_student.classe.name+" na turma "+classe_student.classes.name+".")
                    #Verificar se o discente está a pular de ano            
                    else:
                        cls.raise_user_error("Não foi possivél matrícular o discente "+company_student.party.name+", na classe "+classes.classe.name+", porque o mesmo ainda não têm uma matrículado na classe anterior.")
                else:
                    pass
        else:
            course_frist_year = 1
            verify_year = course_frist_year - int(classes_classe_year[0].course_year)
            #Verificar se o discente está a pular de ano 
            if verify_year == 0:
                MatriculationCreateWzard.student_classe_matriculation(student, ClasseStudent, company_student, classes, Student_Discipline, not_update)                
            else:
                cls.raise_user_error("Não foi possivél matrícular o discente "+company_student.party.name+", na classe "+classes.classe.name+", por favor verifique a situação do discente.")
    
    @classmethod
    def student_classe_matriculation(cls, classe_student, ClasseStudent, company_student, classes, Student_Discipline, not_update):
        MatriculationStudent = MatriculationCreateWzard.save_student_matriculation(classe_student, ClasseStudent, 'Matrículado(a)', 'Transição de classe', company_student, classes, classes.classe, not_update)        
        student = []

        for studyplan_discipline in classes.studyplan.studyplan_discipline:                        
            #VERIFICA SE O DISCENTE JÁ ESTA MATÍCULADO NESTA DISCIPLINA
            student_matriculation = Student_Discipline.search(
                [
                    ('classe_student', '=', MatriculationStudent), 
                    ('studyplan_discipline', '=', studyplan_discipline)
                ]
            )
            
            if len(student_matriculation) > 0:
                pass
            else:
                if len(studyplan_discipline.discipline_precedentes) > 0:
                    MatriculationCreateWzard.save_student_discipline(Student_Discipline, MatriculationStudent, classes.studyplan.id, studyplan_discipline, False, "Matrículado(a)", "Presencial")                                
                else:      
                    #Matrícula o discente na disciplina
                    MatriculationCreateWzard.save_student_discipline(Student_Discipline, MatriculationStudent, classes.studyplan.id, studyplan_discipline, False, "Matrículado(a)", "Presencial")
                    
            #if len(classe_student) > 0:
            student.append(classe_student.student)
        
        student.clear() 
          
    @classmethod
    def save_student_matriculation(cls, classe_student, ClasseStudent, state, type, student, classes, classe, not_update):        
        #Efectua a matrícula do discente
        MatriculationStudent = ClasseStudent(
            state = state,
            type = type,
            student = student,
            classes = classes,
        )
        MatriculationStudent.save()

        #Atualiza o ano curricular
        MatriculationCreateWzard.update_student_classe(student, classe)        
        if not_update == 0:
            pass
        else:
            #Atualiza o estado da matrícula
            MatriculationCreateWzard.update_student_state(classe_student)

        return MatriculationStudent
       
    @classmethod
    def save_student_discipline(cls, StudentDiscipline, StudentClasse, Studyplan, StudyplanDiscipline, repeat, state, modality):
        #Efectua a matrícula do disente na disciplina
        matriculaton = StudentDiscipline(
            classe_student = StudentClasse,
            studyplan = Studyplan,
            studyplan_discipline = StudyplanDiscipline,
            state = state,
            modality = modality,
            repeat = repeat,
        )
        matriculaton.save() 

    @classmethod
    def update_student_classe(cls, company_student, classe):
        #Atualiza a classe do discente
        company_student.classe = classe
        company_student.save()

    @classmethod
    def update_student_state(cls, classe_student):
        #Atualiza o estado da matrícula
        classe_student.state = 'Aprovado(a)'
        classe_student.save()

