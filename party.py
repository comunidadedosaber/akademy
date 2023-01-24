from trytond.model import fields
from trytond.pyson import Eval, Not, Bool
from trytond.pool import PoolMeta
from .varibales import sel_sex, sel_marital_status

# extende o modulo party.party adicionando alguns campos.

__all__ = ['Party']
#__metaclass__ = PoolMeta


class Party(metaclass = PoolMeta):
    'Party'
    __name__ = 'party.party'
    _rec_name = 'name'
       
    is_person = fields.Boolean(
        string=u'Pessoa', 
        states={
            'invisible': Bool(Eval('is_institution')), 
            'required': Not(Bool(Eval('is_institution')))
        }, depends=['is_institution'], 
        help='A entidade é uma pessoa.')
    is_institution = fields.Boolean(
        string=u'Instituição', 
        states={
            'invisible':  Bool(Eval('is_person')), 
            'required': Not(Bool(Eval('is_person')))
        }, depends=['is_person'], 
        help='A entidade é uma instituição ou organização.')
    date_birth = fields.Date(
        string=u'Nascimento', 
        states={
            'invisible': Not(Bool(Eval('is_person'))), 
            'required': Bool(Eval('is_person'))            
        }, help='Data de nascimento.')    
    gender = fields.Selection(
        selection=sel_sex, string=u'Genêro',         
        states={
            'invisible': Not(Bool(Eval('is_person'))), 
            'required': Bool(Eval('is_person'))
        })
    marital_status = fields.Selection(
        selection=sel_marital_status, string=u'Estado Civil', 
        states={
            'invisible': Not(Bool(Eval('is_person'))), 
            'required': Bool(Eval('is_person'))
        })
    bi_number = fields.Char(
        string=u'B.I nº', size=15,
        states={
            'invisible': Not(Bool(Eval('is_person'))), 
            'required': Bool(Eval('is_person'))
        }, help="Número do bilhete de intidade.")
    father = fields.Many2One(
        model_name='party.party', string=u'Pai',
        states={'invisible': Not(Bool(Eval('is_person')))}, 
        help="Nome do pai.")
    mother = fields.Many2One(
        model_name='party.party',  string=u'Mãe',
        states={'invisible': Not(Bool(Eval('is_person')))}, 
        help="Nome da mãe.")
    student = fields.One2Many('company.student', 'party', string=u'Discente')
    candidates = fields.One2Many('akademy.candidates', 'party', string=u'Candidato')

