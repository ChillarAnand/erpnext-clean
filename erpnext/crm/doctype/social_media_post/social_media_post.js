// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Social Media Post', {
    validate: function(frm){
        if(frm.doc.text.length > 280){
            frappe.throw(__("Length Must be less than 280."))
        }
    },
	refresh: function(frm){
        if(frm.doc.docstatus === 1){
            if(frm.doc.post_status != "Posted"){
                add_post_btn(frm); 
            }
            else if(frm.doc.post_status == "Posted"){
                frm.set_df_property('sheduled_time', 'read_only', 1);
            }
            let html = '<div class="row">';
            if(frm.doc.twitter){
                let color = frm.doc.twitter_post_id ? "green" : "red";
                let status = frm.doc.twitter_post_id ? "Posted" : "Not Posted";
                html += '<div class="col-xs-6">' +
                            '<span class="indicator whitespace-nowrap '+ color +'"><span class="hidden-xs">Twitter : '+ status +'</span></span> ' +
                        '</div>' ;
            }
            if(frm.doc.linkedin){
                let color = frm.doc.linkedin_post_id ? "green" : "red";
                let status = frm.doc.linkedin_post_id ? "Posted" : "Not Posted";
                html += '<div class="col-xs-6">' +
                            '<span class="indicator whitespace-nowrap '+ color +'"><span class="hidden-xs">LinkedIn : '+ status +'</span></span> ' +
                        '</div>' ;
            }
            html += '</div>';
            frm.dashboard.set_headline_alert(html);
        }
    }
});
var add_post_btn = function(frm){
    frm.add_custom_button(('Post Now'), function(){
        post(frm);
    });
}
var post = function(frm){
    frappe.call({
        method: "erpnext.crm.doctype.social_media_post.social_media_post.publish",
        args: {
            doctype: frm.doc.doctype,
            name: frm.doc.name
        },
        callback: function(r) {
            frm.reload_doc();
        }
    })
    
}