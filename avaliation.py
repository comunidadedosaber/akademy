from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval
from datetime import date
from .variables import sel_presence, sel_schedule

__all__ = ['PublicGradesCreateWizard', 'PublicGradesCreateWizardStart', 'ScheduleCreateWizard', 'ScheduleCreateWizardStart', 'PublicHistoricCreateWizard', 'PublicHistoricCreateWizardStart',
        'ClassesAvaliation', 'ClassesStudentAvaliation', 'ClassesSchedule', 'ClassesScheduleQuarter', 'ClassesStudentScheduleQuarter', 'ClassesStudentSchedule', 'HistoricGrades']


#Assistente Grades
class PublicGradesCreateWizardStart(ModelView):
    'PublicGradesCreate Start'
    __name__ = 'akademy.wizpublicgrades_create.start'
    
    studyplan = fields.Function(
        fields.Integer(
            string=u'Plano de Estudo'
        ), 'on_change_with_studyplan')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        required=True, help="Informa o nome da turma.")
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Disciplina', 
        states={ 
            'required': True
        }, required=True, 
        domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
        depends=['studyplan'], help="Informa o nome da disciplina.")   
    metric_avaliation = fields.Many2One(
        model_name='akademy.metric-avaliation', string=u'Avaliação',
        states={
            'required': True
        }, required=True, 
        help="Nome da avaliação.") 
    quarter = fields.Many2One(
		model_name="akademy.quarter", string=u'Trimestre', 
		help="Escolha o trimestre em que a avaliação será lecionada.")      

    @fields.depends('classes')
    def on_change_with_studyplan(self, name=None):
        if self.classes:
            return self.classes.studyplan.id
        else:
            return None

    
class PublicGradesCreateWizard(Wizard):
    'PublicGrades Create'
    __name__ = 'akademy.wizpublicgrades_create'

    start_state = 'start'
    start = StateView(
        model_name='akademy.wizpublicgrades_create.start', \
        view='akademy.act_publicgrades_wizard_from', \
        buttons=[
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Lançar notas', state='studentgrades', icon='tryton-save')
        ]
    )
    studentgrades = StateTransition()

    def transition_studentgrades(self): 
        ClassesStudent = Pool().get('akademy.classe-student')
        StudentClasses = ClassesStudent.search([('classes', '=', self.start.classes)])        
        Quarter= Pool().get('akademy.quarter') 
        classes_avaliation = 0

        #Verifica se o trimestre foi selecionado
        if self.start.quarter: 
            quarter = self.start.quarter 
            quarter_studyplan_avaliations = self.start.quarter.studyplan_avaliations 
        else:    
            quarter = Quarter.search([('start', '<=', date.today()), ('end', '>=', date.today())])
            quarter  = quarter[0]
            quarter_studyplan_avaliations = quarter.studyplan_avaliations

        for studyplan_avaliations in quarter_studyplan_avaliations:
            #Verifica se a avaliação a ser lançada a nota e a mesma que foi selecionada  
            for studyplan_avaliation in self.start.studyplan_discipline.studyplan_avaliations:                     
                if studyplan_avaliations == studyplan_avaliation:  
                    if studyplan_avaliations.metric_avaliation == self.start.metric_avaliation: 

                        classes_avaliation = ClassesAvaliation.save_classes_avaliation(self.start, quarter, studyplan_avaliation)                        
                        break            

        #ESTADO DA MATRÍCULA
        state_student = ['Aguardando', 'Suspenso(a)', 'Anulada', 'Transfêrido(a)', 'Reprovado(a)']        
        
        #Verifica se a discplina têm a avaliação
        if classes_avaliation != 0:
            for classe_student in StudentClasses:
                #VERIFICA O ESTADO DA MATRÍCULA
                if classe_student.state not in state_student: 
                    for classes_student_discipline in classe_student.classe_student_discipline:
                        #Verifica se a disciplina a ser lançada a nota e a mesma que foi selecionada
                        if classes_student_discipline.studyplan_discipline == self.start.studyplan_discipline:
                            
                            ClassesStudentAvaliation.save_classes_student_avaliation(classe_student, classes_avaliation)
        else:
            self.raise_user_error("A disciplina "+self.start.studyplan_discipline.discipline.name+" não tẽm a avalicação "+self.start.metric_avaliation.name+".")                        

        return 'end'
          

class ScheduleCreateWizardStart(ModelView):
    'ScheduleCreate Start'
    __name__ = 'akademy.wizschedule_create.start'

    studyplan = fields.Function(
        fields.Integer(
            string=u'Plano de Estudo'
        ), 'on_change_with_studyplan')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        required=True, help="Informa o nome da turma.")
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', 
        string=u'Disciplina', required=True, 
        domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
        depends=['studyplan'], help="Informa o nome da disciplina.")      
    schedule = fields.Selection(selection=sel_schedule, string=u'Tipo de pauta', required=True) 
    quarter = fields.Many2One(
		model_name="akademy.quarter", string=u'Trimestre',  
		help="Escolha o trimestre em que a avaliação será lecionada.")

    @fields.depends('classes')
    def on_change_with_studyplan(self, name=None):
        return self.classes.studyplan.id

    
class ScheduleCreateWizard(Wizard):
    'Schedule Create'
    __name__ = 'akademy.wizschedule_create'

    start_state = 'start'
    start = StateView(
        model_name='akademy.wizschedule_create.start', \
        view='akademy.act_schedule_wizard_from', \
        buttons=[
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Gerar pauta', state='discipline_schedule', icon='tryton-save')
        ]
    )
    discipline_schedule = StateTransition()

    def transition_discipline_schedule(self): 
        #Quarter = Pool().get('akademy.quarter') 
        schedule_t = "Pauta trimestral"
        schedule_f = "Pauta final"
        
        # Verifica se o tipo de pauta e o trimestre foram selecionados
        if self.start.schedule:            
            if self.start.schedule == schedule_t:
                if self.start.quarter:        
                    quarter_metric = self.start.quarter
                else:
                    #Verifica qual é a metrica com base na data actual
                    #quarter_metric = Quarter.search([('start', '<=', date.today()), ('end', '>=', date.today())])
                    #quarter_metric = quarter_metric[0]
                    self.raise_user_error("Por favor informe o trimestre em que na qual deseja criar a pauta.")
                                                
                if len(self.start.classes.classes_avaliation) > 0:
                    #Pesquisa pelo docente
                    classes_schedule_quarter = ClassesScheduleQuarter.save_classes_schedule_quarter(self.start, quarter_metric)
                    
                    #Pesquisa pelo discente       
                    student_state = ['Aguardando', 'Suspenso(a)', 'Anulada', 'Transfêrido(a)', 'Reprovado(a)']

                    for classes_student in self.start.classes.classe_student:
                        #VERIFICA O ESTADO DA MATRÍCULA
                        if classes_student.state not in student_state:                                                   
                            quarter_gardes = ScheduleCreateWizard.get_student_grades_quarter(classes_student, self.start.studyplan_discipline, quarter_metric)
                            
                            if quarter_gardes is not None:        
                                ClassesStudentScheduleQuarter.save_classes_student_schedule_quarter(
                                    quarter_gardes[0], 
                                    quarter_gardes[1],
                                    quarter_gardes[2],
                                    quarter_gardes[3],
                                    classes_schedule_quarter,
                                    classes_student,
                                )
                            
                else:
                    self.raise_user_error("Infelizmente não foi possivél criar a pauta, porque ainda não existem avaliações na turma "+self.start.classes.name+".")

            if self.start.schedule == schedule_f:
                student_state = ['Aguardando', 'Suspenso(a)', 'Anulada', 'Transfêrido(a)', 'Reprovado(a)']
                
                if len(self.start.classes.classes_schedule_quarter) > 0:
                    classes_schedule_final = ClassesSchedule.save_classes_schedule(self.start)
                    
                else:
                    self.raise_user_error("Infelizmente não foi possivél criar a pauta final, porque ainda não existem pautas trimestrais na turma "+self.start.classes.name+".")
                
                #Pesquisa pelo discente
                for classes_student in self.start.classes.classe_student:
                    #VERIFICA O ESTADO DA MATRÍCULA
                    if classes_student.state not in student_state:
                        quarter_average = ScheduleCreateWizard.get_student_grades(classes_student, self.start.classes, self.start.studyplan_discipline)
                    
                    #Pesquisa pela prova final do discente
                    discipline_final_grade = ScheduleCreateWizard.get_student_final_grade(classes_student, self.start.studyplan_discipline)                                                                        
                    
                    # Caso o discente não esteja associado a disciplina enquestão
                    if discipline_final_grade is not None: 
                        student_discipline_final_grade = (quarter_average[0] + discipline_final_grade) / 2
                        
                        ClassesStudentSchedule.save_classes_student_schedule(
                            quarter_average[1], 
                            quarter_average[2],
                            quarter_average[3],
                            discipline_final_grade,
                            round(student_discipline_final_grade),
                            classes_schedule_final,
                            classes_student,
                            self.start.studyplan_discipline.average
                        )                                                 

        return 'end'

    @classmethod
    def get_student_grades(cls, classes_student, classes, studyplan_discipline):
        first_quarter = 0
        second_quarter = 0
        third_quarter = 0

        #Pesquisa pela notas trimestrais do discente
        for student_schedule_quarter in classes_student.classes_student_schedule_quarter:
            if student_schedule_quarter.classes_schedule_quarter.classes == classes and student_schedule_quarter.classes_schedule_quarter.lective_year == classes.lective_year:
                if student_schedule_quarter.classes_schedule_quarter.studyplan_discipline == studyplan_discipline:
                    
                    if student_schedule_quarter.classes_schedule_quarter.quarter.name == "1º Trimestre":
                        first_quarter = student_schedule_quarter.average
                    if student_schedule_quarter.classes_schedule_quarter.quarter.name == "2º Trimestre":
                        second_quarter = student_schedule_quarter.average
                    if student_schedule_quarter.classes_schedule_quarter.quarter.name == "3º Trimestre":
                        third_quarter = student_schedule_quarter.average               

        quarter_average = (first_quarter + second_quarter + third_quarter) / 3

        return [quarter_average, first_quarter, second_quarter, third_quarter]

    @classmethod
    def get_student_final_grade(cls, classes_student, studyplan_discipline):
        # Caso o discente não esteja a frequentar a disciplina enquestão
        final_grade = None
        #Pesquisa pela prova final do discente
        for student_discipline in classes_student.classe_student_discipline:
            if student_discipline.studyplan_discipline == studyplan_discipline:
                
                for classes_student_avaliation in classes_student.classes_student_avaliation:
                    if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Prova final":                                    
                        final_grade = round(classes_student_avaliation.grade)

        return final_grade

    @classmethod
    def get_student_grades_quarter(cls, classes_student, studyplan_discipline, quarter):
        
        arithmetic_sum  = 0
        weighted_sum = 0
        count_arithmetic = 0 
        #Avaliação de MAC
        mac = 0
        mac_count = 0
        #Prova do professor
        pp = 0
        pp_count = 0
        #prova Trimestral
        pt = 0
        pt_count = 0 

        for classes_student_avaliation in classes_student.classes_student_avaliation:
            if classes_student_avaliation.classes_avaliation.studyplan_discipline == studyplan_discipline:
                if classes_student_avaliation.classes_avaliation.quarter == quarter: 

                    #Verifica se a avaliação tem como operação aritimétrica                                      
                    if classes_student_avaliation.classes_avaliation.studyplan_avaliation.perct_arithmetic == True:
                        
                        #Definição das avaliações que devem aparecer na pauta, de acordo ao critério da instituição
                        if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Avaliação contínua":
                            mac += round(classes_student_avaliation.grade)
                            mac_count += 1
                        if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Prova do professor":
                            pp += round(classes_student_avaliation.grade)
                            pp_count += 1
                        if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Prova trimestral":
                            pt += round(classes_student_avaliation.grade)
                            pt_count += 1                        

                    #Verifica se a avaliação tem como operação percentual
                    if classes_student_avaliation.classes_avaliation.studyplan_avaliation.perct_weighted == True:

                        #Definição das avaliações que devem aparecer na pauta, de acordo ao critério da instituição
                        if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Avaliação contínua":
                            mac += (round(classes_student_avaliation.grade) * (classes_student_avaliation.classes_avaliation.studyplan_avaliation.percent / 100))  
                            
                        if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Prova do professor":
                            pp += (round(classes_student_avaliation.grade) * (classes_student_avaliation.classes_avaliation.studyplan_avaliation.percent / 100))  
                            
                        if classes_student_avaliation.classes_avaliation.studyplan_avaliation.metric_avaliation.avaliation.name == "Prova trimestral":
                            pt += (round(classes_student_avaliation.grade) * (classes_student_avaliation.classes_avaliation.studyplan_avaliation.percent / 100))  

                        #Cálculo das avaliações
                        weighted_sum = mac + pp + pt  

        #Cálculo das avaliações para serem mostradas na pauta
        if mac_count != 0:                    
            mac = mac / mac_count
        if pp_count != 0:
            pp = pp / pp_count
        if pt_count != 0:
            pt = pt / pt_count

        #Operação realizada com base em 3 avaliações
        arithmetic_sum = mac + pp + pt
        count_arithmetic = 3
        
        #Cálculo da média final
        if count_arithmetic > 0:
            #Caso tenha uma avaliação percentuas
            if weighted_sum > 0:
                #Cálculo final é a operação aritimétrica e percentual
                sum = (weighted_sum + (arithmetic_sum / count_arithmetic)) / 2
            else: 
                sum = round((arithmetic_sum / count_arithmetic))

        else:
            sum = weighted_sum   
                
        return [mac, pp, pt, sum]


class PublicHistoricCreateWizardStart(ModelView):
    'PublicHistoricCreate Start'
    __name__ = 'akademy.wizpublichistoric_create.start'
   
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        required=True, help="Informa o nome da turma.")
    
    
class PublicHistoricCreateWizard(Wizard):
    'PublicHistoric Create'
    __name__ = 'akademy.wizpublichistoric_create'

    start_state = 'start'
    start = StateView(
        model_name='akademy.wizpublichistoric_create.start', \
        view='akademy.act_publichistoric_wizard_from', \
        buttons=[
            Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
            Button(string=u'Gerar percurso', state='studenthistoricgrades', icon='tryton-save')
        ]
    )
    studenthistoricgrades = StateTransition()

    def transition_studenthistoricgrades(self):
        Transfrer = Pool().get('akademy.student-transfer')
        average = 0
        count = 0
        discipline = []
        final_grade = 0
        result = 0
        Classes = self.start.classes
        state_student = ['Aguardando', 'Suspenso(a)', 'Anulada', 'Transfêrido(a)', 'Reprovado(a)']
        
        if len(Classes.classe_student) > 0:
            schedule_block  = ClassesSchedule.search([
                ('state', '=', False),
                ('lective_year', '=', Classes.lective_year),
                ('classes', '=', Classes)
            ])
            
            if len(schedule_block) < 1:
                for StudentClasses in Classes.classe_student:
                    #VERIFICA O ESTADO DA MATRÍCULA
                    if StudentClasses.state not in state_student:
                        #Pesquisa pelo discente nas transfêrencias
                        students_transfer = Transfrer.search([
                                ('course_classe', '=', Classes.studyplan.classe), 
                                ('student', '=', StudentClasses.student),
                                ('external', '=', True)
                            ])                    
                                                                
                        if len(StudentClasses.classe_student_discipline) > 0:
                            for student_discipline in StudentClasses.classe_student_discipline:
                                discipline.append(student_discipline)
                                if len(StudentClasses.classes_student_schedule) > 0:
                                    for classes_student_schedule in StudentClasses.classes_student_schedule:
                                        #Verifica se as disciplinas constam no mesmo plano de estudo                            
                                        if classes_student_schedule.classes_schedule.studyplan_discipline == student_discipline.studyplan_discipline:
                                            average += classes_student_schedule.average                                        
                                            count += 1   
                                                                
                                    if count > 0:
                                        result = (average/count)
                                    else:
                                        result = 0
                                                                        
                                    HistoricGrades.public_grade(Classes.lective_year, Classes, StudentClasses, student_discipline.studyplan_discipline, result)                                 
                                    average = 0
                                    count = 0

                                else:
                                    self.raise_user_error("Infelizmente ainda não existem pautas publicadas para o discente "+StudentClasses.student.party.name+", na disciplina de "+student_discipline.studyplan_discipline.discipline.name+", "+Classes.name)            
                        
                        # Quando se tratar de um discente transfêrido                        
                        if len(students_transfer) > 0:
                            #VALIDAR DE ACORDO A DISCIPLINA E CLASSE  
                            studyplan_discipline_exit = []

                            #Faz a equivalencia dos planos de estudo
                            if len(students_transfer[0].student_transfer_discipline) > 0:
                                for studyplan_discipline in Classes.studyplan.studyplan_discipline:          
                                    for student_transfer_discipline in students_transfer[0].student_transfer_discipline:
                                        if student_transfer_discipline.course_classe == Classes.studyplan.classe:
                                            # Verifica se a disciplina do discente é a mesma do plano de estudo 
                                            if (student_transfer_discipline.discipline ==  studyplan_discipline.discipline):
                                                studyplan_discipline_exit.append(studyplan_discipline)                                               
                                                
                                                if (student_transfer_discipline.average >= studyplan_discipline.average):
                                                    final_grade = student_transfer_discipline.average 
                                                    HistoricGrades.public_grade(Classes.lective_year, Classes, StudentClasses, studyplan_discipline, final_grade)
                            
                            #Caso tenha todas as displinas do plano de estudo
                            if len(Classes.studyplan.studyplan_discipline) != len(discipline):                            
                                for studyplan_discipline in Classes.studyplan.studyplan_discipline:                                                                
                                    if StudentClasses.classe_student_discipline == studyplan_discipline.classe_student_discipline:
                                        if studyplan_discipline not in studyplan_discipline_exit and studyplan_discipline not in discipline: 
                                            for classes_schedule in studyplan_discipline.classes_schedule:
                                                if classes_schedule.classes == Classes:
                                                    for classes_student_schedule in classes_schedule.classes_student_schedule:
                                                        if classes_student_schedule.classes_student == StudentClasses:

                                                            final_grade = classes_student_schedule.average                                            
                                                            HistoricGrades.public_grade(Classes.lective_year, Classes, StudentClasses, studyplan_discipline, final_grade)
                                                            final_grade = 0
                                                            count = 0

                            discipline.clear() 
            
            else:
                self.raise_user_error("Infelizmente é possivél gerar o percurso académico porque a pauta final da turma "+Classes.name+", ainda não bloqueada") 

        else:
            self.raise_user_error("Infelizmente não foi possivél lançar as notas no percurso académico, por falta de alunos na turma, ", self.start.classes.name)                                       
        
        return 'end'


class ClassesAvaliation(ModelSQL, ModelView):
    'Classes Avaliation'
    __name__ = 'akademy.classes-avaliation'
    #_rec_name = 'studyplan_avaliation'

    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo', 
        ondelete='CASCADE')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        ondelete='CASCADE',
        domain=[('lective_year', '=', Eval('lective_year', -1))],
        depends=['lective_year'])    
    quarter = fields.Many2One(
		model_name="akademy.quarter",string=u'Trimestre', 
		required=True, help="Escolha o trimestre da pauta.")
    classe_teacher_discipline = fields.Many2One(
        model_name='akademy.classe_teacher-discipline', string=u'Docente', 
        required=True, domain=[('classe_teacher.classes', '=', Eval('classes', -1))],
        depends=['classes'])
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Disciplina', 
        required=True, domain=[('classe_teacher_discipline', '=', Eval('classe_teacher_discipline', -1))],
        depends=['classe_teacher_discipline'])
    studyplan_avaliation = fields.Many2One(
        model_name='akademy.studyplan-avaliation', string=u'Avaliação', 
        required=True, domain=[('studyplan_discipline', '=', Eval('studyplan_discipline', -1))],
        depends=['studyplan_discipline'])
    classes_student_avaliation = fields.One2Many(
        'akademy.classes_student-avaliation', 'classes_avaliation', 
        string="Lista de discentes")

    @classmethod
    def save_classes_avaliation(cls, fields, quarter, studyplan_avaliation):
        classes_avaliation = ClassesAvaliation.search([
            ('lective_year', '=', fields.classes.lective_year),
            ('classes', '=', fields.classes),
            ('quarter', '=', quarter),
            ('studyplan_discipline', '=', fields.studyplan_discipline),
            ('studyplan_avaliation', '=', studyplan_avaliation)
        ])        

        if len(classes_avaliation) <= 0:
            for classe_teacher_discipline in fields.studyplan_discipline.classe_teacher_discipline:
                if classe_teacher_discipline.studyplan_discipline == fields.studyplan_discipline:

                    avaliation = ClassesAvaliation(
                        lective_year = fields.classes.lective_year,
                        classes = fields.classes,
                        quarter = quarter,
                        classe_teacher_discipline = classe_teacher_discipline,
                        studyplan_discipline = fields.studyplan_discipline,
                        studyplan_avaliation = studyplan_avaliation,
                    )
                    avaliation.save()

                    break

        else:
            classes_avaliation[0].write_date = date.today()
            classes_avaliation[0].save()
            avaliation = classes_avaliation[0]
        
        return avaliation    

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.studyplan_avaliation.rec_name)
        return t1


class ClassesStudentAvaliation(ModelSQL, ModelView):
    'Classes-Student Avaliation'
    __name__ = 'akademy.classes_student-avaliation'
    _rac_name = 'classes_avaliation'

    grade = fields.Numeric(string=u'Nota', digits=(2,1))
    presence = fields.Selection(selection=sel_presence, string=u'Presença')
    classes_avaliation = fields.Many2One(
        model_name='akademy.classes-avaliation', string=u'Avaliação', 
        ondelete='CASCADE')
    classes_student = fields.Many2One(
		model_name='akademy.classe-student', string=u'Discente',
        domain=[('classes.classes_avaliation', '=', Eval('classes_avaliation', -1))],
        depends=['classes_avaliation'])
    
    @classmethod
    def default_presence(cls):
        return "Presente"

    @classmethod
    def save_classes_student_avaliation(cls, classe_student, classe_avaliation):
        classes_student_avaliation = ClassesStudentAvaliation.search([
            ('classes_student', '=', classe_student),
            ('classes_avaliation', '=', classe_avaliation)
        ])

        if len(classes_student_avaliation) <= 0:
            
            student_avaliation = ClassesStudentAvaliation(
                grade = 0,
                presence = "Presente",
                classes_avaliation = classe_avaliation,
                classes_student = classe_student
            )
            student_avaliation.save()

        else:
            cls.raise_user_error("O discente já possui uma nota nesta avaliação.")    

    @classmethod
    def __setup__(cls):
        super(ClassesStudentAvaliation, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [            
            ('grade_max', Check(table, table.grade <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('grade_min', Check(table, table.grade >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.')
        ]
        cls._order = [('classes_avaliation', 'ASC')]                         


#Discipline Quarter Schedule 
class ClassesScheduleQuarter(ModelSQL, ModelView):
    'Classes Schedule-Quarter'
    __name__ = 'akademy.classes_schedule-quarter'
    #_rec_name = 'studyplan_discipline'

    code = fields.Char(string=u'Código', size=20)
    state =fields.Boolean(string=u"Bloqueada", help="Bloquear/Desbloquear para a edição.")
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo', 
        ondelete='CASCADE')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        ondelete='CASCADE',
        domain=[('lective_year', '=', Eval('lective_year', -1))],
        depends=['lective_year'])    
    quarter = fields.Many2One(
		model_name="akademy.quarter",string=u'Trimestre', 
		required=True, help="Escolha o trimestre da pauta.")
    schedule = fields.Selection(selection=sel_schedule, string=u'Tipo de pauta')
    classe_teacher_discipline = fields.Many2One(
        model_name='akademy.classe_teacher-discipline', string=u'Docente', 
        required=True, domain=[('classe_teacher.classes', '=', Eval('classes', -1))],
        depends=['classes'])
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Disciplina', 
        required=True, domain=[('classe_teacher_discipline', '=', Eval('classe_teacher_discipline', -1))],
        depends=['classe_teacher_discipline'])
    classes_student_schedule_quarter = fields.One2Many(
        'akademy.classes_student-schedule_quarter', 'classes_schedule_quarter', 
        string="Lista de discentes")

    @classmethod
    def default_state(cls):
        return False

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.studyplan_discipline.rec_name)
        return t1

    #Create a Classe Schedule Quarter
    @classmethod
    def save_classes_schedule_quarter(cls, fields, quarter):        
        for classe_teacher in fields.classes.classe_teacher: 
            for teacher_discipline in classe_teacher.classe_teacher_discipline:
                if teacher_discipline.studyplan_discipline == fields.studyplan_discipline: 
                    
                    schedule_update = ClassesScheduleQuarter.search([
                            ('lective_year', '=', fields.classes.lective_year),
                            ('classes', '=', fields.classes),
                            ('quarter', '=', quarter),
                            ('schedule', '=', fields.schedule),
                            ('classe_teacher_discipline', '=', teacher_discipline),
                            ('studyplan_discipline', '=', fields.studyplan_discipline)
                        ])

                    if len(schedule_update) <= 0:     
                        
                        schedule = ClassesScheduleQuarter (
                            lective_year = fields.classes.lective_year,
                            classes = fields.classes,
                            quarter = quarter,
                            schedule = fields.schedule,
                            classe_teacher_discipline = teacher_discipline,
                            studyplan_discipline = fields.studyplan_discipline
                        )
                        schedule.save()

                        break

                    else:
                        schedule_update[0].write_date = date.today()
                        schedule_update[0].save()
                        schedule = schedule_update[0]
            
        return schedule        


class ClassesStudentScheduleQuarter(ModelSQL, ModelView):
    'Classes_Student-Schedule_Quarter'
    __name__ = 'akademy.classes_student-schedule_quarter'
    _rac_name = 'classes_schedule_quarter'
    
    mac = fields.Numeric(string=u'MAC', digits=(2,1))
    pp = fields.Numeric(string=u'PP', digits=(2,1))
    pt = fields.Numeric(string=u'PT', digits=(2,1))
    average = fields.Numeric(string=u'Média', digits=(2,1))
    classes_schedule_quarter = fields.Many2One(
        model_name='akademy.classes_schedule-quarter', string=u'Pauta', 
        ondelete='CASCADE')
    classes_student = fields.Many2One(
		model_name='akademy.classe-student', string=u'Discente')
        
    @classmethod
    def save_classes_student_schedule_quarter(cls, mac, pp, pt, grade, schedule, classes_student):
        if schedule.state == False:            
            student_schedule_update = ClassesStudentScheduleQuarter.search([
                ('classes_schedule_quarter', '=', schedule),
                ('classes_student', '=', classes_student)
            ])

            if len(student_schedule_update) <= 0:                
                student_schedule = ClassesStudentScheduleQuarter(
                    mac = mac,
                    pp = pp,
                    pt = pt,            
                    average = grade,
                    classes_schedule_quarter = schedule,
                    classes_student = classes_student,
                )
                
                student_schedule.save()

            else:
                student_schedule_update[0].mac = mac
                student_schedule_update[0].pp = pp
                student_schedule_update[0].pt = pt
                student_schedule_update[0].average = grade
                student_schedule_update[0].write_date = date.today()
                student_schedule_update[0].save()

        else:
            cls.raise_user_error("A pauta está bloqueado para edição.")
    
    @classmethod
    def __setup__(cls):
        super(ClassesStudentScheduleQuarter, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [            
            ('mac_max', Check(table, table.mac <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('mac_min', Check(table, table.mac >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('pp_max', Check(table, table.pp <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('pp_min', Check(table, table.pp >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('pt_max', Check(table, table.pt <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('pt_min', Check(table, table.pt >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('average_max', Check(table, table.average <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('average_min', Check(table, table.average >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.')
        ]        


#Discipline Final Schedule 
class ClassesSchedule(ModelSQL, ModelView):
    'Classes Schedule'
    __name__ = 'akademy.classes-schedule'
    #_rec_name = 'studyplan_discipline'

    code = fields.Char(string=u'Código', size=20)
    state =fields.Boolean(string=u"Bloqueada", help="Bloquear/Desbloquear para para a edição.")
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo', 
        ondelete='CASCADE')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        ondelete='CASCADE',
        domain=[('lective_year', '=', Eval('lective_year', -1))],
        depends=['lective_year'])    
    quarter = fields.Many2One(
		model_name="akademy.quarter",string=u'Trimestre', 
		required=True, help="Escolha o trimestre da pauta.")
    schedule = fields.Selection(selection=sel_schedule, string=u'Tipo de pauta')
    classe_teacher_discipline = fields.Many2One(
        model_name='akademy.classe_teacher-discipline', string=u'Docente', 
        required=True, domain=[('classe_teacher.classes', '=', Eval('classes', -1))],
        depends=['classes'])
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Disciplina', 
        required=True, domain=[('classe_teacher_discipline', '=', Eval('classe_teacher_discipline', -1))],
        depends=['classe_teacher_discipline'])
    classes_student_schedule = fields.One2Many(
        'akademy.classes_student-schedule', 'classes_schedule', 
        string="Lista de discentes")

    @classmethod
    def default_state(cls):
        return False

    def get_rec_name(self, name):
        t1 = '%s' % \
            (self.studyplan_discipline.rec_name)
        return t1

    #Create a Classe Schedule
    @classmethod
    def save_classes_schedule(cls, fields):
                    
        count_schedule_lock = 0
        classes_schedule_quarter = ClassesScheduleQuarter.search([
                ('lective_year', '=', fields.classes.lective_year),
                ('classes', '=', fields.classes),
                #('quarter', '=', fields.studyplan_discipline.quarter),
                #('schedule', '=', fields.schedule),
                #classe_teacher_discipline', '=', teacher_discipline),
                ('studyplan_discipline', '=', fields.studyplan_discipline)
            ])

        #Verifica quantas pautas estão trançadas
        for schedule_quarter in classes_schedule_quarter:
            if schedule_quarter.state == True:
                count_schedule_lock += 1

        if len(classes_schedule_quarter) == count_schedule_lock:
        
            for classe_teacher in fields.classes.classe_teacher: 
                for teacher_discipline in classe_teacher.classe_teacher_discipline:
                    if teacher_discipline.studyplan_discipline == fields.studyplan_discipline:      
                        
                        schedule_update = ClassesSchedule.search([
                                ('lective_year', '=', fields.classes.lective_year),
                                ('classes', '=', fields.classes),
                                ('quarter', '=', fields.studyplan_discipline.quarter),
                                ('schedule', '=', fields.schedule),
                                ('classe_teacher_discipline', '=', teacher_discipline),
                                ('studyplan_discipline', '=', fields.studyplan_discipline)
                            ])

                        if len(schedule_update) <= 0: 

                            schedule = ClassesSchedule (
                                lective_year = fields.classes.lective_year,
                                classes = fields.classes,
                                quarter = fields.studyplan_discipline.quarter,
                                schedule = fields.schedule,
                                classe_teacher_discipline = teacher_discipline,
                                studyplan_discipline = fields.studyplan_discipline
                            )
                            schedule.save()
                            
                            break

                        else:
                            schedule_update[0].write_date = date.today()
                            schedule_update[0].save()
                            schedule = schedule_update[0]
            
            return schedule

        else:
            cls.raise_user_error("Infelizmente não foi possivél criar a pauta final de "+fields.studyplan_discipline.discipline.name+", porque a pauta trimestral ainda não foi bloqueada.")


class ClassesStudentSchedule(ModelSQL, ModelView):
    'Classes_Student-Schedule'
    __name__ = 'akademy.classes_student-schedule'
    _rac_name = 'classes_schedule'

    first_quarter = fields.Numeric(string=u'T1', digits=(2,1))
    second_quarter = fields.Numeric(string=u'T2', digits=(2,1))
    third_quarter = fields.Numeric(string=u'T3', digits=(2,1))
    final_grade = fields.Numeric(string=u'PF', digits=(2,1))
    average = fields.Numeric(string=u'Média', digits=(2,1))
    obs = fields.Char(string=u'Observação', size=25)
    classes_schedule = fields.Many2One(
        model_name='akademy.classes-schedule', string=u'Pauta', 
        ondelete='CASCADE')
    classes_student = fields.Many2One(
		model_name='akademy.classe-student', string=u'Discente',
        domain=[('classes.classes_schedule', '=', Eval('classes_schedule', -1))],
        depends=['classes_schedule'])

    @classmethod
    def save_classes_student_schedule(cls, first_quarter, second_quarter, third_quarter, final_grade, student_final_grade, schedule, classes_student, discipline_average):        
        if schedule.state == False:
            if student_final_grade >= discipline_average:
                result = "Aprovado(a)"
            else:
                result = "Reprovado(a)"

            student_schedule_update = ClassesStudentSchedule.search([
                    ('classes_schedule', '=', schedule),
                    ('classes_student', '=', classes_student)
                ])

            if len(student_schedule_update) <= 0:
            
                student_schedule = ClassesStudentSchedule(
                    first_quarter = first_quarter,
                    second_quarter = second_quarter,
                    third_quarter = third_quarter,
                    final_grade = final_grade,
                    average = student_final_grade,
                    obs = result,
                    classes_schedule = schedule,
                    classes_student = classes_student,
                )
                student_schedule.save()
            
            else:
                student_schedule_update[0].first_quarter = first_quarter
                student_schedule_update[0].second_quarter =  second_quarter
                student_schedule_update[0].third_quarter =  third_quarter
                student_schedule_update[0].final_grade = final_grade
                student_schedule_update[0].average = student_final_grade
                student_schedule_update[0].obs = result
                student_schedule_update[0].write_date = date.today()
                student_schedule_update[0].save()   

        else:
            cls.raise_user_error("A pauta está bloqueado para edição.")

    @classmethod
    def __setup__(cls):
        super(ClassesStudentSchedule, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [            
            ('first_quarter_max', Check(table, table.first_quarter <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('first_quarter_min', Check(table, table.first_quarter >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('second_quarter_max', Check(table, table.second_quarter <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('second_quarter_min', Check(table, table.second_quarter >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('third_quarter_max', Check(table, table.third_quarter <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('third_quarter_min', Check(table, table.third_quarter >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('final_grade_max', Check(table, table.final_grade <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('final_grade_min', Check(table, table.final_grade >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.'),           
            ('average_grade_max', Check(table, table.average <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('average_grade_min', Check(table, table.average >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.')
        ]           


class HistoricGrades(ModelSQL, ModelView):
    'Student Grades'
    __name__ = 'akademy.historic-grades'
        
    code = fields.Char(string=u'Código', size=20)
    average = fields.Numeric(string=u'Média', digits=(2,1))
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo',
        ondelete='CASCADE')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        domain=[('lective_year', '=', Eval('lective_year', -1))],
        depends=['lective_year'])
    student = fields.Many2One(
		model_name='akademy.classe-student',
		string=u'Discente',
        ondelete='CASCADE')
    studyplan_discipline = fields.Many2One(
		model_name='akademy.studyplan-discipline', 		
		string=u'Disciplina')
    
    @classmethod
    def default_average(cls):
        return 0 

    @classmethod
    def public_grade(cls, lective_year, classes, student, discipline, average):
        HistoricGrade = Pool().get('akademy.historic-grades') 
        StudentDiscipline = Pool().get('akademy.classe_student-discipline')        

        state_matriculation = StudentDiscipline.search([('classe_student', '=', student), ('studyplan_discipline', '=', discipline)])
        schedule = [] 
        state_student = ['Aguardando', 'Suspenso(a)', 'Anulada', 'Transfêrido(a)', 'Reprovado(a)']

        #CASO TENHA ENCNTRADO UM DISCENTE
        if len(state_matriculation) > 0:
            #VERIFICA O ESTADO DA MATRÍCULA
            if state_matriculation[0].state not in state_student:                               
                
                student_historic_grades = HistoricGrade.search([('lective_year', '=',lective_year ), ('classes', '=', classes), ('student', '=', student), ('studyplan_discipline', '=', discipline)])
                #ATUALIZA A NOTA
                if len(student_historic_grades) > 0:
                    student_historic_grades[0].average = round(average)
                    student_historic_grades[0].save()                    
                #LANÇA A NOTA
                else:
                    HistoricGrades.save_historic_grades(schedule, HistoricGrade, lective_year, classes, student, discipline, average)

                #Muda o estado da matrícula na disciplina
                HistoricGrades.matriculation_discipline_state(average, discipline, state_matriculation[0])
                
        else:
            if student.type not in state_student:
                HistoricGrades.save_historic_grades(schedule, HistoricGrade, lective_year, classes, student, discipline, average)
            else:
                student_historic_grades = HistoricGrade.search([('lective_year', '=',lective_year ), ('classes', '=', classes), ('student', '=', student), ('studyplan_discipline', '=', discipline)])

                if len(student_historic_grades) > 0:
                    student_historic_grades[0].average = round(average)
                    student_historic_grades[0].save()
                else:
                    HistoricGrades.save_historic_grades(schedule, HistoricGrade, lective_year, classes, student, discipline, average)            

    @classmethod
    def save_historic_grades(cls, schedule, HistoricGrades, lective_year, classes, student, discipline, average):
        schedule = HistoricGrades(
            code = discipline.discipline.code,
            lective_year = lective_year,
            classes = classes,
            student = student,
            studyplan_discipline = discipline,
            average = round(average)
        )    
        schedule.save() 

    @classmethod
    def matriculation_discipline_state(cls, student_average, discipline, student_discipline):
        #MUDA O ESTADO DA MATRÍCULA DO DISCENTE NA DISCIPLINA
        if round(student_average) >= discipline.average:
            student_discipline.state = "Aprovado(a)"
            student_discipline.save()
        else:
            student_discipline.state = "Reprovado(a)"
            student_discipline.save()               

    @classmethod
    def __setup__(cls):
        super(HistoricGrades, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
			('key',
			Unique(table, table.classes, table.student, table.studyplan_discipline, table.lective_year),
			u'Não foi possivél lançar a nota do discente no percurso académico, por favor verifica se a uma nota lançada nesta disciplina.'),
            ('max_average', Check(table, table.average <= 20),
            u'Não foi possivél lançar a nota do discente, por favor verifica se a média é superior a 20 valores.'),
            ('min_average', Check(table, table.average >= 0),
            u'Não foi possivél lançar a nota do discente, por favor se a média é inferior a 0 valores.')
        ]
        cls._order = [('classes', 'ASC')] 

