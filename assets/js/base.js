$(function () {
  $(document).scroll(function () {
    var $nav = $(".nav");
    $nav.toggleClass("scrolled", $(this).scrollTop() > $nav.height());
  });
});
/*


'<div class="card" style="text-transform: capitalize">' +
      '<div class="card-header" id="headingOne">' +
          '<div class="report-heading">' + 
            "{{ med|get_item:'medicine' }}" +
         " </div>" +
          "{% if med|get_item:'resolved' %}" +
            '<div class="status resolved"> Resolved </div>' +
            "{% else %}" +
            '<div class="status"> Not resolved </div>' +
            "{% endif %}" +
          
        `<button class="btn btn-link collapsed" type="button" data-toggle="collapse" data-target="#a{{med|get_item:'id'}}" aria-expanded="false" aria-controls="a{{med|get_item:'id'}}">` +
            '<ion-icon name="chevron-down-outline"></ion-icon>' +
          '</button>' +

      '</div>' +
  
      `<div id="a{{med|get_item:'id'}}" class="collapse" aria-labelledby="headingOne" data-parent="#accordionExample">` +
        '<div class="card-body">' +
        '{% for key, value in med.items %}' +
        "{% if key != 'id' and key != 'description' and key != 'location' %}" +
        '<div><b>{{key}}:</b> {{value}}</div>' +
        '{% endif %}' +
        '{% endfor %}  ' +
        "{% if med|get_item:'description' %}" +
        "{{ med|get_item:'description' }}" +
        "{% else %}" +
        "No description provided." +
        '{% endif %}' +  
        '</div>' +
      '</div>' +
        '</div>'

        */
