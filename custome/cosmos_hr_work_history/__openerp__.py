# -*- coding: utf-8 -*-
{
    'name' : 'Cosmos HR Management Work History ',
    'version' : '1.0',
    'author' : 'quyenduy@icsc.vn',
    'category': 'icsc',
    'sequence': 1,
    'description': """Installer for HR Management Work History.""",
    'website': 'https://www.icsc.vn',
    'depends' : ['mail','base', 'cosmos_hr_base','cosmos_info_management','cosmos_hr_contract'],
    'data': [
             'security/ir.model.access.csv',
             'security/hr_work_security.xml',
             'work_history_view.xml',
             'challenge_fuction_job.xml',
             'edi/mail_data.xml',
             'challenge_fuction_job_cron.xml',
             'update_auto_empl_infor_cron.xml',
             'sequence_view.xml'
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
