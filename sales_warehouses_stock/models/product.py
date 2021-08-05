from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_information_from_js(self, product_id, company_id):
        if not product_id:
            return {}
        product = self.env['product.product'].browse(product_id)
        groupe_per_location = {}
        groupe_per_pricelist = {}

        for stock_quant_id in product.stock_quant_ids.filtered(lambda sq: sq.location_id.usage == 'internal'):
            groupe_per_location.setdefault(stock_quant_id.location_id, {'name': stock_quant_id.location_id.display_name,'qty':0.0,'visible':True})
            warehouse = stock_quant_id.location_id.get_warehouse()
            if not warehouse.visible_on_sol:
                groupe_per_location[stock_quant_id.location_id]['visible'] = False
            groupe_per_location[stock_quant_id.location_id]['qty'] += stock_quant_id.quantity

        domain = [ '&',
            ('company_id', 'in', [company_id, False]) ,
            '|',
            '&', ('product_tmpl_id', '=', product.product_tmpl_id.id), ('applied_on', '=', '1_product'),
            '&', ('product_id', '=', product.id), ('applied_on', '=', '0_product_variant')]
        pricelists = self.env['product.pricelist.item'].search(domain)
        for pl in pricelists:
            groupe_per_pricelist.setdefault(pl.id,{'name':pl.pricelist_id.name, 'min_quantity': pl.min_quantity, 'fixed_price': pl.fixed_price})
        return {
            'name': product.display_name,
            'qty_available': product.qty_available,
            'virtual_available': product.virtual_available,
            'uom': product.uom_id.name,
            'qty_per_location': list(groupe_per_location.values()) or False,
            'pricelist_items': list(groupe_per_pricelist.values()) or False,
        }
