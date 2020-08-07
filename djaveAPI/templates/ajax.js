/* AJAX stuff */
function ok(response) {
  return response['OK'];
}

function show_problem(response, feedback_or_append_to) {
  var feedback;
  if (feedback_or_append_to.hasClass('feedback')) {
    feedback = feedback_or_append_to;
  } else {
    feedback = get_feedback_elt_append(feedback_or_append_to);
  }
  var problem = problem_in_response(response);
  if (problem) {
    feedback.text(problem).show();
    return true;
  } else {
    feedback.hide();
    return false;
  }
}

function alert_problem(response) {
  var problem = problem_in_response(response);
  if (problem) {
    alert(problem);
    return true;
  }
  return false;
}

function problem_in_response(response) {
  if (response.responseJSON) {
    // You need this for .fail(function(response) { ...
    response = response.responseJSON;
  } else if (
      response.status && typeof response.status == 'number'
      && response.status != 200) {
    // When objects have a status, it's a word. When responses have a failed
    // status, it's a number.
    if (response.status == 403) {
      return 'Hm, it looks like your login changed. Try refreshing the page.';
    }
    return response.status;
  }
  return response['problem'];
}

function post(url, data, success, always, feedback) {
  success = success || function() {};
  always = always || function() {};
  feedback = feedback || get_feedback_elt_append('body');

  return $.post(url, add_csrf_token(data), function(response) {
    if (!show_problem(response, feedback)) {
      success(response);
    }
    always();
  }).fail(function(response) {
    if (!show_problem(response, feedback)) {
      if (response.status == 0 && response.statusText == 'error') {
        // Firefox is complaining because somebody closed the window before the
        // response could come back and be handled.
        return
      }
      feedback.show().text('Server error :(');
      console.log('Server error :(');
      window.onerror(
          'function post fail server error: ' + JSON.stringify(response));
    }
    always();
  });
}

/* csrf token stuff */
function add_csrf_token(data) {
  data['csrfmiddlewaretoken'] = get_csrf_token();
  return data;
}

function before_send_delete() {
  // https://stackoverflow.com/questions/13089613/ajax-csrf-and-delete
  return function(xhr) {
    xhr.setRequestHeader("X-CSRFToken", get_csrf_token());
  };
}

function get_csrf_token() {
  return $('input[name=csrfmiddlewaretoken]').val();
}

function update_field(
    model_name, pk, field_name, new_value, success, always, feedback) {
  var data = {'type': model_name, 'pk': pk};
  data[field_name] = new_value;
  var use_success = function(response) {
    if (success) {
      return success(pk);
    }
  };
  return post('{{ ajax_update_url }}', data, use_success, always, feedback);
}
