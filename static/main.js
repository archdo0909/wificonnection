define(['base/js/namespace','base/js/dialog','jquery'],function(IPython, dialog, $, mc){

    // we will define an action here that should happen when we ask to clear and restart the kernel.
    var search_wifi  = {
        help: 'wifi',
        icon : 'fa-wifi',
        help_index : '',
        handler : function (env) {
            var settings = {
                url : '/wifi/scan',
                processData : false,
                type : "GET",
                dataType: "json",
                contentType: 'application/json',
                success: function(data) {

                    // display feedback to user
                    console.log(data)
                },
                error: function(data) {

                    // display feedback to user
                    console.log('error')
                }

            };
            $.ajax(settings);
            // get the canvas for user feedback
            var container = $('#notebook-container');

            // function on_ok(){
            //     // var re = /^\/notebooks(.*?)$/;
            //     // var filepath = window.location.pathname.match(re)[1];
            //     var settings = {
            //         url : '/wifi/scan',
            //         processData : false,
            //         type : "GET",
            //         dataType: "json",
            //         contentType: 'application/json',
            //         success: function(data) {

            //             // display feedback to user
            //             console.log('sucess')
            //         },
            //         error: function(data) {

            //             // display feedback to user
            //             console.log('error')
            //         }
            //     };

                // display preloader during commit and push
                // var preloader = '<img class="commit-feedback" src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.8/ajax-loader.gif">';
                // container.prepend(preloader);

                // commit and push
                
            // }


            // dialog.modal({
            //     body: div ,
            //     title: 'Commit and Push Notebook',
            //     buttons: {'Commit and Push':
            //                 { class:'btn-primary btn-large',
            //                   click:on_ok
            //                 },
            //               'Cancel':{}
            //         },
            //     notebook:env.notebook,
            //     keyboard_manager: env.notebook.keyboard_manager,
            // })

        }
    }

    function _on_load(){

        // log to console
        console.info('wifi')

        // register new action
        var action_name = IPython.keyboard_manager.actions.register(search_wifi, 'search wifi list')

        // add button for new action
        IPython.toolbar.add_buttons_group([action_name])

    }

    return {load_ipython_extension: _on_load };
})
