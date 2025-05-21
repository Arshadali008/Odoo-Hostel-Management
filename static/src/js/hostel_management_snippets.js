/** @odoo-module **/

import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

function chunkArray(array, size) {
//This function will slice the array
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
}

publicWidget.registry.get_product_tab = publicWidget.Widget.extend({
    selector : '.rooms_section',
    async willStart() {
        const result = await rpc('/get_rooms', {});
        if(result){
            return this.result = result
        }
    },
    start: function() {
        selector : '.rooms_section'
        if((this.result).length != 0 ){
            var chunks = chunkArray(this.result, 4)
            chunks[0].is_active = true
            const uniq = Math.random() * 9999999;
            this.$target.empty().html(renderToElement('hostel_management.rooms_snippet_carousel',
            {chunks:chunks,uniq:uniq}))
        }
    },
});
publicWidget.registry.get_product_tab = publicWidget.Widget.extend({
    selector : '.rooms_section',
    async willStart() {
        const result = await rpc('/get_rooms', {});
        if(result){
            return this.result = result
        }
    },
    start: function() {
        selector : '.rooms_section'
        if((this.result).length != 0 ){
            var chunks = chunkArray(this.result, 4)
            chunks[0].is_active = true
            const uniq = Math.random() * 9999999;
            this.$target.empty().html(renderToElement('hostel_management.rooms_snippet_carousel',
            {chunks:chunks,uniq:uniq}))
        }
    },
});
