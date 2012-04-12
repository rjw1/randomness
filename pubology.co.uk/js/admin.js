$(
  function() {
    $('#upload_msg').prepend('Uploading... please be patient, this may take '
                             + 'a little while.');
    $('#upload_msg').hide();
  }
);

function reassure() {
  $('#upload_msg').show();
  return true;
}
