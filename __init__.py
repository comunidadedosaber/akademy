from trytond.pool import Pool
from . import configuration
from . import matriculation
from . import party
from . import company
from . import classes
from . import avaliation
from . import report

def register():
    Pool.register(
        configuration.LectiveYear,
        configuration.SchoolChart,
        configuration.Quarter,
        configuration.Area,
        configuration.Course,
        configuration.Classe,
        configuration.CourseClasse,
        configuration.AcademicLevel,
        configuration.TimeCourse, 
        configuration.MetricAvaliation,
        configuration.Avaliation,
        configuration.AvaliationType,
        configuration.Discipline,
        configuration.ApplicationCriteria,
        configuration.Phase,
        configuration.ClasseRoom,
        configuration.StudyPlan, 
        configuration.StudyPlanDiscipline,
        configuration.DisciplinePrecedents,
        configuration.StudyPlanAvaliation,
        matriculation.Candidates, 
        matriculation.Applications,
        matriculation.ApplicationsResult,
        matriculation.StudentTransfer,
        matriculation.StudentTransferDiscipline,
        party.Party,
        company.Employee,
        company.CompanyStudent,
        classes.Classes, 
        classes.ClasseTimeRule,
        classes.ClasseStudent,
        classes.ClasseStudentDiscipline, 
        classes.ClasseTeacher, 
        classes.ClasseTeacherDiscipline,
        classes.ClasseTeacherLesson,
        classes.AssociationDisciplineCreateWzardStart,
        matriculation.MatriculationCreateWzardStart, 
        avaliation.ClassesAvaliation,
        avaliation.ClassesStudentAvaliation,
        avaliation.ClassesSchedule,
        avaliation.OtherSchedule,
        avaliation.StudentSchedule,
        avaliation.ClassesStudentSchedule,
        avaliation.ClassesScheduleQuarter,
        avaliation.ClassesStudentScheduleQuarter,
        avaliation.HistoricGrades,
        avaliation.PublicGradesCreateWizardStart,
        avaliation.PublicHistoricCreateWizardStart,
        avaliation.ScheduleCreateWizardStart,
        
        module='akademy', type_='model'
    )

    Pool.register(
        classes.AssociationDisciplineCreateWzard,
        matriculation.MatriculationCreateWzard,
        avaliation.PublicGradesCreateWizard,
        avaliation.PublicHistoricCreateWizard,
        avaliation.ScheduleCreateWizard,

        module='akademy', type_='wizard'
    )

    Pool.register(
        report.StudyplanReport,
        report.ApplicationCriteriaReport,
        report.AcademicLevelReport,
        report.ApplicationResultReport,
        report.CandidatesReport,
        report.MatriculationReport,
        report.StudentTransferReport,
        report.StudentTransferInternalReport,
        report.EquivalenceDisciplineReport,
        report.ClassesReport,
        report.MatriculationTeacherReport,
        report.ScheduleDisciplineReport,
        report.ScheduleDisciplineFinalReport,
        report.ClassesDisciplineLessonsReport,
        report.StudentDeclarationReport,
        report.StudentDeclarationGradesReport,
        report.StudentGradesReport,
        report.StudentCertificateReport,

        module='akademy', type_='report')
