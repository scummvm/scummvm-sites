# Place all the behaviors and hooks related to the matching controller here.
# All this logic will automatically be available in application.js.
# You can use CoffeeScript in this file: http://coffeescript.org/

$ ->
  $("a.add_fields").
    data("association-insertion-method", 'append').
    data("association-insertion-traversal", 'last').
    data("association-insertion-node", '.versions');
