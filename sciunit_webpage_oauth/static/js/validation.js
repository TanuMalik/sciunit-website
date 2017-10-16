function validateFormEmail() {
  let support_form_email = document.forms["support-form"]["email"].value;
  let email_regex = /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  if (!email_regex.test(support_form_email)) {
    alert("Email Addresss Not Valid");
    return false;
  }
  else{
      alert("Your message has been sent. We will contact you as soon as we are able.")
      return true;
  }
}
