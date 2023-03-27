$(document).ready(function() {
    $('form').submit(function(event) {
            var recaptcha = $("#g-recaptcha-response").val();
            if( document.getElementById('err')){

            if (recaptcha === "" || recaptcha === undefined) {
                event.preventDefault();
                document.getElementById('err').innerHTML="Please verify Captcha";
            }
            else{
                return true;
            }
            }
      });
});
