from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pool import Pool
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval
from datetime import date
from .varibales import sel_presence, sel_schedule

__all__ = ['PublicGradesCreateWizard', 'PublicGradesCreateWizardStart', 
        'ScheduleCreateWizard', 'ScheduleCreateWizardStart',
        'PublicHistoricCreateWizard', 'PublicHistoricCreateWizardStart',
        'ClasseStudentGrades', 'ClassesGrades', 'HistoricGrades']


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
            Button(string=u'Gerar lista de discentes', state='studentgrades', icon='tryton-save')
        ]
    )
    studentgrades = StateTransition()

    def transition_studentgrades(self): 
        ClassesStudent = Pool().get('akademy.classe-student')
        StudentClasses = ClassesStudent.search([('classes', '=', self.start.classes)])
        StudentGrades= Pool().get('akademy.classe_student-grades') 
        Quarter= Pool().get('akademy.quarter') 

        #Verifica se o trimestre foi selecionado
        if self.start.quarter.studyplan_avaliations:        
            quarter_metric = Quarter.search([('start', '<=', date.today()), ('end', '>=', date.today())])
            quarter_metric = quarter_metric[0].studyplan_avaliations
        else:
            quarter_metric = self.start.quarter.studyplan_avaliations

        #ESTADO DA MATRÍCULA
        state_student = ['Aguardando', 'Suspenço(a)', 'Anulada', 'Transfêrido(a)']
        
        for Student in StudentClasses:
            #VERIFICA O ESTADO DA MATRÍCULA
            if Student.state not in state_student: 
                for StudentDiscipline in Student.classe_student_discipline:
                    #Verifica se a disciplina a ser lançada a nota e a mesma que foi selecionada
                    if StudentDiscipline.studyplan_discipline == self.start.studyplan_discipline:
                        for studyplan_avaliations in quarter_metric:
                            #Verifica se a avaliação a ser lançada a nota e a mesma que foi selecionada  
                            for avaliation in StudentDiscipline.studyplan_discipline.studyplan_avaliations:                     
                                if studyplan_avaliations == avaliation:  
                                    if studyplan_avaliations.metric_avaliation == self.start.metric_avaliation:  
                                        #Lança a nota nas avaliações
                                        ClasseStudentGrades = StudentGrades(
                                            quarter = self.start.quarter,
                                            lective_year = self.start.classes.lective_year,
                                            studyplan = self.start.studyplan_discipline.studyplan.id,
                                            classes = self.start.classes,
                                            studyplan_discipline = self.start.studyplan_discipline,
                                            student = StudentDiscipline.classe_student,
                                            student_discipline = StudentDiscipline,
                                            studyplan_avaliation = avaliation,
                                            #employee = 
                                            #value = teacher_defined_grade
                                        )
                                        ClasseStudentGrades.save() 

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
        Quarter = Pool().get('akademy.quarter') 
        m = "mini"

        if self.start.schedule == m:
            # Verifica se o trimestre foi em selecionado
            if self.start.quarter:        
                quarter_metric = self.start.quarter
            else:
                #Verifica qual é a metrica com base na data actual
                quarter_metric = Quarter.search([('start', '<=', date.today()), ('end', '>=', date.today())])
                quarter_metric = quarter_metric[0]
            
            ScheduleCreateWizard.mini_schedule(self.start.classes, self.start.studyplan, self.start.studyplan_discipline, self.start.schedule, quarter_metric)               

        return 'end'

    @classmethod
    def mini_schedule(cls, classes, studyplan, studyplan_discipline, schedule, quarter):        
        arithmetic_sum  = 0
        weighted_sum = 0
        count_arithmetic = 0
        schedule_list = []        
        state_student = ['Aguardando', 'Suspenço(a)', 'Anulada', 'Transfêrido(a)']

        for student in classes.classe_student:
            #VERIFICA O ESTADO DA MATRÍCULA
            if student.state not in state_student:            
                for student_discipline in student.classe_student_discipline:
                    #Verifica se o plano de estudo disciplina é o mesmo
                    if student_discipline.studyplan_discipline == studyplan_discipline:                    
                        for grades in student_discipline.student_grades:
                            #Verifica se o trimstre é o mesmo     
                            if grades.quarter == quarter:  
                                #Verifica se a avaliação tem como operação aritimétrica                                      
                                if grades.studyplan_avaliation.perct_arithmetic == True:
                                    arithmetic_sum += grades.value
                                    count_arithmetic += 1
                                #Verifica se a avaliação tem como operação percentual
                                if grades.studyplan_avaliation.perct_weighted == True:
                                    weighted_sum += (grades.value * (grades.studyplan_avaliation.percent / 100))                                                        
                                
                        if count_arithmetic != 0:
                            #Caso tenha uma avaliação percentuas
                            if weighted_sum != 0:
                                #Cálculo final é a operação aritimétrica e percentual
                                sum = (weighted_sum + (arithmetic_sum / count_arithmetic)) / 2
                            else: 
                                sum = (arithmetic_sum / count_arithmetic)
                        else:
                            sum = weighted_sum

                        schedule_list.append(
                            (
                                classes.lective_year,
                                classes,
                                quarter,
                                schedule,
                                student,
                                student_discipline,
                                sum,
                                studyplan,
                                studyplan_discipline             
                            )
                        )
                        
                        arithmetic_sum  = 0
                        weighted_sum = 0
                        count_arithmetic = 0

        #Criação de pautas
        if len (schedule_list) > 0:
            ClassesGrades.schedule_grade(schedule_list)
        else:
            cls.raise_user_error("Infelizmente não foi possivél criar a pauta, porque os estudantes ainda não possuem avaliações lançadas.")


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
            Button(string=u'Gerar lista de discentes', state='studenthistoricgrades', icon='tryton-save')
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
        state_student = ['Aguardando', 'Suspenço(a)', 'Anulada', 'Transfêrido(a)']
        
        if len(Classes.classe_student) > 0:
            for StudentClasses in Classes.classe_student:
                #VERIFICA O ESTADO DA MATRÍCULA
                if StudentClasses.state not in state_student:
                    #Pesquisa pelo discente nas transfêrencias
                    students_transfer = Transfrer.search([('course_classe', '=', Classes.studyplan.classe), ('student', '=', StudentClasses)])
                                                            
                    if len(StudentClasses.classe_student_discipline) > 0:
                        for student_discipline in StudentClasses.classe_student_discipline:
                            discipline.append(student_discipline)
                            if len(StudentClasses.classes_grades) > 0:
                                for grades in StudentClasses.classes_grades:
                                    #Verifica se as disciplinas constam no mesmo plano de estudo                            
                                    if grades.student_discipline.studyplan_discipline == student_discipline.studyplan_discipline:
                                        average += grades.value                                        
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
                                        for discipline_grades in studyplan_discipline.classe_student_discipline:
                                            for student_grades in discipline_grades.classes_grades:
                                                final_grade += student_grades.value
                                                count += 1
                                            
                                            if count > 0:
                                                final_grade = (final_grade/count)
                                            else:
                                                final_grade = 0
                                            
                                        HistoricGrades.public_grade(Classes.lective_year, Classes, StudentClasses, studyplan_discipline, final_grade)
                                        final_grade = 0
                                        count = 0

                        discipline.clear()                                                           
                else:
                    self.raise_user_error("Infelizmente o discente "+StudentClasses.student.party.name+", ainda não têm disciplinas associadas na, "+Classes.name)                                              
        else:
            self.raise_user_error("Infelizmente não foi possivél lançar as notas no percurso académico, por falta de alunos na turma, ", self.start.classes.name)                                       
        
        return 'end'

                            
class ClasseStudentGrades(ModelSQL, ModelView):
    'Classe Student Grades'
    __name__ = 'akademy.classe_student-grades'

    code = fields.Char(string=u'Código', size=20)
    value = fields.Numeric(string=u'Nota', digits=(2,1))
    presence = fields.Selection(selection=sel_presence, string=u'Presença')
    studyplan = fields.Function(
		fields.Integer(
			string=u'Plano de estudo'
		), 'on_change_with_studyplan')
    employee = fields.Function(
        fields.Many2One(
            model_name='company.employee', string=u'Docente'
        ), 'on_change_with_employee', searcher='search_company') 
    quarter = fields.Many2One(
		model_name="akademy.quarter",  string=u'Trimestre', 
		required=True, help="Escolha o trimestre em que a avaliação será lecionada.")
    lective_year = fields.Many2One(
        model_name='akademy.lective-year', string=u'Ano lectivo',  
        required=True)  
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma', 
        required=True)
    student = fields.Many2One(
		model_name='akademy.classe-student', string=u'Discente',
        required=True, domain=[('classes', '=', Eval('classes', -1))],
        depends=['classes'])
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Disciplina',
        domain=[('studyplan.id', '=', Eval('studyplan', -1))],
        depends=['studyplan'])
    student_discipline = fields.Many2One(
        model_name='akademy.classe_student-discipline', string=u'Disciplina', 
        required=True, domain=[('classe_student', '=', Eval('student', -1))],
        depends=['student'])
    studyplan_avaliation = fields.Many2One(
        model_name='akademy.studyplan-avaliation', string=u'Avaliação', 
        required=True)
            
    @fields.depends('studyplan_discipline')
    def on_change_with_employee(self, name=None): 
        for classe_teacher in self.classes.classe_teacher:
            for teacher_discipline in classe_teacher.classe_teacher_discipline:                
                if (teacher_discipline.studyplan == self.classes.studyplan.id) and (teacher_discipline.studyplan_discipline == self.student_discipline.studyplan_discipline):                    
                    return classe_teacher.employee.id
    
    @classmethod
    def search_company(cls, name, clause):
        """ search in company
        """
        return [('classes.company',) + tuple(clause[1:])]

    @fields.depends('classes')
    def on_change_with_studyplan(self, name=None): 
        if self.classes:
            return self.classes.studyplan.id
        else:
            return None 
    
    @classmethod
    def default_presence(cls):
        return "Presente"

    @classmethod
    def default_value(cls):
        return 0

    @classmethod
    def __setup__(cls):
        super(ClasseStudentGrades, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', 
            Unique(table, table.lective_year, table.quarter, table.classes, table.student_discipline, table.studyplan_avaliation), 
            u'Não foi possível atribuir a nota da avaliação, porque o discente já possui uma nota neste ano lectivo e disciplina.'),
            ('grade_max', Check(table, table.value <= 20),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é superior a 20 valores.'),
            ('grade_min', Check(table, table.value >= 0),
            u'Não foi possível atribuir a nota ao discente, por favor se a nota é inferior a 0 valores.')
        ]            


#ClassesSchedule  
class ClassesGrades(ModelSQL, ModelView):
    'Classes Grades'
    __name__ = 'akademy.classes-grades'

    code = fields.Char(string=u'Código', size=20)
    value = fields.Numeric(string=u'Nota', digits=(2,1))
    studyplan = fields.Function(
		fields.Integer(
			string=u'Plano de estudo'
		), 'on_change_with_studyplan')
    quarter = fields.Many2One(
		model_name="akademy.quarter",string=u'Trimestre', 
		required=True, help="Escolha o trimestre da pauta.")
    schedule = fields.Selection(selection=sel_schedule, string=u'Tipo de pauta')
    lective_year = fields.Many2One(model_name='akademy.lective-year', string=u'Ano lectivo', ondelete='CASCADE')
    classes = fields.Many2One(
        model_name='akademy.classes', string=u'Turma',
        ondelete='CASCADE',
        domain=[('lective_year', '=', Eval('lective_year', -1))],
        depends=['lective_year'])
    student = fields.Many2One(
		model_name='akademy.classe-student', string=u'Discente',
        domain=[('classes', '=', Eval('classes', -1))],
        depends=['classes'])
    student_discipline = fields.Many2One(
		model_name='akademy.classe_student-discipline', string=u'Disciplina',
        required=True, domain=[('classe_student', '=', Eval('student', -1))],
        depends=['student'])
    studyplan_discipline = fields.Many2One(
        model_name='akademy.studyplan-discipline', string=u'Plano de estudo - Disciplina',
        domain=[('studyplan.id', '=', Eval('studyplan', -1))],
        depends=['studyplan'])
    employee = fields.Function(
        fields.Many2One(
            model_name='company.employee', string=u'Docente'
        ), 'on_change_with_employee', searcher='search_company')

    @fields.depends('studyplan_discipline')
    def on_change_with_employee(self, name=None): 
        for classe_teacher in self.classes.classe_teacher:
            for teacher_discipline in classe_teacher.classe_teacher_discipline:                
                if (teacher_discipline.studyplan == self.classes.studyplan.id) and (teacher_discipline.studyplan_discipline == self.student_discipline.studyplan_discipline):                                   
                    return classe_teacher.employee.id        
    
    @classmethod
    def search_company(cls, name, clause):
        """ search in company
        """
        return [('classes.company',) + tuple(clause[1:])]

    @fields.depends('classes')
    def on_change_with_studyplan(self, name=None): 
        return self.classes.studyplan.id 

    @classmethod
    def default_value(cls):
        return 0 

    @classmethod
    def schedule_grade(cls, student_list):
        StudentSchedule = Pool().get('akademy.classes-grades') 
        schedule = []     

        for list in student_list: 
            student_update_grade = StudentSchedule.search(
                [
                    ('student', '=', list[4]), 
                    ('student_discipline', '=', list[5]),
                    ('schedule', '=', list[3]),
                    ('quarter', '=' ,list[2]),
                    ('classes', '=' ,list[1]),
                ]
            )
            
            if len(student_update_grade) > 0:
                student_update_grade[0].value = round(list[6])
                student_update_grade[0].save()
            else:                
                schedule = StudentSchedule(
                    code = list[5].studyplan_discipline.discipline.code,
                    lective_year = list[0],
                    classes = list[1],
                    quarter = list[2],
                    schedule = list[3],
                    student = list[4],
                    student_discipline = list[5],
                    value = round(list[6]),
                    studyplan = list[7],
                    studyplan_discipline = list[8]
                )  
                schedule.save() 

    @classmethod
    def __setup__(cls):
        super(ClassesGrades, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
			('key',
			Unique(table, table.classes, table.student, table.student_discipline, table.lective_year, table.quarter),
			u'Não foi possivél lançar a nota do discente, por favor verifica se o discente já têm uma média na disciplina.'),
            ('max_value', Check(table, table.value <= 20),
            u'Não foi possivél lançar a nota do discente, por favor verifica se a média é superior a 20 valores.'),
            ('min_value', Check(table, table.value >= 0),
            u'Não foi possivél lançar a nota do discente, por favor se a média é inferior a 0 valores.')
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
        state_student = ['Aguardando', 'Suspenço(a)', 'Anulada', 'Transfêrido(a)']

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
                    HistoricGrades.save_historic_grades(cls, schedule, HistoricGrade, lective_year, classes, student, discipline, average)            

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
