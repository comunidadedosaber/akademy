from trytond.model import ModelView, ModelSQL, fields, Unique, Check
from trytond.pyson import Eval, Id, And
from trytond.wizard import Button, Wizard, StateView, StateTransition
from trytond.pool import Pool
from trytond.transaction import Transaction
from datetime import date
from .varibles import sel_modality, sel_state_teacher, sel_state_student, sel_registration_type, sel_classes_time, sel_lesson_type

__all_ = ['Classes', 'ClasseStudent', 'ClasseStudentDiscipline', 'ClasseTeacher', 'ClasseTeacherDiscipline', 
		'ClasseTimeRlue', 'ClasseTeacherLesson',
		'AssociationDisciplineCreateWizard', 'AssociationDisciplineCreateWizardStart']


class Classes(ModelSQL, ModelView):
	'Classes'
	__name__ = 'akademy.classes'
	
	code = fields.Char(string=u'Código', size=20,
		help="Código da turma.")
	name = fields.Char(string=u'Nome', required=True,
		help="Nome da turma.")	
	max_student = fields.Integer(string=u'Total de discentes', 
		help=u'Limite máximo de discentes por adcionar na turma.')
	max_teacher = fields.Integer(string=u'Total de docentes', 
		help=u'Limite máximo de docentes por adcionar na turma.')
	modality = fields.Selection(selection=sel_modality, string=u'Modalidade', required=True) 
	classe = fields.Many2One(
		model_name='akademy.classe', string=u'Classe', 
		required=True, help="Nome da classe.")
	time_course = fields.Many2One(
		model_name='akademy.time-course', string=u'Periódo', 
		required=True)
	lective_year = fields.Many2One(
		model_name="akademy.lective-year", string=u'Ano lectivo', 
		required=True, help="Nome do ano lectivo.")
	studyplan = fields.Many2One(model_name='akademy.studyplan', string=u'Plano de estudo', required=True) 
	coordinator = fields.Many2One(
		model_name="company.employee", string=u'Coordenador',
		domain=[('employee', '=', True)], help=u'Nome do coordenador do plano de estudo.')
	company = fields.Many2One(string=u'Company', model_name='company.company',
        states={
            'readonly': 
                ~And(
                    Id('res', 'group_admin').in_(Eval('context', {}).get('groups', [])),
                    Eval('id', -1) == -1
                ),
        }, required=True, select=True)
	classe_timerule = fields.One2Many('akademy.classe-timerule', 'classes', string=u'Horário')
	classe_student = fields.One2Many('akademy.classe-student', 'classes', string=u'Discente')
	classe_teacher = fields.One2Many('akademy.classe-teacher', 'classes', string=u'Docente')
	stundent_grades = fields.One2Many('akademy.classe_student-grades', 'classes', string=u'Discente nota')
	classes_grades = fields.One2Many('akademy.classes-grades', 'classes', string=u'Avaliações')
	historic_grades = fields.One2Many('akademy.historic-grades', 'classes', string="Percurso académico")
	classe_teacher_lesson = fields.One2Many('akademy.classe_teacher-lesson', 'classes', string="Plano de aula")		
		
	@classmethod
	def default_modality(cls):
		return "Presencial"

	@classmethod
	def default_max_student(cls):
		return 1

	@classmethod
	def default_max_teacher(cls):
		return 1

	@classmethod
	def default_company(cls):
		""" set active company to default
		"""
		context = Transaction().context
		return context.get('company')

	#Ao clicar no botão avaliar estado da matrícula
	@classmethod
	@ModelView.button
	def matriculation_state(cls, classes):
		discipline_required = []
		student_discipline_possitive = []

		for classes_list in classes:
			for studyplan_discipline in classes_list.studyplan.studyplan_discipline:
				if studyplan_discipline.state == "Obrigatório":
					discipline_required.append(studyplan_discipline)

			for classes_student in classes_list.classe_student:
				count = 0
				for historic_grades in classes_student.historic_grades:
					if (historic_grades.studyplan_discipline in discipline_required) and (classes_student.classe_student_discipline[count].state == "Aprovado(a)"):
						student_discipline_possitive.append(historic_grades.studyplan_discipline)
					count += 1

				#Muda o estado da matrícula na turma
				Classes.matriculation_classes_state(discipline_required, student_discipline_possitive, classes_student)
								
				student_discipline_possitive.clear()	
			discipline_required.clear()

	@classmethod
	def matriculation_classes_state(cls, discipline_required, student_discipline, classes_student):
		#MUDA O ESTADO DA MATRÍCULA DO DISCENTE NA TURMA
		if len(discipline_required) == len(student_discipline):
			state = "Aprovado(a)"
		else:
			state = "Reprovado(a)"
		
		classes_student.state =	state
		classes_student.save()

		Classes.matriculation_student_state(classes_student.student, state)
		
	@classmethod
	def matriculation_student_state(cls, company_student, state):
		#MUDA O ESTADO DA MATRÍCULA NO ANO LECTIVO
		company_student.state = state
		company_student.save()			
	
	@classmethod
	def __setup__(cls):
		super(Classes, cls).__setup__()
		table = cls.__table__()
		cls._sql_constraints = [
			('key', Unique(table, table.name, table.classe, table.lective_year),
			u'Não foi possível cadastrar a nova turma, por favor verifica se já existe uma turma com este nome para este ano lectivo.'),
            ('student', Check(table, table.max_student > 0),
            u'Não foi possível adicionar o discente a turma, por favor verifica se o limite de vagas para existente na turma, para os discentes.'),
            ('teacher', Check(table, table.max_teacher > 0),
            u'Não foi possível adicionar o docente na turma, por favor verifica se o limite de vagas para existente na turma, para os docentes.')
		]

		cls._buttons.update({
			'matriculation_state':{
				'visible': True
			}
		})


class ClasseStudent(ModelSQL, ModelView):
	'Classe Student'
	__name__ = 'akademy.classe-student'
		
	description = fields.Text(string=u'Descrição')
	state = fields.Selection(selection=sel_state_student,  string=u'Estado', 
		required=True, help="Escolha o estado da matrícula.")
	type = fields.Selection(
		selection=sel_registration_type, string=u'Tipo', 
		required=True, help="Escolha o tipo de matrícula.")
	student = fields.Many2One(
		model_name='company.student', string=u'Nome', 
		required=True, ondelete='CASCADE')
	classes = fields.Many2One(
		model_name='akademy.classes', string=u'Turma', 
		required=True)
	classe_student_discipline = fields.One2Many(
		'akademy.classe_student-discipline', 'classe_student', 
		string=u'Discente disciplina')
	classes_grades = fields.One2Many(
		'akademy.classes-grades', 'student', 
		string=u'Pautas')
	student_grades = fields.One2Many(
        'akademy.classe_student-grades', 'student',
        string=u'Avaliacões')	
	historic_grades = fields.One2Many(
        'akademy.historic-grades', 'student',
        string=u'Percurso académico')

	@classmethod
	def default_state(cls):
		return "Matrículado(a)"

	@classmethod
	def default_type(cls):
		return "Transição de classe"

	def get_rec_name(self, name):
		t1 = '%s' % \
			(self.student.rec_name)
		return t1

	@classmethod
	def __setup__(cls):
		super(ClasseStudent, cls).__setup__()
		table = cls.__table__()
		cls._sql_constraints = [
			('key', Unique(table, table.student, table.classes), 
			u'Não foi possivél cadastrar o novo discente, por favor verifica se o discente já está matriculado nesta turma.')
		]
		#cls._buttons.update({
        #    'discipline_association_button':{
        #        'invisible': Eval('state')
        #    }
        #}) 
		cls._order = [('student', 'ASC')]
		
	
class ClasseStudentDiscipline(ModelSQL, ModelView):
	'StudentDiscipline'
	__name__ = 'akademy.classe_student-discipline'

	state = fields.Selection(
		selection=sel_state_student, string=u'Estado', 
		select=True, required=True, 
		help="Escolha o estado da matrícula.")
	modality = fields.Selection(
		selection=sel_modality, string=u'Modalidade', 
		select=True, required=True, 
		help="Escolha o tipo de frequência.")	
	studyplan = fields.Function(
		fields.Integer(
			string=u'Plano de estudo'
		), 'on_change_with_studyplan')
	classe_student = fields.Many2One(
		model_name='akademy.classe-student', string=u'Discente', 
		required=True)
	studyplan_discipline = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Disciplina', 
		required=True, domain=[('studyplan.id', '=', Eval('studyplan', -1))],
		depends=['studyplan'])
	student_grades = fields.One2Many(
		'akademy.classe_student-grades', 'student_discipline', 
		string=u'Discente nota')
	classes_grades = fields.One2Many(
		'akademy.classes-grades', 'student_discipline', 
		string=u'Avaliações')

	@fields.depends('classe_student')
	def on_change_with_studyplan(self, name=None):
		return self.classe_student.classes.studyplan.id

	@classmethod
	def default_modality(cls):
		return "Presencial"

	def get_rec_name(self, name):
		t1 = '%s' % \
			(self.studyplan_discipline.rec_name)
		return t1
	
	@classmethod
	def __setup__(cls):
		super(ClasseStudentDiscipline, cls).__setup__()
		table = cls.__table__()
		cls._sql_constraints = [
			('uniq_classes', Unique(table, table.classe_student, table.studyplan_discipline),
			u'Não foi possivél associar o discente a discipline, por favor verica se o discente já está a frequentar está disciplina nesta turma.')
		]


class ClasseTeacher(ModelSQL, ModelView):
	'Classe Teacher'
	__name__ = 'akademy.classe-teacher'
	#_rec_name = 'employee'
	
	state = fields.Selection(
		selection=sel_state_teacher, string=u'Estado', 
		required=True, help="Seleciona um estado para matrícula.")
	description = fields.Text(string=u'Descrição')
	employee = fields.Many2One(
		model_name='company.employee', string=u'Nome', 
		required=True, ondelete='CASCADE')
	classes = fields.Many2One(
		model_name='akademy.classes', string=u'Turma', 
		required=True)
	classe_teacher_discipline = fields.One2Many(
		'akademy.classe_teacher-discipline', 'classe_teacher', 
		string=u'Associar disciplina')
	classe_teacher_lesson = fields.One2Many(
		'akademy.classe_teacher-lesson', 'classe_teacher', 
		string="Plano de aula")

	@classmethod
	def default_state(cls):
		return "Matrículado(a)"
	
	def get_rec_name(self, name):
		t1 = '%s' % \
			(self.employee.rec_name)
		return t1
	
	@classmethod
	def __setup__(cls):
		super(ClasseTeacher, cls).__setup__()
		table = cls.__table__()
		cls._sql_constraints += [
			('key', Unique(table, table.employee, table.classes), 
			u'Não foi possivél matricular o docente, por favor verifica se o docente já existe na turma.')
		]
		cls._order = [('employee', 'ASC')]	
	

class ClasseTeacherDiscipline(ModelSQL, ModelView):
	'TeacherDiscipline'
	__name__ = 'akademy.classe_teacher-discipline'
	#_rec_name = 'studyplan_discipline'
		
	state = fields.Selection(
		selection=sel_state_teacher, string=u'Estado', 
		required=True, help="Escolha o estado da matrícula.")
	modality = fields.Selection(
		selection=sel_modality, string=u'Modalidade', 
		select=True, required=True, 
		help="Escolha o tipo de frequência.")			
	studyplan = fields.Function(
		fields.Integer(
			string='Plano de Estudo', 
			required=True
		), 'on_change_with_studyplan')
	classe_teacher = fields.Many2One(
		model_name='akademy.classe-teacher', string=u'Docente', 
		required=True)
	studyplan_discipline = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Disciplina', 
		required=True, domain=[('studyplan.id', '=', Eval('studyplan', -1))],
		depends=['studyplan'],)
	classe_teacher_lesson = fields.One2Many(
		'akademy.classe_teacher-lesson', 'classe_teacher_discipline', 
		string="Plano de aula")
		
	@fields.depends('classe_teacher')
	def on_change_with_studyplan(self, name=None):
		return self.classe_teacher.classes.studyplan.id

	@classmethod
	def default_state(cls):
		return "Matrículado(a)"

	@classmethod
	def default_modality(cls):
		return "Todas"
	
	def get_rec_name(self, name):
		t1 = '%s' % \
			(self.studyplan_discipline.rec_name)
		return t1

	@classmethod
	def __setup__(cls):
		super(ClasseTeacherDiscipline, cls).__setup__()
		table = cls.__table__()
		cls._sql_constraints = [
			('key', Unique(table, table.classe_teacher, table.studyplan_discipline),
			u'Não foi possivél associar o docente a disciplina, por favor verifica se o mesmo já está a lecionar esta disciplina na turma.')
		]


class ClasseTimeRule(ModelSQL, ModelView):
	'Classe TimeRule'
	__name__ = 'akademy.classe-timerule'
	_order_name = 'lesson_time'

	lesson_time = fields.Selection(selection=sel_classes_time, string=u'Tempo', required=True)
	start_lesson = fields.Time(string=u'Entrada', format='%H:%M', required=True)
	end_lesson = fields.Time(string=u'Saída', format='%H:%M', required=True)	
	studyplan = fields.Function(
		fields.Integer(
			string='Plano de Estudo', 
			required=True
		), 'on_change_with_studyplan')			
	classes = fields.Many2One(
		model_name='akademy.classes', 
		string=u'Turma', required=True)	
	mon = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Segunda-Feira', 
		domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
		depends=['studyplan'], help=u'Escolha a disciplina.')
	tue = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Terça-Feira', 
		domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
		depends=['studyplan'], help=u'Escolha a disciplina.')
	wed = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Quarta-Feira', 
		domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
		depends=['studyplan'], help=u'Escolha a disciplina.')
	thu = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Quinta-Feira', 
		domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
		depends=['studyplan'], help=u'Escolha a disciplina')
	fri = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Sexta-Feira', 
		domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
		depends=['studyplan'], help=u'Escolha a disciplina.')
	sat = fields.Many2One(
		model_name='akademy.studyplan-discipline', string=u'Sábado', 
		domain=[('studyplan.id', '=', Eval('studyplan', -1))], 
		depends=['studyplan'], help=u'Escolha a disciplina.')
	mon_room = fields.Many2One(
		model_name='akademy.classe-room', string=u'Sala', 
		help=u'Escolha a sala de aula em que a disciplina vai ser lecionada.')
	tue_room = fields.Many2One(
		model_name='akademy.classe-room', string=u'Sala', 
		depends=['studyplan'], help=u'Escolha a sala de aula em que a disciplina vai ser lecionada.')
	wed_room = fields.Many2One(
		model_name='akademy.classe-room', string=u'Sala', 
		depends=['studyplan'], help=u'Escolha a sala de aula em que a disciplina vai ser lecionada.')
	thu_room = fields.Many2One(
		model_name='akademy.classe-room', string=u'Sala', 
		depends=['studyplan'], help=u'Escolha a sala de aula em que a disciplina vai ser lecionada.')
	fri_room = fields.Many2One(
		model_name='akademy.classe-room', string=u'Sala', 
		depends=['studyplan'], help=u'Escolha a sala de aula em que a disciplina vai ser lecionada.')
	sat_room = fields.Many2One(
		model_name='akademy.classe-room', string=u'Sala', 
		depends=['studyplan'], help=u'Escolha a sala de aula em que a disciplina vai ser lecionada.')		

	@fields.depends('classes')
	def on_change_with_studyplan(self, name=None):
		return self.classes.studyplan.id

	@classmethod
	def __setup__(cls):
		super(ClasseTimeRule, cls).__setup__()
		table = cls.__table__()
		cls._sql_constraints = [
			('key', Unique(table, table.lesson_time, table.classes),
			u'Não foi possivél definir o tempo lectivo para a turma, por favor verifica se o tempo lectivo já existe para este horário.')
		]


class ClasseTeacherLesson(ModelSQL, ModelView):
	'Classes Lesson'
	__name__ = 'akademy.classe_teacher-lesson'

	lesson_number = fields.Integer(string=u'Lição nº', help="Insira o número da aula.")	
	objective = fields.Text(string=u'Objectivos')
	unidate = fields.Char(string=u'Unidade')
	summary = fields.Text(string=u'Sumário')
	lesson_date = fields.Date(string=u'Data', required=True)
	lesson_type = fields.Selection(
		selection=sel_lesson_type, string=u'Tipo de aula', 
		help="Seleciona um tipo de aula.")
	classes = fields.Many2One(
		model_name='akademy.classes', string=u'Turma', required=True, 
		domain=[('classe_teacher', '=', Eval('classe_teacher', -1))],
		depends=['classe_teacher'])
	classe_timerule = fields.Many2One(
		model_name='akademy.classe-timerule', string=u'Horário', required=True, 
		domain=[('classes', '=', Eval('classes', -1))],
		depends=['classes'])
	classe_teacher_discipline = fields.Many2One(
		model_name='akademy.classe_teacher-discipline', 
		string=u'Disciplina')
	classe_teacher = fields.Many2One(
		model_name='akademy.classe-teacher', string=u'Docente', required=True,
		domain=[('classe_teacher_discipline', '=', Eval('classe_teacher_discipline', -1))],
		depends=['classe_teacher_discipline'])
	
	@classmethod
	def default_lesson_date(cls):
		return date.today()


#Assistente
class AssociationDisciplineCreateWzardStart(ModelView):
	'AssociationDiscipline CreateStart'
	__name__ = 'akademy.wizassociatiodiscipline_create.start'

	classes = fields.Many2One(
		model_name='akademy.classes', string=u'Turma',
		help="Caro utilizador será feita uma associação entre os estudentes desta turma e as displinas existentes no plano de estudo."
	)


class AssociationDisciplineCreateWzard(Wizard):
	'AssociationDiscipline CreateWzard'
	__name__ = 'akademy.wizassociatiodiscipline_create'

	start_state = 'start'
	start = StateView(
		model_name='akademy.wizassociatiodiscipline_create.start', \
		view="akademy.act_associationdiscipline_wizard_from", \
		buttons=[
			Button(string=u'Cancelar', state='end', icon='tryton-cancel'),
			Button(string=u'Associar', state='association', icon='tryton-save')
		]
	)
	association = StateTransition()

	def transition_association(self):		
		Student_Discipline = Pool().get('akademy.classe_student-discipline')

		state_student = ['Aguardando', 'Suspenço(a)', 'Anulada', 'Transfêrido(a)']
		list_matriculation = 0

		for classe_student in self.start.classes.classe_student:
			#VERIFICA O ESTADO DA MATRÍCULA
			if classe_student.state not in state_student:
				for studyplan_discipline in self.start.classes.studyplan.studyplan_discipline:
					matriculaton_discipline = Student_Discipline.search([('classe_student', '=', classe_student), ('studyplan_discipline', '=', studyplan_discipline)])

					#Efectua a matrícula do discente na disciplina
					if (len(matriculaton_discipline) < 1):
						list_matriculation = 1
						matriculaton = Student_Discipline(
							classe_student = classe_student,
							studyplan = self.start.classes.studyplan,
							studyplan_discipline = studyplan_discipline,
							state = "Matrículado(a)",
							modality = "Presencial"

						)
						matriculaton.save()
		
		if list_matriculation == 0:
			self.raise_user_error("Não foi possivél associar disciplina aos discentes desta turma, todas as disciplinas já foram associadas")
					
		return 'end'
