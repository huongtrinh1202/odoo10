# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import math
class convert_munber_to_string(models.Model):
    _name = 'convert.number.to.string'
    _descrition = 'Convert Number To String'
    _inherit = 'mail.thread'
    name = fields.Float('Nhap so')
    to_string = fields.Char('Chu')
    
#     @api.model
    def dochangchuc(self,arr_number,so,daydu):
        chuoi = ""
        chuc = math.floor(so/10)
        donvi = so%10
        print 'aaaaaa' ,chuc , donvi
        if chuc>1 :
            for data in arr_number:
                print data[chuc]
                chuoi = " " + data[chuc] + " mươi"
            if (donvi==1):
                chuoi += " mốt"
            
        elif (chuc==1):
            chuoi = " mười"
            if (donvi==1):
                chuoi += " một";
        elif (daydu and donvi>0):
            chuoi = " lẻ";
        if (donvi==5 and chuc>=1):
            chuoi += " lăm";
        elif (donvi>1 or (donvi==1 and chuc==0)):
            for data1 in arr_number:
                chuoi += " " + data1[ donvi ]
        return chuoi
#     @api.model
    def docblock(self,arr_number,so,daydu):
        chuoi = ""
        tram = math.floor(so/100)
        so = so%100
        if (daydu or tram>0):
            chuoi = " " + arr_number[tram] + " trăm"
            chuoi += self.dochangchuc(arr_number,so,True)
        else:
            chuoi = self.dochangchuc(arr_number,so,False)
        return chuoi
#     @api.model
    def dochangtrieu(self,arr_number,so,daydu):
        chuoi = ""
        trieu = math.floor(so/1000000)
        so = so%1000000
        if (trieu>0):
            chuoi = self.docblock(arr_number,trieu,daydu) + " triệu"
            daydu = True
        nghin = math.floor(so/1000)
        so = so%1000
        if (nghin>0):
            chuoi += self.docblock(arr_number,nghin,daydu) + " nghìn"
            daydu = True
        if (so>0):
            chuoi += self.docblock(arr_number,so,daydu)
        return chuoi
    @api.onchange('to_string')
    def docso(self,so):
        so= 79
        print so
        arr_number = ['không','một','hai','ba','bốn','năm','sáu','bảy','tám','chín']
        if (so==0):
            return arr_number[0]
        chuoi = ""
        hauto = ""
        ty = so%1000000000
        so = math.floor(so/1000000000)
        if (so>0): 
            chuoi = self.dochangtrieu(arr_number,ty,True) + hauto + chuoi
        else:
            chuoi = self.dochangtrieu(arr_number,ty,False) + hauto + chuoi
        hauto = " tỷ"
        while (so>0):
            ty = so%1000000000
            so = math.floor(so/1000000000)
            if (so>0): 
                chuoi = self.dochangtrieu(arr_number,ty,True) + hauto + chuoi
            else:
                chuoi = self.dochangtrieu(arr_number,ty,False) + hauto + chuoi
            hauto = " tỷ"
        print 'chuoi', chuoi
        return chuoi
    
    