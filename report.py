from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime, date

__all_ = ['StudyplanReport', 'AppCriteriaReport', 'AcademicLevelReport'
		'ApplicationResultReport','CandidatesReport', 'StudentTransferReport', 'MatriculationReport', 
		'MatriculationTeacherReport', 'ClassesReport', 'ScheduleDisciplineFinalReport', 'ScheduleDisciplineReport', 'ClassesDisciplineLessonsReport',
		'StudentDeclarationReport', 'StudentGradesReport', 'StudentDeclarationGradesReport', 'StudentCertificateReport',
		'EquivalenceDisciplineReport']

#REPORT PLANOS DE ESTUDO
class StudyplanReport(Report):
	__name__ = 'akademy.studyplan-report'

	@classmethod
	def get_context(cls, records, data):
		Studyplan = Pool().get('akademy.studyplan')

		context = super().get_context(records, data)
		studyplan = Studyplan.browse(data['ids'])
        
		context['studyplans'] = studyplan
		context['create_date'] = date.today()

		return context


#REPORT CRITÉRIO DE ADMISSÃO
class ApplicationCriteriaReport(Report):
	__name__ = 'akademy.application_criteria-report'

	@classmethod
	def get_context(cls, records, data):
		ApplicationCriteria = Pool().get('akademy.application-criteria')

		context = super().get_context(records, data)
		appcriteria = ApplicationCriteria.browse(data['ids'])

		context['appcriterias'] = appcriteria
		context['create_date'] = date.today()
		
		return context


#REPORT NÍVEL ACADÉMICO
class AcademicLevelReport(Report):
	__name__ = 'akademy.academic_level-report'

	@classmethod
	def get_context(cls, records, data):
		AcademicLevel = Pool().get('akademy.academic-level')

		context = super().get_context(records, data)
		academic_level = AcademicLevel.browse(data['ids'])

		context['academic_level'] = academic_level
		context['create_date'] = date.today()

		return context


#REPORT PAUTA DE EXAME DE ACESSO
class ApplicationResultReport(Report):
	__name__ = 'akademy.application_criteria-report'

	@classmethod
	def get_context(cls, records, data):
		ApplicationsResult = Pool().get('akademy.application-criteria')

		context = super().get_context(records, data)
		result = ApplicationsResult.browse(data['ids'])
        
		context['result'] = result
		context['create_date'] = date.today()

		return context


#REPORT CANDIDATE
class CandidatesReport(Report):
	__name__ = 'akademy.candidates-report'

	@classmethod
	def get_context(cls, records, data):		
		Candidates = Pool().get('akademy.candidates')

		context = super().get_context(records, data)
		candidate = Candidates.browse(data['ids'])

		context['candidates'] = candidate
		context['create_date'] = date.today()

		return context


#REPORT DISCENTE TRANSFERIDO
class StudentTransferReport(Report):
	__name__ = 'akademy.student_transfer-report'

	@classmethod
	def get_context(cls, records, data):
		StudentTransfer = Pool().get('akademy.student-transfer')

		context = super().get_context(records, data)
		student = StudentTransfer.browse(data['ids'])
		
		list_students = StudentCertificateReport.student_academy_histori(student[0].student.student)
		
		context['student'] = student
		context['list_students'] = list_students
		context['create_date'] = date.today()

		return context


#REPORT DISCENTE TRANSFERIDO EQUIVALENCIA
class EquivalenceDisciplineReport(Report):
	__name__ = 'akademy.equivalence_discipline-report'

	@classmethod
	def get_context(cls, records, data):
		StudentTransfer = Pool().get('akademy.student-transfer')        
		Studyplan = Pool().get('akademy.studyplan')

		context = super().get_context(records, data)
		students = StudentTransfer.browse(data['ids'])

		get_student_equivalence = []
		get_student_discipline = []
		get_studyplan_discipline = []
		discipline_exit = []		

		#PROCESSO DE EQUIVALENCIAS
		for student in students:
			#Verifica se a tranfêrencia é interna ou externa
			if student.internal == True:
				pass
			else:
				get_studyplan = Studyplan.search([
					#('classe', '=', student.course_classe.classe),
					('area', '=', student.area),
					('course', '=', student.course)
				])  
				
				#BUSCA TODAS AS DISCIPLA DO PLANO DE ESTUDO
				for studyplan in get_studyplan:
					for studyplan in get_studyplan:
							for studyplan_discipline in studyplan.studyplan_discipline:
								if studyplan_discipline not in discipline_exit:
									discipline_exit.append(studyplan_discipline)
									get_studyplan_discipline.append([studyplan_discipline.discipline.name, studyplan.classe.classe.name, 0])								
				
				# VERIFICA SE O DISCENTE TÊM DISCIPLINA, NA TRANSFÊRENCIA
				if len(student.student_transfer_discipline) > 0:
					for student_transfer_discipline in student.student_transfer_discipline:											
						if student_transfer_discipline not in discipline_exit:
							discipline_exit.append(student_transfer_discipline)
							get_student_discipline.append([student_transfer_discipline.discipline.name, student_transfer_discipline.course_classe.classe.name, student_transfer_discipline.average])
			
				get_student_equivalence.append(student)
		
		if student.internal == True:
			context['students'] = [student]
			context['discipline'] = []
			context['create_date'] = date.today()

			return context
						
		else:
			student_has_discipline = []
			student = []
			discipline = []

			for student_equivalence in get_student_equivalence:				
				student_discipline_exit = []
				student.append(student_equivalence)

				for studyplan_discipline in get_studyplan_discipline:
					st_discipline_state = False
					if studyplan_discipline not in student_discipline_exit:
						student_discipline_exit.append(studyplan_discipline)
						st_discipline_exit = []
						for student_discipline in get_student_discipline:
							if student_discipline not in st_discipline_exit:
								st_discipline_exit.append(student_discipline)
								if (student_discipline[0] == studyplan_discipline[0]) and (student_discipline[1] == studyplan_discipline[1]):									
									student_has_discipline.append(student_discipline)
									discipline.append(student_discipline)

									st_discipline_state = True
						if st_discipline_state == False:
							discipline.append(studyplan_discipline)

				for student_discipline in get_student_discipline:
							if student_discipline not in student_has_discipline:
								discipline.append(student_discipline)
			
			context['students'] = student
			context['discipline'] = discipline
			context['create_date'] = date.today()

			return context


#REPORT BOLETIM DE MATRÍCULA
class MatriculationReport(Report):
	__name__ = 'akademy.matriculation-report'

	@classmethod
	def get_context(cls, records, data):
		Matriculation = Pool().get('akademy.classe-student')

		context = super().get_context(records, data)
		matriculation = Matriculation.browse(data['ids'])

		context['matriculation'] = matriculation
		context['create_date'] = date.today()

		return context


#REPORT BOLETIM DE MATRÍCULA DOCENTE
class MatriculationTeacherReport(Report):
	__name__ = 'akademy.matriculation_teacher-report'

	@classmethod
	def get_context(cls, records, data):
		Matriculation = Pool().get('akademy.classe-teacher')

		context = super().get_context(records, data)
		matriculations = Matriculation.browse(data['ids'])		

		context['matriculation'] = matriculations
		context['create_date'] = date.today()

		return context


#REPORT TURMA
class ClassesReport(Report):
	__name__ = 'akademy.classes-report'

	@classmethod
	def get_context(cls, records, data):
		Classes = Pool().get('akademy.classes')

		context = super().get_context(records, data)
		classes = Classes.browse(data['ids'])

		context['classes'] = classes
		context['create_date'] = date.today()

		return context


#REPORT BOLETIM DE NOTAS
class StudentGradesReport(Report):
	__name__ = 'akademy.student_grades-report'

	@classmethod
	def get_context(cls, records, data):
		StudentGrades = Pool().get('akademy.classe-student')

		context = super().get_context(records, data)
		student = StudentGrades.browse(data['ids'])

		context['student_grades'] = student
		context['create_date'] = date.today()

		return context


#REPORT PAUTA DISCIPINA
class ScheduleDisciplineReport(Report):
	__name__ = 'akademy.schedule_discipline-report'

	@classmethod
	def get_context(cls, records, data):
		TeacherDiscipline = Pool().get('akademy.classe_teacher-discipline')
		Quarter = Pool().get('akademy.quarter')

		context = super().get_context(records, data)
		teacher_discipline = TeacherDiscipline.browse(data['ids'])		

		schedule = []
		student_number = 0		
		#Verifica o trimestre com base na data actual	
		quarter = Quarter.search([('start', '<=', date.today()), ('end', '>=', date.today())])

		classes_schedule = Pool().get('akademy.classes-grades')

		for discipline in teacher_discipline:
			for classe_student_discipline in discipline.studyplan_discipline.classe_student_discipline:	
				if classe_student_discipline.studyplan_discipline.discipline == discipline.studyplan_discipline.discipline:
				
					#Pesquisa pela pauta do discente na disciplina
					discipline_schedule = classes_schedule.search([
						('lective_year', '=', discipline.classe_teacher.classes.lective_year),
						('classes', '=', discipline.classe_teacher.classes),
						('quarter', '=', quarter[0]),
						('student_discipline', '=', classe_student_discipline),
						#('employee', '=', discipline.classe_teacher.employee.id)
					])
					
					#Incrementa o número de ordem
					student_number = student_number +1
					#Lista de discentes
					schedule.append(
						(
							student_number,
							discipline_schedule[0].student_discipline.classe_student.student.party.name,
							discipline_schedule[0].mac,
							discipline_schedule[0].pp,
							discipline_schedule[0].pt,
							discipline_schedule[0].value
						)
					
					)			

		context['discipline'] = teacher_discipline
		context['schedule'] = schedule
		context['quarter'] = quarter[0]
		context['create_date'] = date.today()

		return context



#REPORT PAUTA FINAL DISCIPINA
class ScheduleDisciplineFinalReport(Report):
	__name__ = 'akademy.schedule_discipline_final-report'

	@classmethod
	def get_context(cls, records, data):
		TeacherDiscipline = Pool().get('akademy.classe_teacher-discipline')

		context = super().get_context(records, data)
		teacher_discipline = TeacherDiscipline.browse(data['ids'])	

		schedule = []
		student_number = 0
		classes_schedule = Pool().get('akademy.discipline-schedule')

		for discipline in teacher_discipline:			
			#Pesquisa pela pauta do discente na disciplina
			discipline_schedule = classes_schedule.search([
				('lective_year', '=', discipline.classe_teacher.classes.lective_year),
				('classes', '=', discipline.classe_teacher.classes),
				#('quarter', '=', quarter[0]),
				('studyplan_discipline', '=', discipline.studyplan_discipline),
				('employee', '=', discipline.classe_teacher.employee)
			])
			
			for student in discipline_schedule:
				#Incrementa o número de ordem					
				student_number = student_number +1

				#Verifica se o discente aprova ou reprova
				if student.value >= discipline.studyplan_discipline.average:
					obs = "Aprovado(a)"
				else:
					obs = "Reprovado(a)"

				#Lista de discentes
				schedule.append(
					(
						student_number,
						student.student.student.party.name,
						student.first_quarter,
						student.second_quarter,
						student.third_quarter,
						student.value,
						obs
					)				
				)			

		context['discipline'] = teacher_discipline
		context['schedule'] = schedule
		context['create_date'] = date.today()

		return context



#REPORT PLANO DE AULA
class ClassesDisciplineLessonsReport(Report):
	__name__ = 'akademy.classes_discipline-lessons_report'

	@classmethod
	def get_context(cls, records, data):
		TeacherDisciplineLessons = Pool().get('akademy.classe_teacher-lesson')

		context = super().get_context(records, data)
		discipline_lessons = TeacherDisciplineLessons.browse(data['ids'])

		context['discipline_lessons'] = discipline_lessons
		context['create_date'] = date.today()

		return context


#REPORT DECLARAÇÃO SEM NOTAS / DECLARAÇÃO DE MATRÍCULA
class StudentDeclarationReport(Report):
	__name__ = 'akademy.student_declaration-report'

	@classmethod
	def get_context(cls, records, data):
		StudentDeclaration = Pool().get('akademy.classe-student')

		context = super().get_context(records, data)
		declaration = StudentDeclaration.browse(data['ids'])

		context['declaration'] = declaration
		context['create_date'] = date.today()

		return context


#REPORT DECLARAÇÃO COM NOTAS
class StudentDeclarationGradesReport(Report):
	__name__ = 'akademy.student_declaration_grades-report'

	@classmethod
	def get_context(cls, records, data):
		StudentDeclaration = Pool().get('akademy.classe-student')

		context = super().get_context(records, data)
		declaration_grades = StudentDeclaration.browse(data['ids'])

		context['declaration_grades'] = declaration_grades
		context['create_date'] = date.today()

		return context


#REPORT CERTIFICADO
class StudentCertificateReport(Report):
	__name__ = 'akademy.student_certificate-report'

	@classmethod
	def get_context(cls, records, data):
		StudentCertificate = Pool().get('akademy.classe-student')

		context = super().get_context(records, data)
		certificates = StudentCertificate.browse(data['ids'])

		list_students = StudentCertificateReport.student_academy_histori(certificates)

		context['certificate'] = certificates
		context['list_students'] = list_students[0]
		context['list_students_transfer'] = list_students[1]		
		context['create_date'] = date.today()

		return context

	@classmethod
	def student_academy_histori(cls, students):
		#Busca as nostas no percurso acadêmico do discente
		list_students = []
		list_students_transfer = []

		for certificate in students:
			for course in certificate.classes.studyplan.course.course_classe:
				for classes in course.classe.classes:					
					for student in classes.classe_student:						
						if student.student.party.name in certificate.student.party.name:
							#Verifica se o discemnte já existe na lista
							if student not in list_students:
								#Pega todas as matrículas do aluno, e suas respectivas notas
								list_students.append(student)

								#Verifica se o discente é transfêrido							
								if student.type == "Transfêrido(a)":
									for student_transfer in student.student.student_transfer:
										for student_transfer_discipline in student_transfer.student_transfer_discipline:
											#Pega as notas do discente na disciplina
											if student_transfer_discipline.course_classe != course:
												list_students_transfer.append(student_transfer_discipline)

		return [list_students,list_students_transfer]
