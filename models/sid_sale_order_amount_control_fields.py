from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    base_restante = fields.Monetary(
        string="Restante",
        compute="_compute_restante",
        help="Base imponible que queda por entregar",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    excesos_pendientes = fields.Monetary(
        string="Excesos Pend.",
        compute="_compute_excesos_pendientes",
        store=True,
        readonly=True,
        currency_field='currency_id',
        help="Para cálculo de excesos de metraje",
    )

    hitos_pendientes = fields.Monetary(
        string="Hitos pendientes",
        compute="_compute_hitos_pendientes",
        store=True,
        currency_field='currency_id',
        help="Para cálculo de Hitos Pendientes del campo Down Payment"
    )

    base_pendiente = fields.Monetary(
        string="Base Pendiente",
        compute="_compute_base_pendiente",
        help="Base imponible que queda por facturar y ya está entregado",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    base_total = fields.Monetary(
        string="Base Total Facturada",
        compute="_compute_base_total",
        help="Base facturada por línea de venta",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    # === MÉTODOS ===

    @api.depends('order_line.qty_delivered', 'order_line.price_reduce', 'order_line.product_uom_qty', 'order_line.product_id')
    def _compute_restante(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered < line.product_uom_qty:
                        total_base += (line.product_uom_qty - line.qty_delivered) * line.price_reduce
            record.base_restante = total_base

    @api.depends('order_line.qty_delivered', 'order_line.qty_invoiced', 'order_line.price_reduce',
                 'order_line.product_uom_qty', 'order_line.product_id')
    def _compute_excesos_pendientes(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered > line.product_uom_qty and line.qty_invoiced <= line.product_uom_qty:
                        total_base += (line.qty_delivered - line.product_uom_qty) * line.price_reduce
                    elif line.qty_invoiced < line.qty_delivered and line.qty_invoiced > line.product_uom_qty:
                        total_base += (line.qty_delivered - line.qty_invoiced) * line.price_reduce
            record.excesos_pendientes = total_base

    @api.depends('order_line.product_id', 'order_line.product_uom_qty', 'order_line.qty_delivered', 'order_line.qty_invoiced')
    def _compute_hitos_pendientes(self):
        for record in self:
            total_down_payment = 0.0
            for line in record.order_line:
                if line.product_id.default_code == "Down payment" and line.product_uom_qty > 0 and line.qty_delivered == 0 and line.qty_invoiced == 0:
                    total_down_payment += (line.product_uom_qty - line.qty_delivered) * line.price_reduce
            record.hitos_pendientes = total_down_payment

    @api.depends('order_line.qty_to_invoice', 'order_line.price_reduce', 'invoice_ids', 'order_line.qty_delivered', 'order_line.product_uom_qty', 'order_line.qty_invoiced', 'order_line.product_id')
    def _compute_base_pendiente(self):
        for record in self:
            total_base_ex = 0.0
            for line in record.order_line:
                if line.product_id.default_code != "Down payment":
                    if line.qty_delivered > line.product_uom_qty and line.qty_invoiced <= line.product_uom_qty:
                        total_base_ex += (line.qty_delivered - line.product_uom_qty) * line.price_reduce
                    elif line.qty_invoiced < line.qty_delivered and line.qty_invoiced > line.product_uom_qty:
                        total_base_ex += (line.qty_delivered - line.qty_invoiced) * line.price_reduce
            total_base = 0.0
            for line in record.order_line:
                total_base += line.qty_to_invoice * line.price_reduce
            record.base_pendiente = total_base - total_base_ex

    @api.depends('order_line.qty_invoiced', 'order_line.price_reduce_taxexcl')
    def _compute_base_total(self):
        for record in self:
            total_base = 0.0
            for line in record.order_line:
                total_base += line.qty_invoiced * line.price_reduce_taxexcl
            record.base_total = total_base
