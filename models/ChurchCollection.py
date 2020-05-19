# -*- coding:utf-8 -*-
"""Church Collections consists of all church weekly or monthly collections."""
import datetime
from .helper import parish, program_default_date

from odoo import api, fields, models
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError


class Collection(models.Model):
    """ng_church.collection."""

    _name = 'ng_church.collection'

    name = fields.Char()

class Donation(models.Model):
    """Church Donation is cetain sum of money that is given to a church as charity."""

    _name = 'ng_church.donation'

    name = fields.Many2one('project.project', 'Project', required=True)
    start_date = fields.Date(related='name.x_date', string='Start Date')
    notes = fields.Text(string='Note')
    church_id = fields.Many2one('res.company', default=parish)
    donation_line_ids = fields.One2many(
        'ng_church.donation_line', 'donation_id', srting='Donations')


class DonationLine(models.Model):
    """Church Donation is cetain sum of money that is given to a church as charity."""

    _name = 'ng_church.donation_line'

    donation_id = fields.Many2one('ng_church.donation', string='Donation')
    name = fields.Char(string='name')
    date = fields.Date(string='Date', required=True)
    donor_id = fields.Many2one('res.partner', string='Donor')
    amount = fields.Float(string='Donated Amount', required=True)
    is_invoiced = fields.Boolean(string='Invoiced', readonly=True)
    notes = fields.Char(related='donation_id.name.name')
    church_id = fields.Many2one('res.company', default=parish)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True)

    @api.constrains('amount')
    def _check_valid_amount(self):
        if self.amount < 1:
            raise ValidationError(
                'Please enter a valid amount of money {} can\'t be deposited'.format(self.amount))

    @api.onchange('date')
    def _onchange_name(self):
        if self.date:
            self.name = self.date.strftime("%B %d, %Y")

    def _prepare_account_payment(self):
        """Generate Account Voucher."""
        company = self.env.user.company_id
        payment_obj = self.env['account.payment']
        payload = {
            'company_id': company.id,
            'partner_id': self.env.user.partner_id.id,
            'partner_type': 'customer',
            'journal_id': company.donation_payment_journal.id,
            'amount': self.amount,
            'payment_date': self.date,
            'payment_method_id': self.payment_method_id.id,
            'communication': '{} Donation'.format(self.donor_id.name or 'Anonymous'),
            'payment_type': 'inbound'
        }
        payment_obj = payment_obj.create(payload)
        return payment_obj

    def generate_donation_move(self):
        """User Interface button call this method."""
        self._prepare_account_payment()
        self.is_invoiced = True


class Tithe(models.Model):
    """One tenth of produce or earnings, formerly taken as a tax for the support of the church and clergy."""

    _name = 'ng_church.tithe'

    def _compute_default_collection(self):
        category = self.env['ng_church.collection'].name_search('Tithes', limit=1)
        if category:
            # Remove the item at the given position in the list, and unpack the tupple
            category_id, category_name = category.pop(0)
            return category_id
        else:
            self.env['ng_church.collection'].create({'name': 'Tithes'})
            category = self.env['ng_church.collection'].name_search('Tithes', limit=1)
            category_id, category_name = category.pop(0)
            return category_id

    name = fields.Many2one(
        'ng_church.collection', string='Collection', default=_compute_default_collection)
    section_id = fields.Many2one('church.sections', string="Church Section", required=True)
    service_id = fields.Many2one('ng_church.program', string="Church Service")
    pastor_id = fields.Many2one('ng_church.pastor', string='Minister\'s Name')
    church_id = fields.Many2one('res.company', string='Church\'s Tithe', default=parish)
    is_pastor_tithe = fields.Boolean(string='Minister\'s Tithe')
    tithe_line_ids = fields.One2many('ng_church.tithe_lines', 'tithe_id', string='Tithes')
    date = fields.Date(string='Date')

class TitheLine(models.Model):
    """One tenth of produce or earnings, formerly taken as a tax for the support of the church and clergy."""

    _name = 'ng_church.tithe_lines'

    date = fields.Date(string='Date', required=True)
    name = fields.Char(string='Date')
    tithe_type = fields.Selection(
        selection=[('members', 'Members'), ('pastor', 'Pastor'), ('minister', 'Minister')], string='Category',
        default='members')
    tither = fields.Many2one('res.partner', string='Name')
    is_invoiced = fields.Boolean(string='Invoiced', readonly=True)
    tithe_id = fields.Many2one('ng_church.tithe', string='Tithe')
    amount = fields.Float('Amount', required=True)
    church_id = fields.Many2one('res.company', default=parish)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True) #change=1

    @api.constrains('amount')
    def _check_valid_amount(self):
        if self.amount < 1:
            raise ValidationError(
                'Please enter a valid amount of money {} can\'t be deposited'.format(self.amount))

    @api.onchange('date')
    def _onchange_name(self):
        if self.date:
            self.name = self.date.strftime("%B %d, %Y")

    def _prepare_account_payment(self):
        """Generate Account Voucher."""
        company = self.env.user.company_id
        payment_obj = self.env['account.payment']
        payload = {
            'company_id': company.id,
            'partner_id': self.env.user.partner_id.id,
            'partner_type': 'customer', #changes= 8          
            'journal_id': company.tithe_payment_journal.id, #changes=2
            'amount': self.amount, #change=3
            'payment_date': self.date, #change=4
            'payment_method_id': self.payment_method_id.id, #change=5
            'communication': '{} Tithe'.format(self.tithe_type.capitalize()),
            'payment_type': 'inbound' #change=6
        }
        payment_obj = payment_obj.create(payload)
        return payment_obj

    def generate_tithe_voucher(self):
        """User Interface button call this method."""
        self._prepare_account_payment() #change=7
        self.is_invoiced = True


class Offering(models.Model):
    """Church Offering Model."""

    _name = 'ng_church.offering'

    def _compute_default_collection(self):
        category = self.env['ng_church.collection'].name_search('Offering', limit=1)
        if category:
            # Remove the item at the given position in the list, and unpack the tupple
            category_id, category_name = category.pop(0)
            return category_id
        else:
            self.env['ng_church.collection'].create({'name': 'Offering'})
            category = self.env['ng_church.collection'].name_search('Offering', limit=1)
            category_id, category_name = category.pop(0)
            return category_id

    name = fields.Many2one(
        'ng_church.collection', string='Collection Source', default=_compute_default_collection)
    section_id = fields.Many2one('church.sections', string="Church Section", required=True)
    service_id = fields.Many2one('ng_church.program', string="Church Service")
    church_id = fields.Many2one('res.company', default=parish)
    offering_line_ids = fields.One2many(
        'ng_church.offering_line', 'offering_id', string='Offering')


class OfferingLine(models.Model):
    """Church Offering lines model."""

    _name = 'ng_church.offering_line'

    date = fields.Date(string='Date', required=True)
    name = fields.Char(string='Date')
    is_invoiced = fields.Boolean(string='Invoiced')
    amount = fields.Float(string='Amount')
    offering_id = fields.Many2one('ng_church.offering', string='Offering')
    church_id = fields.Many2one('res.company', default=parish)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True) 

    @api.constrains('amount')
    def _check_valid_amount(self):
        if self.amount < 1:
            raise ValidationError(
                'Please enter a valid amount of money {} can\'t be deposited'.format(self.amount))

    @api.onchange('date')
    def _onchange_name(self):
        if self.date:
            self.name = self.date.strftime("%B %d, %Y")

    def _prepare_account_payment(self):
        """Generate Account Voucher."""
        company = self.env.user.company_id
        payment_obj = self.env['account.payment']
        payload = {
            'company_id': company.id,
            'partner_id': self.env.user.partner_id.id,
            'partner_type': 'customer',
            'journal_id': company.offering_payment_journal.id,
            'amount': self.amount,
            'payment_date': self.date,
            'payment_method_id': self.payment_method_id.id,
            'communication': '{} Offering'.format(self.offering_id.section_id.name),
            'payment_type': 'inbound'
        }
        payment_obj = payment_obj.create(payload)
        return payment_obj

    def generate_offering_voucher(self):
        """User Interface button call this method."""
        self._prepare_account_payment()
        self.is_invoiced = True
        

class Pledge(models.Model):
    """."""

    _name = 'ng_church.pledge'

    name = fields.Many2one('project.project', string='Project', required=True)
    date = fields.Date(related='name.x_date', string='Date')
    church_id = fields.Many2one('res.company', default=parish)
    pledge_line_ids = fields.One2many('ng_church.pledge_line', 'pledge_id', string='Pledges', required=True)


class PledgeLine(models.Model):
    """."""

    _name = 'ng_church.pledge_line'

    name = fields.Char(string='Name', related='pledge_id.name.name')
    date = fields.Date(string='Pledged Date', required=True)
    pledger = fields.Many2one('ng_church.associate', string='Pledges')
    amount = fields.Float(string='Pledged Amount')
    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)
    paid = fields.Float(string='Paid', compute='_compute_total_paid', store=True)
    is_invoiced = fields.Char(string='Invoiced', default=False)
    state = fields.Selection(selection=[(
        'active', 'Active'), ('fulfilled', 'Fulfilled')], default='active')
    pledge_id = fields.Many2one('ng_church.pledge', string='Pledge')
    pledge_line_payment_ids = fields.One2many(
        'ng_church.pledge_line_payment', 'pledge_line_id', string='Pledge Payment', required=True)

    @api.constrains('amount')
    def _check_valid_amount(self):
        if self.amount < 1:
            raise ValidationError(
                'Please enter a valid amount of money {} can\'t be pledged'.format(self.amount))

    @api.depends('pledge_line_payment_ids')
    def _compute_total_paid(self):
        total = 0
        for pledge_line_id in self.pledge_line_payment_ids:
            for pledge in pledge_line_id:
                total += pledge.amount
        self.paid = total

    @api.depends('paid')
    def _compute_balance(self):
        if self.paid >= self.amount:
            self.write({'state': 'fulfilled'})
        else:
            self.write({'state': 'active'})
        self.balance = 0.0 if (self.amount - self.paid) < 1 else (self.amount - self.paid)

    def send_by_email(self):
        """Send report via email."""
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'ng_church', 'ng_church_pledge_payment_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'ng_church.pledge_line',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': 'Compose Email',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def message_get_reply_to(self, res_id):
        """message_get_reply_to."""
        if self.env.user.company_id.email is False:
            raise MissingError('Set church email address')
        return {res_id[0]: self.env.user.company_id.email}

    def _prepare_account_payment(self):
        """Generate Account Invoice."""
        company = self.env.user.company_id
        payment_obj = self.env['account.payment']
        payload = {           
            'company_id': company.id,
            'partner_id': self.env.user.partner_id.id,
            'partner_type': 'customer',
            'journal_id': company.pledge_payment_journal.id,            
            'amount': self.amount,
            'payment_date': self.date,
            'payment_method_id': self.payment_method_id.id,
            'communication': '{} Pledge'.format(self.name),
            'payment_type': 'inbound'
        }
        payment_obj = payment_obj.create(payload)
        return payment_obj

    def generate_pledge_move(self):
        """User Interface button call this method."""
        self._prepare_account_payment()
        self.is_invoiced = True

class PledgeLinePayment(models.Model):
    """."""

    _name = 'ng_church.pledge_line_payment'
    date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount')
    pledge_line_id = fields.Many2one('ng_church.pledge_line')

    @api.constrains('amount')
    def _check_valid_amount(self):
        if self.amount < 1:
            raise ValidationError(
                'Please enter a valid amount of money {} can\'t be deposited'.format(self.amount))
