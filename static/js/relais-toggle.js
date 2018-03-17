$(function () {
   $(document).on('click', '.relais-toggle', function (e) {
       e.preventDefault();
       console.log("saefasef");
       var relais_id = $(this).attr('relais-id');
       var button = $(this);
       $.ajax({
           type: 'GET',
           url: 'switch_relais/',
           dataType: 'json',
           data: {'relais_id': relais_id}
       }).done(function (data) {
           if(data['state'] === 0)
               $(button).removeClass('active');
           else
               $(button).addClass('active');
       }).fail(function (data) {
            $(this).toggleClass('error');
       });
   });
});