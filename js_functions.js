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

function match_id(value) {
  $.ajax({
    url: "fileset.php",
    type: "post",
    dataType: "json",
    data: {
      match: value,
    },
  });
}

function remove_empty_inputs() {
  var myForm = document.getElementById("filters-form");
  var allInputs = myForm.getElementsByTagName("input");
  var input, i;

  for (i = 0; (input = allInputs[i]); i++) {
    if (input.getAttribute("name") && !input.value) {
      console.log(input);
      input.setAttribute("name", "");
    }
  }
}

function hyperlink(link) {
  window.location = link;
}

$(document).ready(function () {
  $(".hidden").hide();
  $("#delete-button").one("click", delete_id);
  $("#match-button").one("click", match_id);
});
