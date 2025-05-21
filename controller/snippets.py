from odoo.http import request, route, Controller


class WebsiteProduct(Controller):

    @route('/rooms', auth='public', website=True)
    def rooms_snippet_view(self):
        return request.render('hostel_management.rooms_website')

    @route('/get_rooms', auth="public", type='json',
           website=True)
    def get_latest_four_rooms(self):
        """Get the website categories for the snippet."""
        latest_rooms = request.env['room.management'].sudo().search_read(
            fields=['room_no', 'no_of_bed', 'total_rent', 'id', 'image'])
        # for category in four_rooms:
        #     print(category)

        return latest_rooms

    @route('/rooms/<model("room.management"):room>', type='http', auth="public", website=True)
    def product_detail(self, room):
        value = {
            'room': room,
        }
        return request.render('hostel_management.room_details_page', value)
