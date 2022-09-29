// GlOBAL VARIABLES
var prev_chunk = 0;
var next_chunk = 0;
var getFinalResult = false;


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



async function get_inv(page_chunk = null, finalResults=false) {
    // Toggle Final Results Flag    
    getFinalResult = finalResults

    show_load_layout();

    //Validate Inputs
    var valid = validate_inputs();

    if (!valid) {
        hide_load_layout();
        return
    }

    var signal_inv_element = document.getElementById("inv_list");

    signal_inv_element.innerHTML = "";

    var base_url = '/api/investors/signal'


    // Creating Query Paramters for Pagination & FinalResults
    var queryParams = []

    if (page_chunk) {
        var offset = "offset=" + String(page_chunk);
        queryParams.push(offset)
    }

    if (getFinalResult) {
        var finalResultTag = "finalResults=" + String(getFinalResult);
        queryParams.push(finalResultTag)
    }

    if (queryParams.length > 0) {
        base_url += "?"
    }

    var url = base_url + String(queryParams.join("&"));

    var prev_btn = document.getElementById("prev-link");
    var next_btn = document.getElementById("next-link");

    var query_count_ele = document.getElementById("query_count");
    var total_count_ele = document.getElementById("total_count");
    var count_percent_ele = document.getElementById("count_percent");


    fetch(url, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(signal_query)
    })
    .then(response => response.json())
    .then(data => {
        try {
            var {investors, total_count, query_count, next_chunk, prev_chunk, limit} = data
            if (investors.length > 0) {
              for (let i = 0; i < investors.length; i++) {
                let current_investor = investors[i]

                // Creating a List Item
                let li = document.createElement('li');
                li.classList.add("list-group-item");

                // Appending main image to the list element
                if (current_investor["images"].length !== 0) {
                    let div = document.createElement('div');
                    div.style.cssText = 'position:relative';
                    div.classList.add("invest-img_container")
                    
                    let img = document.createElement('img');
                    img.src = current_investor["images"][0];
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
                
                // Appending Profile Name to the list element
                if (current_investor["Profile Name"]) {
                    let h3 = document.createElement('h3');
                    h3.textContent = current_investor["Profile Name"];
                    li.appendChild(h3)
                    
                }
                // Appending Position to the list element
                if (current_investor["Position"]) {
                    let p = document.createElement('p');
                    p.classList.add("text-muted")
                    p.textContent = current_investor["Position"];
                    li.appendChild(p)
                }

                // Appending RenderJson to the list element
                li.appendChild(
                    renderjson(current_investor)
                );
                signal_inv_element.appendChild(li);
            }
            }
            else{
                // if no investors found for the current query
                let p = document.createElement('p');
                    p.classList.add("h3")
                    p.classList.add("text-info")
                    p.textContent = "NO RESULT FOUND!";
                    signal_inv_element.appendChild(p)
            }
            
            prev_btn.onclick = function() { get_inv(prev_chunk, getFinalResult) }
            next_btn.onclick = function() { get_inv(next_chunk, getFinalResult) }

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
    signal_query.newstage = this.value;
});
///// added by hesham



const handleStageMatchAll = () => {
    var stageMatchAll = document.getElementById("stage-all-check").checked;
    console.log(stageMatchAll)
    signal_query.stage_match_all = stageMatchAll;
}

//Handle sweet_spot filter
const handleMinSweet = () => {
    var minSweetValue = document.getElementById("min-sweet-spot").value;
    signal_query.min_sweet_spot = minSweetValue;
}
const handleMaxSweet = () => {
    var maxSweetValue = document.getElementById("max-sweet-spot").value;
    signal_query.max_sweet_spot = maxSweetValue;
}



// Handle Investor connections amount
const handleMinInvCon = () => {
    var minConnValue = document.getElementById("min-invs-connect").value;
    signal_query.min_invs_connect = minConnValue;
}
const handleMaxInvCon = () => {
    var maxConnValue = document.getElementById("max-invs-connect").value;
    signal_query.max_invs_connect = maxConnValue;
}


// HANDLE SEARCH INPUTS MECHANISM
let searchInputs = document.querySelectorAll(".searchInput")

searchInputs.forEach(searchInput => {
    searchInput.addEventListener('focus',(event) => {
      event.target.nextElementSibling.classList.remove("d-none");
    })

    searchInput.addEventListener('blur',(event) => {
      event.target.nextElementSibling.classList.add("d-none");
    })
});

// Handle Search Profile Name
const handleSearchProfileName = debounce(async () => {
    let searchProfileName = document.getElementById("searchProfileName");
    let searchValue = searchProfileName.value.trim();
    signal_query.profile_name = searchValue
    if (searchValue !== "") {
        let url = "/api/investors/signal/count";
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
    signal_query.min_investment = minInvValue;
}
const handleMaxInvest = () => {
    var maxInvValue = document.getElementById("max-investment").value;
    signal_query.max_investment = maxInvValue;
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
        minSweetSpotInput.value = signal_query.min_sweet_spot;
        maxSweetSpotInput.value = signal_query.max_sweet_spot;
        positionInput.setValue(signal_query.position)
        newStageInput.setValue(signal_query.newstage)
        stageInput.setValue(signal_query.stage)
        stageAllCheckInput.checked = signal_query.stage_match_all
        profileNameInput.value = signal_query.profile_name;
        minInvsConnctInput.value = signal_query.min_invs_connect
        maxInvsConnctInput.value = signal_query.max_invs_connect
        minInvsInput.value = signal_query.min_investment
        maxInvsInput.value = signal_query.max_investment
    } catch (err) {
        console.log(err)        
    }
} 


// Fill the Option Lists in Filters
const get_filters_options = async () => {
    fetch("/api/investors/signal/options")
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
                signal_query.stage = this.value;
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
                signal_query.position = this.value;
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
    signal_query = blank_signal_query;
    updateFilters();
    get_inv();
}

// Call Get signal_inv data function
get_inv();
get_filters_options();

// Fire Apply Filter after Offcanvas closing
var filtersOffcanvas = document.getElementById('filtersOffcanvas');
filtersOffcanvas.addEventListener('hidden.bs.offcanvas', function () {
    get_inv();
})