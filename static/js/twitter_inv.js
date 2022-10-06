// GlOBAL VARIABLES
var prev_chunk = 0
var next_chunk = 0
var lastQuery = "";

// Define Filter Input Fields
var minFollowers = document.querySelector("#min-followers");
var maxFollowers = document.querySelector("#max-followers");
var minFollowing = document.querySelector("#min-following");
var maxFollowing = document.querySelector("#max-following");


async function get_inv(page_chunk = null) {
    if (page_chunk) {
        lastQuery += String(page_chunk);
    }
    
    // If there is no change in the filter Abort
    if (JSON.stringify(twitter_query) === lastQuery) {
        return;
    }

    show_load_layout();

    //Validate Inputs
    var valid = validate_inputs();

    if (!valid) {
        hide_load_layout();
        return
    }

    var twitter_inv_element = document.getElementById("inv_list");

    twitter_inv_element.innerHTML = "";

    var base_url = '/api/investors/twitter'

    var url = page_chunk ? base_url + "?offset=" + String(page_chunk) : base_url;

    var prev_btn = document.getElementById("prev-link");
    var next_btn = document.getElementById("next-link");

    var query_count_ele = document.getElementById("query_count");
    var total_count_ele = document.getElementById("total_count");
    var count_percent_ele = document.getElementById("count_percent");
    var excluded_count_ele = document.getElementById("excluded_count");


    fetch(url, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(twitter_query)
    })
    .then(response => response.json())
    .then(data => {
        try {
            var {investors, total_count, query_count, next_chunk, prev_chunk, limit, no_twitter_count} = data
            if (investors.length > 0) {
              for (let i = 0; i < investors.length; i++) {
                let current_investor = investors[i]

                // Creating a List Item
                let li = document.createElement('li');
                li.classList.add("list-group-item");

                // Appending main image to the list element
                if (current_investor["Image"]) {
                    let div = document.createElement('div');
                    div.style.cssText = 'position:relative';
                    div.classList.add("invest-img_container")
                    
                    let img = document.createElement('img');
                    img.src = current_investor["Image"];
                    img.classList.add("img-fluid")
                    img.classList.add("invest-img")
                    
                    let zoomOverlay = document.createElement('img');
                    zoomOverlay.src = "/static/img/zoom-in.png";
                    zoomOverlay.classList.add("img-zoom")
                    zoomOverlay.setAttribute("data-toggle", "modal");
                    zoomOverlay.setAttribute("data-target", "#viewImageModal");
                    zoomOverlay.onclick = function() { toggleviewImageModal(this) }
                    //data-toggle="modal" data-target="#exampleModalCenter"
                    

                    div.appendChild(img)
                    div.appendChild(zoomOverlay)
                    
                    li.appendChild(div)
                }
                
                // Appending Profile name to the list element
                if (current_investor["Name"]) {
                    let h3 = document.createElement('h3');
                    h3.textContent = current_investor["Name"];
                    li.appendChild(h3)
                }

                // // Appending Position to the list element
                // if (current_investor["Position"]) {
                //     let p = document.createElement('p');
                //     p.classList.add("text-muted")
                //     p.textContent = current_investor["Position"];
                //     li.appendChild(p)
                // }

                // // Appending RenderJson to the list element
                li.appendChild(
                    renderjson(current_investor)
                );
                twitter_inv_element.appendChild(li);
            }
            }
            else{
                // if no investors found for the current query
                let p = document.createElement('p');
                    p.classList.add("h3")
                    p.classList.add("text-info")
                    p.textContent = "NO RESULT FOUND!";
                    twitter_inv_element.appendChild(p)
            }
            
            prev_btn.onclick = function() { get_inv(prev_chunk) }
            next_btn.onclick = function() { get_inv(next_chunk) }

            // disable prev_btn logic
            if(next_chunk - limit <= 0) {
                prev_btn.parentElement.classList.add("disabled")
            }
            else{
                prev_btn.parentElement.classList.remove("disabled")
            }

            // disable next_btn logic
            if(query_count - next_chunk <= 0) {
                next_btn.parentElement.classList.add("disabled")
            }
            else{
                next_btn.parentElement.classList.remove("disabled")
            }
            
            query_count_ele.textContent = query_count
            total_count_ele.textContent = total_count
            count_percent_ele.textContent = ((query_count/total_count)*100).toFixed(3)
            if (no_twitter_count > 0) {
                excluded_count_ele.textContent = "(" + String(no_twitter_count) + " results were excluded, having no Twitter Profile)"
            }

            // Record Last Change in Filter
            lastQuery = JSON.stringify(twitter_query);

            hide_load_layout();
        } catch (err) {
            console.log(err)
        }
    });

}

/** HANDLING FILTERS */

//Handle Followers filter
const handleMinFollowers = () => {
    var minFollowersValue = document.getElementById("min-followers").value;
    twitter_query.min_followers = minFollowersValue;
}
const handleMaxFollowers = () => {
    var maxFollowersValue = document.getElementById("max-followers").value;
    twitter_query.max_followers = maxFollowersValue;
}

//Handle Following filter
const handleMinFollowing = () => {
    var minFollowingValue = document.getElementById("min-following").value;
    twitter_query.min_following = minFollowingValue;
}
const handleMaxFollowing = () => {
    var maxFollowingValue = document.getElementById("max-following").value;
    twitter_query.max_following = maxFollowingValue;
}

// Validate Critical Inputs
const validate_inputs = () =>{
    // Clear any in-valid classes on inputs
    var inputElements = document.querySelectorAll(".form-control")
    inputElements.forEach(ele => {
        ele.classList.remove("is-invalid");
    })

    // Validate Inputs Here and return false if not valid! 

    return true
}


// View Large Image handler
const toggleviewImageModal = (event) => {
    var imgSrc = event.parentElement.querySelector('.invest-img').src;
    var modal = $('#viewImageModal');
    modal.modal('show')
    modal.find('.modal-body img').attr('src', imgSrc)
}

// Update Filter Input Fields with Query Values
const updateFilters = async () =>{
    try {
        minFollowers.value = twitter_query.min_followers;
        maxFollowers.value = twitter_query.max_followers;
        minFollowing.value = twitter_query.min_following;
        maxFollowing.value = twitter_query.max_following;
    } catch (err) {
        console.log(err)        
    }
} 


// Fill the Option Lists in Filters
const get_filters_options = async () => {
    fetch("/api/investors/twitter/options")
    .then(response => response.json())
    .then(data => {
        try {

            // Update Filter Input Fields with Query Values
            updateFilters()
        }
        catch(err){
            console.log(err)
        }
    })
}

const clear_filters = async () => {
    twitter_query = blank_twitter_query;
    updateFilters();
    get_inv();
}

// Fire Apply Filter after Offcanvas closing
var filtersOffcanvas = document.getElementById('filtersOffcanvas');
filtersOffcanvas.addEventListener('hidden.bs.offcanvas', function () {
    get_inv();
})

// Call Get twitter_inv data function
get_inv();
get_filters_options();
