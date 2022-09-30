// Show the loading wheel layout above the main content
function show_load_layout() {
    var loading_layout_div = document.getElementById("loading_overlay");
    var main_content_div = document.getElementById("main_content");
    var main_content_height = main_content_div.clientHeight;
    if (main_content_height > 200) {
      loading_layout_div.style.height = main_content_height.toString()+"px";
    }
    loading_layout_div.classList.remove("invisible");
  }
  
  
// Hide the loading wheel layout above the main content
function hide_load_layout() {
  var loading_layout_div = document.getElementById("loading_overlay");
  loading_layout_div.classList.add("invisible");
}

function show_load_btn(currentTarget) {
  var btn_value = currentTarget.getElementsByClassName("btn-value")[0];
  btn_value.classList.add("hidden");
  var spinner_element = currentTarget.getElementsByClassName("spinner-border")[0];
  spinner_element.classList.remove("hidden");
  currentTarget.disabled = true;
}

function hide_load_btn(currentTarget) {
  var btn_value = currentTarget.getElementsByClassName("btn-value")[0];
  btn_value.classList.remove("hidden");
  var spinner_element = currentTarget.getElementsByClassName("spinner-border")[0];
  spinner_element.classList.add("hidden");
  currentTarget.disabled = false;
}

// Debounce Any passed Function for Any Passed Time (default = 300ms)
function debounce(func, timeout = 300){
  /** Debounce Any Given Function */
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => { func.apply(this, args); }, timeout);
  };
}


// Auto Dismess Alerts after 4 Seconds
const autoDismessAlert = () => {
  setTimeout(function() {
    $(".alert").alert('close');
  }, 7000);
};

$(document).ready(autoDismessAlert());

// Function Used with .filter() to get unique Array
function onlyUnique(value, index, self) {
  return self.indexOf(value) === index;
}