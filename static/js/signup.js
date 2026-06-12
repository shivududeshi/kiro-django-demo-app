var $DOM = $(document);

$DOM.on('click', '#signup_submit', function() {
    console.log("submit clicked");
    var data = {};
    data["first_name"] = $(".fname").val();
    data["last_name"] = $(".lname").val();
    data["email"] = $(".email").val();
    data["phone_number"] = $(".phno").val();

    $.ajax({
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify(data),
        url: '/signup/validate',
        success: function(result) {
            console.log(result);
            if (result.success) {
                window.location.href = "/login";
            } else {
                alertify.set('notifier', 'position', 'top-right');
                alertify.error(result.message);
            }
        },
        error: function(xhr) {
            alertify.set('notifier', 'position', 'top-right');
            alertify.error("Signup failed. Please try again.");
            console.error(xhr.responseText);
        }
    });
});
