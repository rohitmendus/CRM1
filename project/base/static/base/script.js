$(document).ready(function () {
  $(".dpdown").click(function (e) {
    const next = e.currentTarget.nextElementSibling;
    if (next.classList.contains("submenu")) {
      next.classList.toggle("show");
    }
  });

  $(".toggle-btn").click(function () {
    const sidebar = $("#sidebar"); // your sidebar
    const wrapper = $("#main-wrapper"); // new wrapper that holds navheader + content

    sidebar.toggleClass("collapsed");
    wrapper.toggleClass("collapsed"); // shift header + content together

    const large_logo = $("#large-logo");
    const small_logo = $("#small-logo");

    large_logo.toggleClass("d-none");
    small_logo.toggleClass("d-none");
  });
  
  $(".dlt-service").click(function (e) {
    e.preventDefault();
    const url = $(this).attr("href");
    const csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    const data = { csrfmiddlewaretoken: csrf_token };
    $("#deleteModalService").modal("show");
    $("#deleteServiceButton").click(function () {
      $.ajax({
        url: url,
        data: data,
        type: "post",
        success: function (response) {
          if (response == "success") {
            location.reload();
          }
        },
      });
    });
  });

  $(".dlt-project").click(function (e) {
    e.preventDefault();
    const url = $(this).attr("href");
    const csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    const data = { csrfmiddlewaretoken: csrf_token };
    $("#deleteModalProject").modal("show");
    $("#deleteProjectButton").click(function () {
      $.ajax({
        url: url,
        data: data,
        type: "post",
        success: function (response) {
          if (response == "success") {
            location.reload();
          }
        },
      });
    });
  });


  function rebindConfirmBusiness() {
    const $checkbox = $("#confirmBusiness");
    const $extraFields = $("#extraWorkForm");
    const $siteVisit = $("#siteVisitOn");
    const $comments = $('#comments');
    const $nextFollowUp = $('#nextFollowUp');

    if ($checkbox.length === 0 || $extraFields.length === 0 || $siteVisit.length === 0) return;

    if ($checkbox.is(":checked")) {
      $extraFields.removeClass("d-none");
      $siteVisit.attr("required", "True");

      $comments.attr("disabled", "True");
      $comments.val('');
      $nextFollowUp.removeAttr("required");
      $nextFollowUp.attr("disabled", "True");
      $nextFollowUp.val('');
    } else {
      $extraFields.addClass("d-none");
      $siteVisit.removeAttr("required");

      $comments.removeAttr("disabled");
      $nextFollowUp.removeAttr("disabled");
      $nextFollowUp.attr("required", "True");
    }
    $extraFields.toggleClass("d-none", !this.checked);

    // Bind change event
    $checkbox.off('change').on("change", function () {
        if ($checkbox.is(":checked")) {
          $extraFields.removeClass("d-none");
          $siteVisit.attr("required", "True");

          $comments.attr("disabled", "True");
          $comments.val('');
          $nextFollowUp.removeAttr("required");
          $nextFollowUp.attr("disabled", "True");
          $nextFollowUp.val('');
        } else {
          $extraFields.addClass("d-none");
          $siteVisit.removeAttr("required");

          $comments.removeAttr("disabled");
          $nextFollowUp.removeAttr("disabled");
          $nextFollowUp.attr("required", "True");
        }
        $extraFields.toggleClass("d-none", !this.checked);
      });
  }

  function initSelect2Widget() {
    var $select = $('#serviceTypes');
    if ($select.length) {
      if ($select.hasClass('select2-hidden-accessible')) {
        $select.select2('destroy');
      } 

      $select.select2({
        closeOnSelect: false,
        width: '100%',
        dropdownParent: $(document.body),
      });
    }
  }





  // Initial run
  rebindConfirmBusiness();
  initSelect2Widget();


  // Rebind after HTMX swap
  document.body.addEventListener("htmx:afterSettle", function (evt) {
    if (evt.target && evt.target.id === "enquiryForm") {
      rebindConfirmBusiness();
      initSelect2Widget();
    }
  });

  $('#editModalEnquiry').on('shown.bs.modal', function () {
    initSelect2Widget();  
  });

  $('#editModalWork').on('shown.bs.modal', function () {
    initSelect2Widget();  
  });


  $(".dlt-user").click(function (e) {
    e.preventDefault();
    const url = $(this).attr("href");
    const csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    const data = { csrfmiddlewaretoken: csrf_token };
    $("#deleteModalUser").modal("show");
    $("#deleteUserButton").click(function () {
      $.ajax({
        url: url,
        data: data,
        type: "post",
        success: function (response) {
          if (response == "success") {
            location.reload();
          }
        },
      });
    });
  });

  $(".dlt-enquiry").click(function (e) {
    e.preventDefault();
    const url = $(this).attr("href");
    const csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    const data = { csrfmiddlewaretoken: csrf_token };
    $("#deleteModalEnquiry").modal("show");
    $("#deleteEnquiryButton").click(function () {
      $.ajax({
        url: url,
        data: data,
        type: "post",
        success: function (response) {
          if (response == "success") {
            location.reload();
          }
        },
      });
    });
  });

  $(".dlt-work").click(function (e) {
    e.preventDefault();
    const url = $(this).attr("href");
    const csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    const data = { csrfmiddlewaretoken: csrf_token };
    $("#deleteModalWork").modal("show");
    $("#deleteWorkButton").click(function () {
      $.ajax({
        url: url,
        data: data,
        type: "post",
        success: function (response) {
          if (response == "success") {
            location.reload();
          }
        },
      });
    });
  });

});
