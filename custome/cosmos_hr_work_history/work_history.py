# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from datetime import datetime
from openerp import tools, SUPERUSER_ID

class cosmos_addendum_contract(osv.osv):
    _inherit = 'cosmos.addendum.contract'
    _columns={ 'work_history_id': fields.many2one('cosmos.work.history','Điều chỉnh nhân sự')}

class cosmos_decisions_manage(osv.osv):
    _inherit = 'cosmos.decisions.manage'
    _columns={ 'work_history_id': fields.many2one('cosmos.work.history','Điều chỉnh nhân sự')}
    
class cosmos_work_history(osv.osv):
    _name='cosmos.work.history'
    _description = 'Lich su lam viec cua nhan vien.'
    _inherit = ['mail.thread']
    _order = 'date desc'
    
    #Hàm kiểm tra user hiện tại có đủ thẩm quyền phê duyệt hay không
    def _check_is_approver(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        approval_obj = self.pool.get('approval.request.common')
        for data in self.browse(cr, uid, ids, context):
            try:
                res[data.id] = approval_obj.check_is_approver(cr,uid,reference_class=self,item_id=data.id,context=context)
            except:
                res[data.id] = False
        return res
    
    
    #Hàm kiểm tra đã phải cấp duyệt cuối hay chưa
    def _check_is_final_approval_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        approval_obj = self.pool.get('approval.request.common')
        for data in self.browse(cr, uid, ids, context):
            try:
                res[data.id] = approval_obj.check_is_final_approval_level(cr,uid, context=context)
            except:
                res[data.id] = False
        return res
    
    
    #Hàm kiểm tra người dùng hiện tại có phải người lập hay không
    def _check_is_owner(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = (data.create_uid.id==uid)
        return res
    
    _columns = {
                'need_update_employee_infor' : fields.boolean('invisible'),
                'name':fields.char('Mã', readonly=True,track_visibility='onchange'),
                'possition_appro': fields.many2one('res.groups','Thẩm quyền duyệt',required=True,track_visibility='onchange'),
                'employee_id': fields.many2one('hr.employee','Nhân viên', required=True,track_visibility='onchange'),
                'create_date' : fields.date('Ngày lập',readonly=True),
                'create_uid' : fields.many2one('res.users','Người lập',readonly=True),
                'date' : fields.date('Ngày hiệu lực',track_visibility='onchange'),
                'unit_old' : fields.many2one('hr.department','Đơn vị cũ',readonly=True,track_visibility='onchange'),
                'unit_new' : fields.many2one('hr.department','Đơn vị mới',required=True,track_visibility='onchange'),
                'company_old' : fields.many2one('res.company','Công ty cũ',readonly=True,track_visibility='onchange'),
                'company_new' : fields.many2one('res.company','Công ty mới',required=True,track_visibility='onchange'),
                'possition_old' : fields.many2one('res.function.groups','Chức vụ cũ',readonly=True,track_visibility='onchange'),
                'possition_new' : fields.many2one('res.function.groups','Chức vụ mới',required=True,track_visibility='onchange'),
                'job_ids_old' : fields.many2many('hr.job', 'work_employee_rel', 'work_id', 'job_id','Vị trí kiêm nhiệm công việc cũ' ,readonly=True,track_visibility='onchange'),
                'job_ids_new' : fields.many2many('hr.job', 'work_employee_new_rel', 'work_new_id', 'job_new_id','Vị trí kiêm nhiệm công việc mới',track_visibility='onchange'),
                'job_pri_old' : fields.many2one('hr.job','Vị trí công việc chính cũ',readonly=True,track_visibility='onchange'),
                'job_pri_new' : fields.many2one('hr.job','Vị trí công việc chính mới',required=True,track_visibility='onchange'),
                'salarylevel_old' : fields.many2one('cosmos.rank.salary','Mức lương cũ',readonly=True,track_visibility='onchange'),
                'salarylevel_new' : fields.many2one('cosmos.rank.salary','Mức lương mới',track_visibility='onchange'),
                'state' : fields.selection([('draft','Dự thảo'),('waitting_confirm','Chờ xác nhận'),('waitappro','Chờ duyệt'),('appro','Đã duyệt'),('reject','Đã từ chối')],'Trạng thái',readonly=True,track_visibility='onchange'),
                'temporary_transfers': fields.boolean('Là điều chuyển tạm thời', track_visibility='onchange'),
                'date_expire': fields.date('Ngày hết hiệu lực', track_visibility='onchange'),
                'related_id': fields.many2one('hr.employee', 'Thay thế cho', track_visibility='onchange'),
                #Thêm bởi Thư - 24/06/2016 nhằm mục đích kiểm tra user có thẩm quyền duyệt hay không (dùng cho phân quyền object và ẩn hiện các button Chấp thuận, Từ chối, Gửi lên cấp trên)
                'is_approver' : fields.function(_check_is_approver, string='Có đủ quyền phê duyệt', type='boolean'),
                #Thêm bởi Thư - 24/06/2016 nhằm mục đích không cho hiển thị button Gửi lên cấp trên nếu đã đạt cấp duyệt cao nhất
                'is_final_approval_level' : fields.function(_check_is_final_approval_level, string='Là cấp duyệt cuối cùng', type='boolean'),
                #Thêm bởi Thư - 24/06/2016 nhằm mục đích lưu lại danh sách người đủ thẩm quyền phê duyệt (dùng trong phân quyền object)
                'current_approver_list': fields.many2many('res.users', 'cosmos_work_history_approver_rel', 'work_id', 'uid', string='Những người có thẩm quyền phê duyệt hiện tại'),
                #Thêm bởi Thư - 24/06/2016 nhằm mục đích kiểm tra người dùng hiện tại có Thẩm quyền duyệt phải người lập hay không (dùng cho phân quyền object và ẩn hiện button Thiết lập thành dự thảo)
                'is_owner' : fields.function(_check_is_owner, string='Có quyền chuyển sang trạng thái dự thảo', type='boolean'),
                'approve_id': fields.many2one('res.users', 'Người duyệt'),
                'approve_date': fields.datetime('Ngày duyệt'),
              }
    _defaults = {
                 'state': 'draft',
                 'need_update_employee_infor' :False,
                 'temporary_transfers': False,
                 }
    
    #Thêm bởi Hương 12/07/2016 tự động Cập nhật lại thông tin nhân sự trên hồ sơ nhân viên
    def cron_update_auto_employee_infor(self, cr, uid, context=None):
        if context ==None:
            context={}
        date_now= datetime.now().strftime('%Y-%m-%d')
        #Tìm danh sách những thay đổi nhân sự thỏa mãn tất cả các điều kiện sau:
        #o Trạng thái = Đã duyệt.
        #o Ngày hiệu lực >= ngày hiện tại.
        #o need_update_employee_infor = False.
        #o Là điều chuyển tạm thời = False.
        empl_upd_list= self.search(cr, uid, [('state','=','appro'),('date','>=',date_now),('need_update_employee_infor','=',False), ('temporary_transfers','=',False)], context=context)
        if empl_upd_list:
            for empl_upd_id in empl_upd_list:
                upd_obj= self.browse(cr, uid, empl_upd_id,context)
                #Công ty = giá trị field Công ty mới
                #Đơn vị = giá trị field Đơn vị mới.
                #Chức vụ = giá trị field Chức vụ mới.
                #Vị trí công việc chính = giá trị field Vị trí công việc chính mới.
                #Vị trí công việc kiêm nhiệm = giá trị field Vị trí công việc kiêm nhiệm mới.
                #Mức lương hiện tại = giá trị field Mức lương mới.
                vals={}
                vals.update({'company_id': upd_obj.company_new.id ,
                             'department_id': upd_obj.unit_new.id,
                             'function_id': upd_obj.possition_new.id,
                             'job_id': upd_obj.job_pri_new.id, 
                             'job_ids': [(6, 0, upd_obj.job_ids_new.ids or False)],
                             'salary_curent': upd_obj.salarylevel_new.id})
                self.pool.get('hr.employee').write(cr, uid,upd_obj.employee_id.id, vals,context)
                #Cập nhật giá trị field need_update_employee_infor của thay đổi nhân sự đang xét = True
                self.write(cr, uid, upd_obj.id, {'need_update_employee_infor': True})
        return True   
    
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, record.name or ''))
        return res
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(cosmos_work_history,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        for field in res['fields']:
            if field == 'possition_appro':
                ir_model_data = self.pool.get('ir.model.data')
                human_manager = ir_model_data.get_object(cr, uid, 'base','group_hr_director')
                company_seo = ir_model_data.get_object(cr, uid, 'base','group_company_ceo')
                res['fields'][field]['domain'] = [('id','in',[human_manager.id, company_seo.id])]
        return res
    
    #Thêm bởi Thư - Hàm dùng chung lấy giá trị cho onchange_job_id, write, create
    def set_information(self, cr, uid, employee, dict_values, is_onchange=False, context=None):
        company_old = False
        unit_old = False
        possition_old = False
        job_pri_old = False
        job_ids_old = []
        salarylevel_old = False
        if employee.company_id:
            company_old = employee.company_id.id
        if employee.department_id:
            unit_old = employee.department_id.id
        if employee.function_id:
            possition_old = employee.function_id.id
        if employee.job_id:
            job_pri_old = employee.job_id.id
        try:
            if employee.job_ids:
                jobs_obj = employee.job_ids
                job_ids_old = jobs_obj.ids
        except ValueError:
            pass
        if employee.salary_curent:
            salarylevel_old = employee.salary_curent.id
        dict_values.update ({'unit_old':unit_old, 'company_old':company_old, 'possition_old':possition_old,'job_pri_old':job_pri_old,'job_ids_old':[(6, 0, job_ids_old)],'salarylevel_old':salarylevel_old})
        if is_onchange:
            dict_values.update ({'unit_new':unit_old, 'company_new':company_old, 'possition_new':possition_old,'job_pri_new':job_pri_old,'job_ids_new':[(6, 0, job_ids_old)],'salarylevel_new':salarylevel_old})
        return dict_values
    
    def onchange_job_id(self, cr, uid, ids, job_id, context=None):
        if job_id:
            rank_ids = self.pool.get('cosmos.rank.salary').get_valid_rank_salary_of_a_job(cr,uid,job_id,context=context)
            return {'value': {'salarylevel_new':False},
                    'domain':{'salarylevel_new':[('id','in',rank_ids)]}
                    }
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        if not employee_id:
            return {'value': {'unit_old':False, 'unit_new':False, 'company_old':False, 'company_new':False, 'possition_old':False, 'possition_new':False,'job_pri_old':False, 'job_pri_new':False,'job_ids_old':False,'job_ids_new':False,'salarylevel_old':False,'salarylevel_new':False}}
        emp_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        dict_values = self.set_information(cr, uid, emp_obj, dict_values={}, is_onchange=True, context=context)
        return {'value': dict_values}
    
    
    #Hàm tạo mã - thêm bởi Tuấn ngày 08/07/2016 - Sửa lần 2 bởi Tuấn - 19/07/2016 (đưa về sequence autoreset)
    def get_cosmos_work_history_code(self, cr, uid, context=None):
        #Lấy sequence chuẩn
        str_code = self.pool.get('ir.sequence').get(cr, uid, 'code.work.history', context=context)
        return str_code
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.get_cosmos_work_history_code(cr, uid, context)
        if 'employee_id' in vals:
            emp_obj = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context)
            #Gọi hàm dùng chung để lấy giá trị (do các field readonly ko dùng onchange được)
            dict_values = self.set_information(cr, uid, emp_obj, dict_values=vals, is_onchange=False, context=context)
        return super(cosmos_work_history, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'employee_id' in vals:
            emp_obj = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'], context=context)
            #Gọi hàm dùng chung để lấy giá trị (do các field readonly ko dùng onchange được)
            dict_values = self.set_information(cr, uid, emp_obj, dict_values=vals, is_onchange=False, context=context)
        #Update giá trị khi Là điều chuyển tạm thời = True
        if vals.get('temporary_transfers') == True:
            for data in self.browse(cr, uid, ids, context=context):
                vals['unit_new'] = data.unit_old.id
                vals['company_new'] = data.company_old.id
                vals['possition_new'] = data.possition_old.id
                vals['job_pri_new'] = data.job_pri_old.id
                try:
                    if data.job_ids_old:
                        job_ids_old = data.job_ids_old.ids
                except ValueError:
                    pass
                vals['job_ids_new'] = [(6, 0, job_ids_old)]
                vals['salarylevel_new'] = data.salarylevel_old.id
        return super(cosmos_work_history, self).write(cr, uid, ids, vals, context=context)
    
    #Thêm bởi Thư ngày 24/06/2016 - Hàm lấy giá trị description(dùng cho việc lấy description cho yêu cầu phê duyệt khi bấm Gửi yêu cầu hoặc Gửi lên cấp trên)
    def get_description(self, cr, uid, data_obj,context=None):
        return data_obj.name
    
    #Sửa bởi Thư ngày 24/06/2016 - Hàm gửi yêu cầu phê duyệt đến người phê duyệt thuộc nhóm người dùng chỉ định
    def action_request(self, cr, uid, ids, context=None):
        approval_obj = self.pool.get('approval.request.common')
        for data in self.browse(cr, uid, ids, context):
            #Mô tả văn bản
            description = self.get_description(cr, uid, data_obj=data, context=context)
            group_id = data.possition_appro.id 
            #Gọi hàm gửi yêu cầu phê duyệt dùng chung
            approval_obj.send_approval_request_group_case(cr, uid, reference_class=self, item_id=data.id, description=description, group_id=group_id, company=data.company_old, approved_state_name='appro', next_state_name='waitappro', context=context)
        return True
    
    #Sửa bởi Thư ngày 24/06/2016 - Hàm chấp thuận yêu cầu 
    #cập nhật lại bởi Hương ngày 12/07/2014
    def action_approve(self, cr, uid, ids, context=None):
        approval_obj = self.pool.get('approval.request.common')
        for data in self.browse(cr, uid, ids, context):
            #Thực hiện các quy luật chung khi bấm chấp thuận
            approval_obj.approved_request(cr, uid, reference_class=self, item_id=data.id, approved_state_name='appro', context=context)
            #Nếu điều chuyển tạm thời là True 
            if data.temporary_transfers==True:
                #Người ủy quyền = thuộc tính Người dùng liên quan của field Thay thế cho
                #Người được ủy quyền = thuộc tính Người dùng liên quan của field Nhân viên
                #Ngày hết hiệu lực = giá trị field Ngày hết hiệu lực
                #Trạng thái = Đang hiệu lực
                #Lý do = Ủy quyền do điều chuyển tạm thời
                vals={}
                vals={'authuser_id':data.related_id.user_id.id,
                      'authed_id':data.employee_id.user_id.id,
                      'date_deadline':data.date_expire,
                      'state':'active',
                      'reason':'Ủy quyền do điều chuyển tạm thời'
                      }
                self.pool.get('cosmos.hr.delegate').create(cr, uid, vals, context=context)
        return True
    
    #Sửa bởi Thư ngày 24/06/2016 - Hàm từ chối yêu cầu
    def action_refuse(self, cr, uid, ids, context=None):
        approval_obj = self.pool.get('approval.request.common')
        for data in self.browse(cr, uid, ids, context):
            #Gọi hàm từ chối yêu cầu dùng chung
            approval_obj.rejected_request(cr, uid, reference_class=self, item_id=data.id, rejected_state_name='reject', context=context)
        return True
    
    #Sửa bởi Thư ngày 24/06/2016 - Hàm chuyển trạng thái thành dự thảo
    def action_set_draft(self, cr, uid, ids, context=None):
        return self.pool.get('approval.request.common').process_document_state_to_draft(cr, uid, ids, reference_class=self, context=context)
    
        
    #Thêm bởi Hương 06/07/2016 - Sửa bới Tuấn - 13/07/2016    
    def action_create_contract(self, cr, uid, ids, context): 
        addendum_contract_pool= self.pool.get('cosmos.addendum.contract')
        view_id = self.pool.get('ir.model.data').get_object(cr, uid, 'cosmos_hr_contract', 'view_addendum_contract_form')[0].id
        
        for data in self.browse(cr, uid, ids, context):
            dict_pram_to_return_view = {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'cosmos.addendum.contract',
                'type': 'ir.actions.act_window',
                'nodestroy': True               
            }
            addendum_contract_ids = addendum_contract_pool.search(cr, uid, [('work_history_id', '=', data.id)],limit=1,context=context)
            #Nếu chưa có phụ lục hợp đồng tương ứng thì mở formview ở chế độ tạo mới
            if not addendum_contract_ids:
                dict_pram_to_return_view.update({'target' : 'current','res_id': False,
                                                 'context' : {'active_model_temp':'cosmos.work.history','active_id_temp':data.id},
                                                 })
                
            else:#Ngược lại thì mở phụ lục hợp đồng tương ứng ở chế độ xem
                dict_pram_to_return_view.update({'target' : 'current','res_id': addendum_contract_ids[0]})
            return dict_pram_to_return_view
    
    
    #Hàm set dữ liệu mặc định cho Phụ lục hợp đồng từ form thay đổi nhân sự -Thêm bởi Hương ngày 07/07/2016
    def set_information_for_addendum_contract(self, cr, uid, work_history, dict_values, context=None):
        if dict_values == None:
            dict_values = {}
        if work_history.employee_id.id:
            dict_values.update ({'employee_id':work_history.employee_id.id})
        if work_history.date:
            dict_values.update ({'date_effect':work_history.date})
        if work_history.unit_old.id:
            dict_values.update ({'department_old':work_history.unit_old.id})
        if work_history.unit_new.id:
            dict_values.update ({'department_new':work_history.unit_new.id})
        if work_history.company_new.id:
            dict_values.update ({'company_new':work_history.company_new.id})
        if work_history.company_old.id:
            dict_values.update ({'company_old':work_history.company_old.id})
        if work_history.possition_old.id:
            dict_values.update ({'function_old':work_history.possition_old.id})
        if work_history.possition_new.id:
            dict_values.update ({'function_new':work_history.possition_new.id})
        if work_history.job_pri_old.id:
            dict_values.update ({'job_old':work_history.job_pri_old.id})
        if work_history.job_pri_new.id:
            dict_values.update ({'job_new':work_history.job_pri_new.id })
        if work_history.salarylevel_old.id:
            dict_values.update ({'salary_old':work_history.salarylevel_old.id})
        if work_history.salarylevel_new.id:
            dict_values.update ({'salary_new':work_history.salarylevel_new.id})
        if work_history.job_ids_old.ids:
            dict_values.update ({'job_olds':work_history.job_ids_old.ids})
        if work_history.job_ids_new.ids:
            dict_values.update ({'job_news':work_history.job_ids_new.ids})
        dict_values.update ({'work_history_id':work_history.id})
        return dict_values
    
    #Thêm bởi Hương 07/07/2016 - Sửa bởi Tuấn ngày 13/07/2016
    def action_create_decide(self, cr, uid, ids, context):
        decisions_manage_pool = self.pool.get('cosmos.decisions.manage')
        view_id = self.pool.get('ir.model.data').get_object(cr, uid, 'cosmos_info_management', 'cosmos_decisions_manage_form')[0].id
        for data in self.browse(cr, uid, ids, context):
            dict_pram_to_return_view = {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'cosmos.decisions.manage',
                'type': 'ir.actions.act_window',
                'nodestroy': True               
            }
            decisions_manage_ids = decisions_manage_pool.search(cr, uid, [('work_history_id', '=', data.id)],limit=1,context=context)
            #Nếu chưa có quyết định tương ứng thì mở formview ở chế độ tạo mới
            if not decisions_manage_ids:
                dict_pram_to_return_view.update({'target' : 'current','res_id': False,
                                                 'context' : {'active_model_temp':'cosmos.work.history','active_id_temp':data.id},
                                                 })
                
            else:#Ngược lại thì mở quyết định tương ứng ở chế độ xem
                dict_pram_to_return_view.update({'target' : 'current','res_id': decisions_manage_ids[0]})
            return dict_pram_to_return_view
        
                    
#Lich su nghi viec cua nhan vien
class cosmos_work_history_leave(osv.osv):
    _name = 'cosmos.work.history.leave'
    _description = 'Lich su nghi viec cua nhan vien.'
    _inherit = ['mail.thread']
    _columns= {
               'employee_id': fields.many2one('hr.employee','Nhân viên', required=True,track_visibility='onchange'),
               'name': fields.related('employee_id','name', type='char',string='Nhân viên'),
               'date_out': fields.date('Ngày xin nghỉ',required=True,track_visibility='onchange'),
               'type_leave': fields.selection([('write','Tự viết đơn xin nghỉ'),('out','Bị sa thải'),('outdate','Nghỉ  do hết hạn hợp đồng')],'Loại nghỉ',track_visibility='onchange',required=True),
               'day_out_begin': fields.date('Ngày bắt đầu nghỉ',required=True,track_visibility='onchange'),
               'reason': fields.many2one('cosmos.work.history.reason','Lý do nghỉ',required=True,track_visibility='onchange'),
               'note': fields.text('Ghi chú',track_visibility='onchange'),
               'state': fields.selection([('draft','Dự thảo'),('save','Lưu hồ sơ')],'Status',track_visibility='onchange')
               }
    _defaults = {
                'state':'draft',
                }
    _description = 'Lich su nghi viec cua nhan vien.' 
    _order = 'date_out desc'
    
    #Them boi Quyen - ngày 14/07/2016 - Hàm xử lý khi luu ho so
    def process_save_profile_leave(self, cr, uid, leave_id, context=None):
        emp_pool = self.pool.get('hr.employee')
        contract_pool = self.pool.get('hr.contract')
        user_pool = self.pool.get('res.users')
        leave_obj = self.browse(cr, uid, leave_id, context=context)
        #Update active nhân viên thành False, ngày nghỉ việc bằng ngày bắt đầu nghỉ
        emp_pool.write(cr, uid, [leave_obj.employee_id.id],{'active': False,'day_out':leave_obj.day_out_begin}, context=context)
        #Tìm hợp đồng của nhân viên, update trạng thái hợp đồng hết hiệu lực
        contract_ids = contract_pool.search(cr, uid, [('employee_id', '=', leave_obj.employee_id.id)], context=context)
        if contract_ids:
            contract_pool.write(cr, uid, contract_ids, {'state':'expire'}, context=context)
        #Tìm user ứng với nhân viên, update active thành False
        user_id = user_pool.search(cr, uid, [('id','=',leave_obj.employee_id.user_id.id)], context=context)
        if user_id:
            user_pool.write(cr, SUPERUSER_ID, user_id, {'active':False}, context=context)
        self.write(cr, uid, leave_obj.id, {'state': 'save'}, context=context)
        return True
    
    #Sửa bởi Thư - ngày 24/06/2016 - Hàm xử lý button lưu hồ sơ
    #Sua boi Quyen - 14/07/2016 - Chuyen ve xu ly trong ham dung chụng
    def action_save(self, cr, uid, ids, context=None):
        for data_id in ids:
            self.process_save_profile_leave(cr, uid, data_id, context=context)
        return True

#Tạo bảng Lý do nghỉ .
class create_table_leave(osv.osv):
    _name = 'cosmos.work.history.reason'
    _description = 'Ly do nghi viec.'
    _columns = {
                'name' : fields.text('Lý do nghỉ')
                }
    