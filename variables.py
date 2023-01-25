
#Variáveis Globais
sel_state = (
    ('Obrigatório', 'Obrigatório'), ('Opcional', 'Opcional')
)

sel_trimestre = (
    ('1º Trimestre', '1º Trimestre'), ('2º Trimestre', '2º Trimestre'), 
    ('3º Trimestre', '3º Trimestre'), ('Anual', 'Anual')
)

sel_precent = (
    ('Média aritmétrica','Média aritmétrica'), ('Média ponderada','Média ponderada')
)

sel_reference = (
    ('Particular', 'Particular'), ('Deficiente', 'Deficiente'), 
    ('Antigo combatente', 'Antigo combatente'), ('Bolseiro', 'Bolseiro')
)

sel_modality = (
	('Presencial', 'Presencial'), ('Não presencial', 'Não presencial'), 
	('Virtual', 'Virtual'), ('Todas', 'Todas')
)

sel_category = (
	('Discente', 'Discente'), ('Docente','Docente')
)

sel_state_teacher = (
	('Matrículado(a)', 'Matrículado(a)'), ('Aguardando', 'Aguardando'), 
	('Suspenço(a)', 'Suspenço(a)'), ('Transfêrido(a)', 'Transfêrido(a)')
)

sel_state_student = (
	('Matrículado(a)', 'Matrículado(a)'), ('Aguardando', 'Aguardando'), 
	('Suspenço(a)', 'Suspenço(a)'), ('Anulada', 'Anulada'), 
	('Transfêrido(a)', 'Transfêrido(a)'), ('Reprovado(a)', 'Reprovado(a)'),
    ('Aprovado(a)', 'Aprovado(a)')
)

sel_registration_type = (
    ('Candidato(a)', 'Candidato(a)'), ('Transfêrido(a)', 'Transfêrido(a)'), 
    ('Repitente', 'Repitente'), ('Transição de classe', 'Transição de classe')
)

sel_type_enrollment = (
    ('Iniciação', 'Iniciação'), ('Transição de classe', 'Transição de classe')
)

sel_presence = (
    ('Presente', 'Presente'), ('Faltou', 'Faltou'),
    ('Espluso', 'Espluso')
)

sel_sex = (
    (None, ''),
    ('Masculino', 'Masculino'), ('Femenino', 'Femenino') 
)

sel_marital_status = (
    (None, ''),
    ('Solteiro(a)', 'Solteiro(a)'), ('Casado(a)', 'Casado(a)'),
    ('Divorciado(a)', 'Divorciado(a)'), ('Víuvo(a)', 'Víuvo(a)')
)

sel_classes_time = (
    ('1º Tempo', '1º Tempo'),
    ('2º Tempo', '2º Tempo'),
    ('3º Tempo', '3º Tempo'),
    ('4º Tempo', '4º Tempo'),
    ('5º Tempo', '5º Tempo'),
    ('6º Tempo', '6º Tempo'),
    ('7º Tempo', '7º Tempo'),
)

sel_result = (
    ('Analizando', 'Analizando'),
    ('Admitido', 'Admitido'),
    ('Não Admitido', 'Não Admitido'),
    ('Lista de Espera', 'Lista de Espera')
)

#Report Variables
sel_report_configuration = (
    ('Área', 'Área'),
    ('Plano de estudo', 'Plano de estudo'),
    ('Critério de admissão', 'Critério de admissão')
)

sel_report_classes = (
    ('Candidaturas', 'Candidaturas'),
    ('Boletim de matrícula', 'Boletim de Matrícula'),
    ('Turma', 'Turma'),
    ('Mini pauta', 'Mini pauta'),
    ('Percurso académico', 'Percurso académico'),
    ('Certificado', 'Certificado'),
    ('Declaração com notas', 'Declaração com notas'),
    ('Declaração sem notas', 'Declaração sem notas')
) 

sel_report_entidate = (
    ('Discentes', 'Discentes'),
    ('Docentes', 'Docentes'),
    ('Funcrionários', 'Funcionários')
)

sel_report_type = (
    ('Indivídual', 'Indivídual'),
    ('Coletivo', 'Coletivo')
)

sel_schedule = (
    (None, 'Seleciona uma opção'), ('Pauta da disciplina', 'Pauta da disciplina')
)

sel_lesson_type = (
    ('Teórica', 'Teórica'),
    ('Prática', 'Prática'),
)

sel_course_yaer = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
)

#RH - GA
sel_position = (
    ('Direitor administrativo', 'Direitor administrativo'),('Direitor pedagógico', 'Direitor pedagógico'),
    ('Coordenator', 'Coordenator'), ('Sub-coordenator', 'Sub-coordenator'),
)