from odoo import models, fields, api, _
import base64
import datetime

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    def notify_expired_quotations(self):
        current_date = datetime.datetime.now().date()
        initial_date = datetime.date(2023, 12, 14)
        expired_sale_quotes = self.env['sale.order'].search([
        ('validity_date', '<=', current_date),
        ('validity_date', '>', initial_date),
        ('state', 'not in', ['cancel', 'done'])
        ])
        report_service = self.env['ir.actions.report']
        
        for quote in expired_sale_quotes:
            subject = "La cotización número: '{}' ha vencido".format(quote.name)
            body = """
                <p>Estimado/a Sr./Sra.: <strong>{}</strong></p>

                <p>Nos servimos de la presente para hacerle saber que su cotización número <strong>{}</strong> está vencida.</p>

                <ul>
                    <li>Orden: <strong>{}</strong></li>
                    <li>Hecha por: <strong>{}</strong></li>
                    <li>Monto: <strong>RD${}</strong></li>
                    <li>Fecha de orden: <strong>{}</strong></li>
                </ul>

                <p>Si desea proceder a utilizar el servicio cotizado, debe comunicarse con nosotros para validar la disponibilidad de la misma y esperar la autorización para proceder con el pago.</p>

                <p>Saludos cordiales,</p>
                <p><strong>Equipo de Transporte Sheila</strong></p>
            """.format(quote.partner_id.name, quote.name, quote.name, quote.user_id.name, quote.amount_total, quote.date_order)
            report = report_service._get_report_from_name('sale.report_saleorder')
            report_pdf = report._render_qweb_pdf([quote.id])[0]
            report_pdf_b64 = base64.b64encode(report_pdf)

            attachment = self.env['ir.attachment'].create({
            'name': 'Cotización {}.pdf'.format(quote.name),
            'type': 'binary',
            'datas': report_pdf_b64,
            'res_model': 'sale.order',
            'res_id': quote.id
            })
            
            message = self.env['mail.message'].create({
                'body': body,
                'subject': subject,
                'message_type': 'comment',
                'partner_ids': [(4, quote.partner_id.id)],
                'model': 'sale.order',
                'res_id': quote.id,
            })
            
            mail_id = self.env['mail.mail'].create({
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body,
                'email_to': quote.partner_id.email,
                'mail_message_id': message.id,
                'auto_delete': True,
                'state': 'outgoing',
                'attachment_ids': [(4, attachment.id)]
            })

            mail_id.send()
            quote.action_cancel()
