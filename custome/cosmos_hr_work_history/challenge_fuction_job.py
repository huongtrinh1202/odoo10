# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from datetime import datetime
from urlparse import urljoin
from urllib import urlencode, quote as quote
from openerp.tools.translate import _

class challenge_function_job(osv.osv):
    _name = 'challenge.function.job'
    _inherit = 'mail.thread'
    _description = 'Thu thach chuc vu, vi tri cong viec.'
    _order = 'date_to desc'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Nhân viên', required=True, track_visibility='onchange'),
        'name': fields.related('employee_id', 'name', type='char', string='Tên'),
        'job_id': fields.many2one('hr.job', 'Vị trí thử thách', track_visibility='onchange'),
        'date_from': fields.date('Từ ngày', required=True, track_visibility='onchange'),
        'fuction_id': fields.many2one('res.function.groups', 'Chức vụ thử thách', track_visibility='onchange'),
        'date_to': fields.date('Đến ngày', required=True, track_visibility='onchange'),
        'level_allowance': fields.many2one('level.allowance.bonus', 'Mức phụ cấp trách nhiệm', track_visibility='onchange'),
        'times_challenge': fields.many2one('cosmos.times.challenge', 'Lần thử thách', track_visibility='onchange'),
        'note': fields.text('Ghi chú', track_visibility='onchange'),
        'state': fields.selection([('effective','Đang hiệu lực'),('no_pass','Không đạt'),('pass','Không đạt')], 'Trạng thái', track_visibility='onchange'),
        }
    
    _defaults = {
        'state': 'effective',
        }
    
    #Thêm bởi Hương 08/07/2016 hàm thực thi xử lý cron
    def challenge_fuction_job_expired(self, cr, uid, context=None):
        if context ==None:
            context={}
        local_context=context.copy() 
        #Lấy id của email teamplate
        template_email_for_reviewer = self.pool.get('ir.model.data').get_object(cr, uid, 'cosmos_hr_work_history', "email_template_challenge_fuction_job")
        #B1 Lấy tất cả công ty
        company_ids= self.pool.get('res.company').search(cr,uid,[],context)
        #Lấy id của nhóm Quản lý thử thách chức vụ, vị trí
        group_challenge_function_job_ids= self.pool.get('ir.model.data').get_object(cr, uid, 'base','group_challenge_function_job')
        #B2: Đối với với mỗi công ty ở B1 thực hiện
        for company_id in company_ids:
            #B2.1 : Lấy tổng số dòng những thử thách thỏa mãn tất cả điều kiện sau
            #Trạng thái = Đang hiệu lực 
            #Đến ngày < Ngày hiện tại
            #Thuộc tính Công ty của field Nhân viên = Công ty đang xét
            cr.execute("select count(j.id) as sl from challenge_function_job j inner join hr_employee hr on j.employee_id = hr.id inner join resource_resource r on hr.resource_id = r.id where r.company_id = %s and j.state = 'effective' and j.date_to < date(now())" % company_id)
            item = cr.dictfetchone()
            company_obj= self.pool.get('res.company').browse(cr, uid, company_id,context)
            if item['sl'] >0:
                #Hàm lấy danh sách người phê duyệt dựa trên nhóm
                group_users=self.pool.get('approval.request.common').get_approver_by_group(cr, uid, group_id=group_challenge_function_job_ids.id, company=company_obj, context=context)
                for user_id in group_users:
                    local_context.update({
                        'is_not_footer': True,
                        'email_template_obj' : template_email_for_reviewer
                    })
                    #B2.2.2 : Đối với mỗi user ở B2.2.1 gửi email
                    self.pool['email.template'].send_mail(cr, uid, template_email_for_reviewer.id, user_id, force_send=True, raise_exception=False, context=local_context)
        return True
                    
class cosmos_times_challenge(osv.osv):
    _name = 'cosmos.times.challenge'
    _columns = {
        'name': fields.char('Tên'),
        }