from odoo import models, fields, api, _
import base64
import datetime

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    def notify_expired_quotations(self):
        current_date = datetime.datetime.now().date()
        initial_date = datetime.date(2023, 1, 15)
        expired_quotations = self.env['sale.order'].search([
        ('validity_date', '<=', current_date),
        ('validity_date', '>', initial_date),
        ('state', 'in', ['draft', 'sent'])
        ])
        report_service = self.env['ir.actions.report']
        
        for quotation in expired_quotations:
            subject = "La cotización número: '{}' ha vencido".format(quotation.name)
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
            """.format(quotation.partner_id.name, quotation.name, quotation.name, quotation.user_id.name, quotation.amount_total, quotation.date_order)
            report = report_service._get_report_from_name('sale.report_saleorder')
            report_pdf = report._render_qweb_pdf([quotation.id])[0]
            report_pdf_b64 = base64.b64encode(report_pdf)

            attachment = self.env['ir.attachment'].create({
            'name': 'Cotización {}.pdf'.format(quotation.name),
            'type': 'binary',
            'datas': report_pdf_b64,
            'res_model': 'sale.order',
            'res_id': quotation.id
            })
            
            message = self.env['mail.message'].create({
                'body': body,
                'subject': subject,
                'message_type': 'comment',
                'partner_ids': [(4, quotation.partner_id.id)],
                'model': 'sale.order',
                'res_id': quotation.id,
            })
            
            mail_id = self.env['mail.mail'].create({
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body,
                'email_to': quotation.partner_id.email,
                'mail_message_id': message.id,
                'auto_delete': True,
                'state': 'outgoing',
                'attachment_ids': [(4, attachment.id)]
            })

            channel = self.env['mail.channel'].search([('name', '=', 'general')], limit=1)
            subtype = self.env.ref('mail.mt_comment') 
            
            mail_id.send()
            channel.message_post(message_type='comment', body=body,  subtype_id=subtype.id, attachment_ids=[attachment.id])
            quotation.write({'state': 'cancel'})
