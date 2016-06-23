jQuery ->
  $("a[rel~=popover], .has-popover").popover()
  $("a[rel~=tooltip], .has-tooltip").tooltip()
  $("[data-provide~=datepicker]").datepicker({"format": "yyyy-mm-dd", "weekStart": 1, "autoclose": true})
