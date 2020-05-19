# -*- coding: utf-8 -*-
"""."""

from odoo import api, fields, models
from odoo.exceptions import MissingError
import datetime

class ChurchAttendanceLineAbstractModel(models.AbstractModel):
    """PledgesReport."""

    _name = 'report.ng_church.church_attendance_report'

    def attendance_line_mutator(self, model):
        """Mutate the state of the original report(s)."""
        attendance_name = model[0].attendance_id.attendance_line_ids
        return model, attendance_name[-1]

    def attendance_census(self, model):
        """."""
        male = 0
        female = 0
        children = 0
        guest = 0
        total = 0
        for population in model:
            male += population.male
            female += population.female
            children += population.children
            guest += population.guest
            total += population.total
        return ['Total:', male, female, children, guest, total]


class ChurchAttendanceLine(models.TransientModel):
    """."""

    _name = 'ng_church.attendance_wizard'

    attendance = fields.Many2one('ng_church.attendance', string="Service", required=True)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(
        string='End Date', default=lambda self: datetime.datetime.now().strftime('%Y-%m-%d'))

    def _report_exist(self, report):
        # check if incomming report is empty, if true return MissingError
        if len(report) <= 0:
            raise MissingError('Attendance record does not exist for selected date range.')

    def check_report(self):
        attendance = self.attendance
        data = {
            'ids': self.env['ng_church.attendance_line'].search([('attendance_id', '=', attendance.id)]),
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'attendance': self.attendance,
            },
        }
        print('Attendance', data)
        return self.env.ref('ng_church.ng_church_church_attendance_report').report_action(self, data)