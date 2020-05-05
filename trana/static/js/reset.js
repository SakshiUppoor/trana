$("#btn-resetPassword").click(function () {
  var auth = firebase.auth();
  var email = $("#email").val();
  if (email != "") {
    auth
      .sendPasswordResetEmail(email)
      .then(function () {
        window.alert("The email has been sent. Please check your mail box!");
        document.getElementById("login").click();
      })
      .catch(function () {
        var errorCode = error.code;
        var errorMessage = error.message;
        console.log(errorCode);
        console.log(errorMessage);
        window.alert("Message : " + errorMessage);
      });
  } else {
    window.alert("Please enter email first");
  }
});
