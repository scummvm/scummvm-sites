function delete_id(value) {
  $("#delete-confirm").slideDown();

  $.ajax({
    url: "fileset.php",
    type: "post",
    dataType: "json",
    data: {
      delete: value,
    },
  });
}

$(document).ready(function () {
  $(".hidden").hide();
  $("#delete-button").one("click", delete_id);
});
