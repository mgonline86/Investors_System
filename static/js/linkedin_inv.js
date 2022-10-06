// GlOBAL VARIABLES
var prev_chunk = 0
var next_chunk = 0


// Define Filter Input Fields
var minSweetSpotInput = document.querySelector("#min-sweet-spot");
var maxSweetSpotInput = document.querySelector("#max-sweet-spot");
var positionInput = document.querySelector("#position-select");
var newStageInput = document.querySelector("#new-stage-select");
var stageInput = document.querySelector("#stage-select");
var stageAllCheckInput = document.querySelector("#stage-all-check");
var profileNameInput = document.querySelector("#searchProfileName");
var minInvsConnctInput = document.querySelector("#min-invs-connect");
var maxInvsConnctInput = document.querySelector("#max-invs-connect");
var minInvsInput = document.querySelector("#min-investment");
var maxInvsInput = document.querySelector("#max-investment");



async function get_inv(page_chunk = null) {
    show_load_layout();

    //Validate Inputs
    var valid = validate_inputs();

    if (!valid) {
        hide_load_layout();
        return
    }

    var linkedin_inv_element = document.getElementById("inv_list");

    linkedin_inv_element.innerHTML = "";

    var base_url = '/api/investors/linkedin'

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
        body: JSON.stringify(linkedin_query)
    })
    .then(response => response.json())
    .then(data => {
        try {
            var {investors, total_count, query_count, next_chunk, prev_chunk, limit, no_linkedin_count} = data
            if (investors.length > 0) {
              for (let i = 0; i < investors.length; i++) {
                let current_investor = investors[i]

                // Creating a List Item
                let li = document.createElement('li');
                li.classList.add("list-group-item");

                // // Appending main image to the list element
                // if (current_investor["images"].length !== 0) {
                //     let div = document.createElement('div');
                //     div.style.cssText = 'position:relative';
                //     div.classList.add("invest-img_container")
                    
                //     let img = document.createElement('img');
                //     img.src = current_investor["images"][0];
                //     img.classList.add("img-fluid")
                //     img.classList.add("invest-img")
                    
                //     let zoomOverlay = document.createElement('img');
                //     zoomOverlay.src = "/static/img/zoom-in.png";
                //     zoomOverlay.classList.add("img-zoom")
                //     zoomOverlay.setAttribute("data-toggle", "modal");
                //     zoomOverlay.setAttribute("data-target", "#viewImageModal");
                //     zoomOverlay.onclick = function() { toggleviewImageModal(this) }
                //     //data-toggle="modal" data-target="#exampleModalCenter"
                    

                //     div.appendChild(img)
                //     div.appendChild(zoomOverlay)
                    
                //     li.appendChild(div)
                // }
                
                // // Appending Profile Name to the list element
                // if (current_investor["Profile Name"]) {
                //     let h3 = document.createElement('h3');
                //     h3.textContent = current_investor["Profile Name"];
                //     li.appendChild(h3)
                    
                // }
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
                linkedin_inv_element.appendChild(li);
            }
            }
            else{
                // if no investors found for the current query
                let p = document.createElement('p');
                    p.classList.add("h3")
                    p.classList.add("text-info")
                    p.textContent = "NO RESULT FOUND!";
                    linkedin_inv_element.appendChild(p)
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
            if (no_linkedin_count > 0) {
                excluded_count_ele.textContent = "(" + String(no_linkedin_count) + " results were excluded, having no LinkedIn Profile)"
            }

            hide_load_layout();
        } catch (err) {
            console.log(err)
        }
    });

}

/** HANDLING FILTERS */
//added by hesham



//newstage filter
var newStageOptions = [
    {label: 'pre-seed', value: 'pre-seed',},
    {label: 'seed', value: 'seed',},
    {label: 'post-seed', value: 'post-seed',},
    {label: 'series-a', value: 'series-a',},
    {label: 'series-b', value: 'series-b',},
    {label: 'series-c', value: 'series-c',},
    {label: 'series-d', value: 'series-d',},
    ]

VirtualSelect.init({
    ele: '#new-stage-select',
    options: newStageOptions,
    search: true,
    // Enable the multi select support
    multiple: true,
    // Customize the placeholder text
    placeholder: 'Select first',
    // Text to show when no options to show
    noOptionsText: 'No results found',
    // Text to show when no results on search
    noSearchResultsTex: 'No results found',
});

document.querySelector('#new-stage-select').addEventListener('change', function() {
    linkedin_query.newstage = this.value;
});
///// added by hesham



const handleStageMatchAll = () => {
    var stageMatchAll = document.getElementById("stage-all-check").checked;
    console.log(stageMatchAll)
    linkedin_query.stage_match_all = stageMatchAll;
}

//Handle sweet_spot filter
const handleMinSweet = () => {
    var minSweetValue = document.getElementById("min-sweet-spot").value;
    linkedin_query.min_sweet_spot = minSweetValue;
}
const handleMaxSweet = () => {
    var maxSweetValue = document.getElementById("max-sweet-spot").value;
    linkedin_query.max_sweet_spot = maxSweetValue;
}



// Handle Investor connections amount
const handleMinInvCon = () => {
    var minConnValue = document.getElementById("min-invs-connect").value;
    linkedin_query.min_invs_connect = minConnValue;
}
const handleMaxInvCon = () => {
    var maxConnValue = document.getElementById("max-invs-connect").value;
    linkedin_query.max_invs_connect = maxConnValue;
}


// HANDLE SEARCH INPUTS MECHANISM
let searchInputs = document.querySelectorAll(".searchInput")

searchInputs.forEach(searchInput => {
    searchInput.addEventListener('focus',(event) => {
      event.target.nextElementSibling.classList.remove("d-none");
    })
    undefined
    searchInput.addEventListener('blur',(event) => {
      event.target.nextElementSibling.classList.add("d-none");
    })
});

// Handle Search Profile Name
const handleSearchProfileName = debounce(async () => {
    let searchProfileName = document.getElementById("searchProfileName");
    let searchValue = searchProfileName.value.trim();
    linkedin_query.profile_name = searchValue
    if (searchValue !== "") {
        let url = "/api/investors/linkedin/count";
        fetch(url, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "field" : "Profile Name",
                "query" : searchValue,
            })
        })
        .then(response => response.json())
        .then(data => {
            try {
                searchProfileName.nextElementSibling.textContent = String(data.count) + " Matches for " + searchValue
            }
            catch(err){
                console.log(err)
            }
        })
    }
    else{
        searchProfileName.nextElementSibling.textContent = "0 Matches"
    }
})

// Handle Investor amount
const handleMinInvest = () => {
    var minInvValue = document.getElementById("min-investment").value;
    linkedin_query.min_investment = minInvValue;
}
const handleMaxInvest = () => {
    var maxInvValue = document.getElementById("max-investment").value;
    linkedin_query.max_investment = maxInvValue;
}


// Validate Critical Inputs
const validate_inputs = () =>{
    // Clear any in-valid classes on inputs
    var inputElements = document.querySelectorAll(".form-control")
    inputElements.forEach(ele => {
        ele.classList.remove("is-invalid");
    })

    // Validate Investment Range 
    const filtersOffcanvas = new bootstrap.Offcanvas('#filtersOffcanvas')
    var minInvEle = document.getElementById("min-investment");
    var maxInvEle = document.getElementById("max-investment");
    var minInvValue = minInvEle.value;
    var maxInvValue = maxInvEle.value;

    if (minInvValue.trim() !== "" && maxInvValue.trim() === "") {
        filtersOffcanvas.show()
        maxInvEle.classList.add("is-invalid");
        maxInvEle.focus();
        return false;
    }
    if (maxInvValue.trim() !== "" && minInvValue.trim() === "") {
        filtersOffcanvas.show()
        minInvEle.classList.add("is-invalid");
        minInvEle.focus();
        return false;
    }

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
        minSweetSpotInput.value = linkedin_query.min_sweet_spot;
        maxSweetSpotInput.value = linkedin_query.max_sweet_spot;
        positionInput.setValue(linkedin_query.position)
        newStageInput.setValue(linkedin_query.newstage)
        stageInput.setValue(linkedin_query.stage)
        stageAllCheckInput.checked = linkedin_query.stage_match_all
        profileNameInput.value = linkedin_query.profile_name;
        minInvsConnctInput.value = linkedin_query.min_invs_connect
        maxInvsConnctInput.value = linkedin_query.max_invs_connect
        minInvsInput.value = linkedin_query.min_investment
        maxInvsInput.value = linkedin_query.max_investment
    } catch (err) {
        console.log(err)        
    }
} 


// Fill the Option Lists in Filters
const get_filters_options = async () => {
    fetch("/api/investors/linkedin/options")
    .then(response => response.json())
    .then(data => {
        try {
            var stageOptions = data.options.stage_options.map(opt => {return {label: opt, value: opt,}})
            VirtualSelect.init({
                ele: '#stage-select',
                options: stageOptions,
                search: true,
                // Enable the multi select support
                multiple: true,
                // Customize the placeholder text
                placeholder: 'Select first',
                // Text to show when no options to show
                noOptionsText: 'No results found',
                // Text to show when no results on search
                noSearchResultsTex: 'No results found',
            });
            // Handle old stage filter
            document.querySelector('#stage-select').addEventListener('change', function() {
                linkedin_query.stage = this.value;
            });

            //Handle position filter
            var positionOptions = data.options.position_options.map(opt => {return {label: opt, value: opt,}});

            VirtualSelect.init({
                ele: '#position-select',
                options: positionOptions,
                search: true,
                // Enable the multi select support
                multiple: false,
                // Customize the placeholder text
                placeholder: 'Search',
                // Text to show when no options to show
                noOptionsText: 'No results found',
                // Text to show when no results on search
                noSearchResultsTex: 'No results found',
            });

            document.querySelector('#position-select').addEventListener('change', function() {
                linkedin_query.position = this.value;
            });


            // Update Filter Input Fields with Query Values
            updateFilters()
        }
        catch(err){
            console.log(err)
        }
    })
}

const clear_filters = async () => {
    linkedin_query = blank_linkedin_query;
    updateFilters();
    get_inv();
}

// Call Get linkedin_inv data function
get_inv();
get_filters_options();

// Fire Apply Filter after Offcanvas closing
var filtersOffcanvas = document.getElementById('filtersOffcanvas');
filtersOffcanvas.addEventListener('hidden.bs.offcanvas', function () {
    get_inv();
})