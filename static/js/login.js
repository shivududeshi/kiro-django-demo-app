var $DOM = $(document);

$DOM.on('click', '#send_otp', function() {
    console.log("send otp clicked");
    var data = {};
    data["email"] = $(".email").val();

    $.ajax({
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify(data),
        url: '/login/send_otp',
        success: function(result) {
            console.log(result);
            alertify.set('notifier', 'position', 'top-right');
            alertify.success("OTP sent to your email");
        },
        error: function(xhr) {
            alertify.set('notifier', 'position', 'top-right');
            alertify.error("Failed to send OTP. Please try again.");
            console.error(xhr.responseText);
        }
    });
});

$DOM.on('click', '#login_submit', function() {
    console.log("login clicked");
    var data = {};
    data["email"] = $(".email").val();
    data["otp"] = $(".otp").val();

    $.ajax({
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify(data),
        url: '/login/validate',
        success: function(result) {
            if (result.success) {
                window.location.href = "/";
            } else {
                alertify.set('notifier', 'position', 'top-right');
                alertify.error(result.message);
            }
        },
        error: function(xhr) {
            alertify.set('notifier', 'position', 'top-right');
            alertify.error("Login failed. Please try again.");
            console.error(xhr.responseText);
        }
    });
});
