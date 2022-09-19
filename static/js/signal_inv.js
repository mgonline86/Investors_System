// Get signal_inv data function
var query = {
    stage: [],
    min_invs_connect: "",
    max_invs_connect: "",
    min_investment: "",
    max_investment: "",
}
var prev_chunk = 0
var next_chunk = 0

async function get_signal_inv(page_chunk = null) {
    show_load_layout();
    var signal_inv_element = document.getElementById("signal_inv");

    signal_inv_element.innerHTML = "";

    var base_url = '/api/investors/signal'

    var url = page_chunk ? base_url + "?offset=" + String(page_chunk) : base_url;

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
        body: JSON.stringify(query)
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
                        let img = document.createElement('img');
                        img.src = current_investor["images"][0];
                        img.classList.add("img-fluid")
                        li.appendChild(img)
                    }
                    
                    // Appending Full name to the list element
                    if (current_investor["Full name"]) {
                        let h3 = document.createElement('h3');
                        h3.textContent = current_investor["Full name"];
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
            
            prev_btn.onclick = function() { get_signal_inv(prev_chunk) }
            next_btn.onclick = function() { get_signal_inv(next_chunk) }

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

// Call Get signal_inv data function
get_signal_inv();


/** HANDLING FILTERS */
var stageOptions = [
    {label: 'drug-delivery-pre-seed', value: 'drug-delivery-pre-seed',},
    {label: 'social-commerce-series-b', value: 'social-commerce-series-b',},
    {label: 'smb-software-seed', value: 'smb-software-seed',},
    {label: 'impact-series-a', value: 'impact-series-a',},
    {label: 'canada', value: 'canada',},
    {label: 'human-capital-hrtech-seed', value: 'human-capital-hrtech-seed',},
    {label: 'real-estate-proptech-seed',  value: 'real-estate-proptech-seed',},
    {label: 'ai-pre-seed', value: 'ai-pre-seed',},
    {label: 'saas-series-a', value: 'saas-series-a',},
    {label: 'local-services-series-b', value: 'local-services-series-b',},
    {label: 'health-it-series-b', value: 'health-it-series-b',},
    {label: 'smb-software-pre-seed', value: 'smb-software-pre-seed',},
    {label: 'iot-series-b', value: 'iot-series-b',},
    {label: 'retail-pre-seed', value: 'retail-pre-seed',},
    {label: 'mobility-series-b', value: 'mobility-series-b',},
    {label: 'e-commerce-seed', value: 'e-commerce-seed',},
    {label: 'enterprise-pre-seed', value: 'enterprise-pre-seed',},
    {label: 'climatetech-cleantech-series-a', value: 'climatetech-cleantech-series-a',},
    {label: 'cloud-infrastructure-pre-seed', value: 'cloud-infrastructure-pre-seed',},
    {label: 'gaming-esports-series-b', value: 'gaming-esports-series-b',},
    {label: 'material-science-seed', value: 'material-science-seed',},
    {label: 'social-networks-series-b', value: 'social-networks-series-b',},
    {label: 'gig-economy-series-a', value: 'gig-economy-series-a',},
    {label: 'transportationtech-seed', value: 'transportationtech-seed',},
    {label: 'medical-devices-seed', value: 'medical-devices-seed',},
    {label: 'payments-series-a', value: 'payments-series-a',},
    {label: 'agtech-series-b', value: 'agtech-series-b',},
    {label: 'british-columbia', value: 'british-columbia',},
    {label: 'data-services-series-a', value: 'data-services-series-a',},
    {label: 'saas-series-b', value: 'saas-series-b',},
    {label: 'fintech-series-b', value: 'fintech-series-b',},
    {label: 'sales-crm-seed', value: 'sales-crm-seed',},
    {label: 'manufacturing-pre-seed', value: 'manufacturing-pre-seed',},
    {label: 'insurance-seed', value: 'insurance-seed',},
    {label: 'enterprise-series-a', value: 'enterprise-series-a',},
    {label: 'local-services-seed', value: 'local-services-seed',},
    {label: 'mobility-seed', value: 'mobility-seed',},
    {label: 'real-estate-proptech-series-a', value: 'real-estate-proptech-series-a',},
    {label: 'lodging-hospitality-series-b', value: 'lodging-hospitality-series-b',},
    {label: 'diagnostics-series-a', value: 'diagnostics-series-a',},
    {label: 'media-content-seed', value: 'media-content-seed',},
    {label: 'direct-to-consumer-dtc-seed', value: 'direct-to-consumer-dtc-seed',},
    {label: 'education-series-a', value: 'education-series-a',},
    {label: 'security-series-b', value: 'security-series-b',},
    {label: 'cybersecurity-seed', value: 'cybersecurity-seed',},
    {label: 'audiotech-pre-seed', value: 'audiotech-pre-seed',},
    {label: 'games-series-b', value: 'games-series-b',},
    {label: 'ar-vr-seed', value: 'ar-vr-seed',},
    {label: 'pharmaceuticals-series-b', value: 'pharmaceuticals-series-b',},
    {label: 'travel-seed', value: 'travel-seed',},
    {label: 'health-it-pre-seed', value: 'health-it-pre-seed',},
    {label: 'supply-chain-tech-seed', value: 'supply-chain-tech-seed',},
    {label: 'consumer-health-series-a', value: 'consumer-health-series-a',},
    {label: 'manufacturing-seed', value: 'manufacturing-seed',},
    {label: 'cloud-infrastructure-series-a', value: 'cloud-infrastructure-series-a',},
    {label: 'govtech-pre-seed', value: 'govtech-pre-seed',},
    {label: 'analytics-pre-seed', value: 'analytics-pre-seed',},
    {label: 'digital-health-pre-seed', value: 'digital-health-pre-seed',},
    {label: 'agtech-pre-seed', value: 'agtech-pre-seed',},
    {label: 'mobility-pre-seed', value: 'mobility-pre-seed',},
    {label: 'messaging-pre-seed', value: 'messaging-pre-seed',},
    {label: 'space-seed', value: 'space-seed',},
    {label: 'legaltech-pre-seed', value: 'legaltech-pre-seed',},
    {label: 'social-commerce-pre-seed', value: 'social-commerce-pre-seed',},
    {label: 'pharmaceuticals-pre-seed', value: 'pharmaceuticals-pre-seed',},
    {label: 'analytics-seed', value: 'analytics-seed',},
    {label: 'transportationtech-series-b', value: 'transportationtech-series-b',},
    {label: 'chemicals-pre-seed', value: 'chemicals-pre-seed',},
    {label: 'mobility-series-a', value: 'mobility-series-a',},
    {label: 'wellness-fitness-series-b', value: 'wellness-fitness-series-b',},
    {label: 'israel', value: 'israel',},
    {label: 'autotech-pre-seed', value: 'autotech-pre-seed',},
    {label: 'direct-to-consumer-dtc-series-a', value: 'direct-to-consumer-dtc-series-a',},
    {label: 'ai-series-b', value: 'ai-series-b',},
    {label: 'gig-economy-seed', value: 'gig-economy-seed',},
    {label: 'enterprise-infrastructure-series-b', value: 'enterprise-infrastructure-series-b',},
    {label: 'enterprise-series-b', value: 'enterprise-series-b',},
    {label: 'space-pre-seed', value: 'space-pre-seed',},
    {label: 'hardware-series-a', value: 'hardware-series-a',},
    {label: 'crypto-web3-series-a', value: 'crypto-web3-series-a',},
    {label: 'travel-series-a', value: 'travel-series-a',},
    {label: 'retail-series-a', value: 'retail-series-a',},
    {label: 'payments-pre-seed', value: 'payments-pre-seed',},
    {label: 'consumer-internet-series-b', value: 'consumer-internet-series-b',},
    {label: 'energytech-series-a', value: 'energytech-series-a',},
    {label: 'cybersecurity-series-b', value: 'cybersecurity-series-b',},
    {label: 'cybersecurity-pre-seed', value: 'cybersecurity-pre-seed',},
    {label: 'iot-series-a', value: 'iot-series-a',},
    {label: 'london', value: 'london',},
    {label: 'autotech-series-a', value: 'autotech-series-a',},
    {label: 'education-series-b', value: 'education-series-b',},
    {label: 'crypto-web3-seed', value: 'crypto-web3-seed',},
    {label: 'logistics-pre-seed', value: 'logistics-pre-seed',},
    {label: 'wellness-fitness-series-a', value: 'wellness-fitness-series-a',},
    {label: 'fashion-seed', value: 'fashion-seed',},
    {label: 'fashion-series-b', value: 'fashion-series-b',},
    {label: 'boston-new-england', value: 'boston-new-england',},
    {label: 'smb-software-series-b', value: 'smb-software-series-b',},
    {label: 'gaming-esports-pre-seed', value: 'gaming-esports-pre-seed',},
    {label: 'entertainment-sports-seed', value: 'entertainment-sports-seed',},
    {label: 'ar-vr-series-b', value: 'ar-vr-series-b',},
    {label: 'insurance-series-a', value: 'insurance-series-a',},
    {label: 'human-capital-hrtech-pre-seed', value: 'human-capital-hrtech-pre-seed',},
    {label: 'payments-series-b', value: 'payments-series-b',},
    {label: 'education-seed', value: 'education-seed',},
    {label: 'insurance-series-b', value: 'insurance-series-b',},
    {label: 'who-invested-in-female-founders', value: 'who-invested-in-female-founders',},
    {label: 'pharmaceuticals-seed', value: 'pharmaceuticals-seed',},
    {label: 'messaging-series-a', value: 'messaging-series-a',},
    {label: 'legaltech-series-a', value: 'legaltech-series-a',},
    {label: 'ar-vr-pre-seed', value: 'ar-vr-pre-seed',},
    {label: 'space-series_a', value: 'space-series_a',},
    {label: 'enterprise-applications-seed', value: 'enterprise-applications-seed',},
    {label: 'media-content-series-b', value: 'media-content-series-b',},
    {label: 'austin', value: 'austin',},
    {label: 'semiconductors-seed', value: 'semiconductors-seed',},
    {label: 'retail-series-b', value: 'retail-series-b',},
    {label: 'midwest', value: 'midwest',},
    {label: 'diagnostics-seed', value: 'diagnostics-seed',},
    {label: 'colorado-utah', value: 'colorado-utah',},
    {label: 'energytech-series-b', value: 'energytech-series-b',},
    {label: 'therapeutics-series-a', value: 'therapeutics-series-a',},
    {label: 'marketingtech-pre-seed', value: 'marketingtech-pre-seed',},
    {label: 'wellness-fitness-pre-seed', value: 'wellness-fitness-pre-seed',},
    {label: 'saas-pre-seed', value: 'saas-pre-seed',},
    {label: 'semiconductors-series-a', value: 'semiconductors-series-a',},
    {label: 'drug-delivery-seed', value: 'drug-delivery-seed',},
    {label: 'travel-pre-seed', value: 'travel-pre-seed',},
    {label: 'health-hospital-services-series-a', value: 'health-hospital-services-series-a',},
    {label: 'chemicals-series-b', value: 'chemicals-series-b',},
    {label: 'enterprise-applications-pre-seed', value: 'enterprise-applications-pre-seed',},
    {label: 'ai-series-a', value: 'ai-series-a',},
    {label: 'marketingtech-series-b', value: 'marketingtech-series-b',},
    {label: 'smart-cities-urbantech-series-a', value: 'smart-cities-urbantech-series-a',},
    {label: 'diverse', value: 'diverse',},
    {label: 'biotech-pre-seed', value: 'biotech-pre-seed',},
    {label: 'deeptech-pre-seed', value: 'deeptech-pre-seed',},
    {label: 'transportationtech-pre-seed', value: 'transportationtech-pre-seed',},
    {label: 'direct-to-consumer-dtc-pre-seed', value: 'direct-to-consumer-dtc-pre-seed',},
    {label: 'agtech-seed', value: 'agtech-seed',},
    {label: 'enterprise-seed', value: 'enterprise-seed',},
    {label: 'iot-seed', value: 'iot-seed',},
    {label: 'therapeutics-pre-seed', value: 'therapeutics-pre-seed',},
    {label: 'pharmaceuticals-series-a', value: 'pharmaceuticals-series-a',},
    {label: 'robotics-pre-seed', value: 'robotics-pre-seed',},
    {label: 'smart-cities-urbantech-seed', value: 'smart-cities-urbantech-seed',},
    {label: 'who-were-founders', value: 'who-were-founders',},
    {label: 'energytech-pre-seed', value: 'energytech-pre-seed',},
    {label: 'e-commerce-series-b', value: 'e-commerce-series-b',},
    {label: 'diagnostics-series-b', value: 'diagnostics-series-b',},
    {label: 'deeptech-series-b', value: 'deeptech-series-b',},
    {label: 'saas-seed', value: 'saas-seed',},
    {label: 'enterprise-applications-series-b', value: 'enterprise-applications-series-b',},
    {label: 'digital-health-series-a', value: 'digital-health-series-a',},
    {label: 'sales-crm-pre-seed', value: 'sales-crm-pre-seed',},
    {label: 'human-capital-hrtech-series-b', value: 'human-capital-hrtech-series-b',},
    {label: 'drug-delivery-series-a', value: 'drug-delivery-series-a',},
    {label: 'biotech-seed', value: 'biotech-seed',},
    {label: 'impact-series-b', value: 'impact-series-b',},
    {label: 'constructiontech-series-a', value: 'constructiontech-series-a',},
    {label: 'marketplaces-series-b', value: 'marketplaces-series-b',},
    {label: 'media-content-pre-seed', value: 'media-content-pre-seed',},
    {label: 'hardware-series-b', value: 'hardware-series-b',},
    {label: 'supply-chain-tech-pre-seed', value: 'supply-chain-tech-pre-seed',},
    {label: 'logistics-seed', value: 'logistics-seed',},
    {label: 'autotech-series-b', value: 'autotech-series-b',},
    {label: 'autotech-seed', value: 'autotech-seed',},
    {label: 'enterprise-infrastructure-series-a', value: 'enterprise-infrastructure-series-a',},
    {label: 'enterprise-applications-series-a', value: 'enterprise-applications-series-a',},
    {label: 'social-commerce-series-a', value: 'social-commerce-series-a',},
    {label: 'smb-software-series-a', value: 'smb-software-series-a',},
    {label: 'therapeutics-series-b', value: 'therapeutics-series-b',},
    {label: 'iot-pre-seed', value: 'iot-pre-seed',},
    {label: 'audiotech-series-a', value: 'audiotech-series-a',},
    {label: 'cosmetics-series-a', value: 'cosmetics-series-a',},
    {label: 'social-networks-pre-seed', value: 'social-networks-pre-seed',},
    {label: 'who-invested-in-diverse-founders', value: 'who-invested-in-diverse-founders',},
    {label: 'fashion-series-a', value: 'fashion-series-a',},
    {label: 'marketplaces-series-a', value: 'marketplaces-series-a',},
    {label: 'parenting-families-series-a', value: 'parenting-families-series-a',},
    {label: 'human-capital-hrtech-series-a', value: 'human-capital-hrtech-series-a',},
    {label: 'semiconductors-pre-seed', value: 'semiconductors-pre-seed',},
    {label: 'audiotech-series-b', value: 'audiotech-series-b',},
    {label: 'food-and-beverage-series-a', value: 'food-and-beverage-series-a',},
    {label: 'social-networks-seed', value: 'social-networks-seed',},
    {label: 'angel-scout-and-solo-capitalists', value: 'angel-scout-and-solo-capitalists',},
    {label: 'social-commerce-seed', value: 'social-commerce-seed',},
    {label: 'web3-blockchain-series-b', value: 'web3-blockchain-series-b',},
    {label: 'deeptech-series-a', value: 'deeptech-series-a',},
    {label: 'entertainment-sports-series-b', value: 'entertainment-sports-series-b',},
    {label: 'female', value: 'female',},
    {label: 'cosmetics-pre-seed', value: 'cosmetics-pre-seed',},
    {label: 'future-of-work-series-a', value: 'future-of-work-series-a',},
    {label: 'hardware-seed', value: 'hardware-seed',},
    {label: 'marketplaces-seed', value: 'marketplaces-seed',},
    {label: 'cloud-infrastructure-seed', value: 'cloud-infrastructure-seed',},
    {label: 'biotech-series-a', value: 'biotech-series-a',},
    {label: 'chemicals-seed', value: 'chemicals-seed',},
    {label: 'web3-blockchain-pre-seed', value: 'web3-blockchain-pre-seed',},
    {label: 'consumer-internet-pre-seed', value: 'consumer-internet-pre-seed',},
    {label: 'health-hospital-services-series-b', value: 'health-hospital-services-series-b',},
    {label: 'parenting-families-pre-seed', value: 'parenting-families-pre-seed',},
    {label: 'gig-economy-series-b', value: 'gig-economy-series-b',},
    {label: 'real-estate-proptech-pre-seed', value: 'real-estate-proptech-pre-seed',},
    {label: 'real-estate-proptech-series-b', value: 'real-estate-proptech-series-b',},
    {label: 'agtech-series-a', value: 'agtech-series-a',},
    {label: 'future-of-work-series-b', value: 'future-of-work-series-b',},
    {label: 'web3-blockchain-seed', value: 'web3-blockchain-seed',},
    {label: 'creator-passion-economy-series-a', value: 'creator-passion-economy-series-a',},
    {label: 'logistics-series_b', value: 'logistics-series_b',},
    {label: 'digital-health-series-b', value: 'digital-health-series-b',},
    {label: 'health-hospital-services-seed', value: 'health-hospital-services-seed',},
    {label: 'crypto-web3-pre-seed', value: 'crypto-web3-pre-seed',},
    {label: 'enterprise-infrastructure-pre-seed', value: 'enterprise-infrastructure-pre-seed',},
    {label: 'robotics-series-a', value: 'robotics-series-a',},
    {label: 'lodging-hospitality-pre-seed', value: 'lodging-hospitality-pre-seed',},
    {label: 'crypto-web3-series-b', value: 'crypto-web3-series-b',},
    {label: 'messaging-series-b', value: 'messaging-series-b',},
    {label: 'advertising-series-b', value: 'advertising-series-b',},
    {label: 'sales-crm-series-a', value: 'sales-crm-series-a',},
    {label: 'retail-seed', value: 'retail-seed',},
    {label: 'developer-tools-pre-seed', value: 'developer-tools-pre-seed',},
    {label: 'smart-cities-urbantech-series-b', value: 'smart-cities-urbantech-series-b',},
    {label: 'insurance-pre-seed', value: 'insurance-pre-seed',},
    {label: 'fintech-pre-seed', value: 'fintech-pre-seed',},
    {label: 'gaming-esports-seed', value: 'gaming-esports-seed',},
    {label: 'food-and-beverage-pre-seed', value: 'food-and-beverage-pre-seed',},
    {label: 'deeptech-seed', value: 'deeptech-seed',},
    {label: 'marketingtech-series-a', value: 'marketingtech-series-a',},
    {label: 'material-science-series-b', value: 'material-science-series-b',},
    {label: 'ar-vr-series-a', value: 'ar-vr-series-a',},
    {label: 'e-commerce-series-a', value: 'e-commerce-series-a',},
    {label: 'govtech-seed', value: 'govtech-seed',},
    {label: 'climatetech-cleantech-pre-seed', value: 'climatetech-cleantech-pre-seed',},
    {label: 'social-networks-series-a', value: 'social-networks-series-a',},
    {label: 'cosmetics-series-b', value: 'cosmetics-series-b',},
    {label: 'gig-economy-pre-seed', value: 'gig-economy-pre-seed',},
    {label: 'semiconductors-series-b', value: 'semiconductors-series-b',},
    {label: 'gaming-esports-series-a', value: 'gaming-esports-series-a',},
    {label: 'payments-seed', value: 'payments-seed',},
    {label: 'material-science-pre-seed', value: 'material-science-pre-seed',},
    {label: 'los-angeles-southern-california', value: 'los-angeles-southern-california',},
    {label: 'creator-passion-economy-pre-seed', value: 'creator-passion-economy-pre-seed',},
    {label: 'games-series-a', value: 'games-series-a',},
    {label: 'web3-blockchain-series-a', value: 'web3-blockchain-series-a',},
    {label: 'logistics-series_a', value: 'logistics-series_a',},
    {label: 'manufacturing-series_a', value: 'manufacturing-series_a',},
    {label: 'space-series_b', value: 'space-series_b',},
    {label: 'transportationtech-series-a', value: 'transportationtech-series-a',},
    {label: 'security-pre-seed', value: 'security-pre-seed',},
    {label: 'developer-tools-series-a', value: 'developer-tools-series-a',},
    {label: 'washington-d-c', value: 'washington-d-c',},
    {label: 'developer-tools-series-b', value: 'developer-tools-series-b',},
    {label: 'security-seed', value: 'security-seed',},
    {label: 'san-francisco-bay-area', value: 'san-francisco-bay-area',},
    {label: 'entertainment-sports-series-a', value: 'entertainment-sports-series-a',},
    {label: 'food-and-beverage-series-b', value: 'food-and-beverage-series-b',},
    {label: 'supply-chain-tech-series-a', value: 'supply-chain-tech-series-a',},
    {label: 'cloud-infrastructure-series-b', value: 'cloud-infrastructure-series-b',},
    {label: 'developer-tools-seed', value: 'developer-tools-seed',},
    {label: 'hardware-pre-seed', value: 'hardware-pre-seed',},
    {label: 'legaltech-series-b', value: 'legaltech-series-b',},
    {label: 'medical-devices-series-b', value: 'medical-devices-series-b',},
    {label: 'entertainment-sports-pre-seed', value: 'entertainment-sports-pre-seed',},
    {label: 'digital-health-seed', value: 'digital-health-seed',},
    {label: 'raleigh-durham-southeast-us', value: 'raleigh-durham-southeast-us',},
    {label: 'health-hospital-services-pre-seed', value: 'health-hospital-services-pre-seed',},
    {label: 'audiotech-seed', value: 'audiotech-seed',},
    {label: 'impact-pre-seed', value: 'impact-pre-seed',},
    {label: 'lodging-hospitality-series-a', value: 'lodging-hospitality-series-a',},
    {label: 'fintech-series-a', value: 'fintech-series-a',},
    {label: 'future-of-work-pre-seed', value: 'future-of-work-pre-seed',},
    {label: 'enterprise-infrastructure-seed', value: 'enterprise-infrastructure-seed',},
    {label: 'games-pre-seed', value: 'games-pre-seed',},
    {label: 'analytics-series-b', value: 'analytics-series-b',},
    {label: 'messaging-seed', value: 'messaging-seed',},
    {label: 'new-york-city', value: 'new-york-city',},
    {label: 'consumer-internet-seed', value: 'consumer-internet-seed',},
    {label: 'data-services-seed', value: 'data-services-seed',},
    {label: 'therapeutics-seed', value: 'therapeutics-seed',},
    {label: 'energytech-seed', value: 'energytech-seed',},
    {label: 'climatetech-cleantech-series-b', value: 'climatetech-cleantech-series-b',},
    {label: 'wellness-fitness-seed', value: 'wellness-fitness-seed',},
    {label: 'fashion-pre-seed', value: 'fashion-pre-seed',},
    {label: 'robotics-series-b', value: 'robotics-series-b',},
    {label: 'medical-devices-pre-seed', value: 'medical-devices-pre-seed',},
    {label: 'drug-delivery-series-b', value: 'drug-delivery-series-b',},
    {label: 'constructiontech-series-b', value: 'constructiontech-series-b',},
    {label: 'cybersecurity-series-a', value: 'cybersecurity-series-a',},
    {label: 'advertising-series-a', value: 'advertising-series-a',},
    {label: 'future-of-work-seed', value: 'future-of-work-seed',},
    {label: 'data-services-pre-seed', value: 'data-services-pre-seed',},
    {label: 'impact-seed', value: 'impact-seed',},
    {label: 'smart-cities-urbantech-pre-seed', value: 'smart-cities-urbantech-pre-seed',},
    {label: 'diagnostics-pre-seed', value: 'diagnostics-pre-seed',},
    {label: 'consumer-internet-series-a', value: 'consumer-internet-series-a',},
    {label: 'creator-passion-economy-seed', value: 'creator-passion-economy-seed',},
    {label: 'parenting-families-seed', value: 'parenting-families-seed',},
    {label: 'chemicals-series-a', value: 'chemicals-series-a',},
    {label: 'cosmetics-seed', value: 'cosmetics-seed',},
    {label: 'fintech-seed', value: 'fintech-seed',},
    {label: 'analytics-series-a', value: 'analytics-series-a',},
    {label: 'consumer-health-pre-seed', value: 'consumer-health-pre-seed',},
    {label: 'material-science-series-a', value: 'material-science-series-a',},
    {label: 'medical-devices-series-a', value: 'medical-devices-series-a',},
    {label: 'supply-chain-tech-series-b', value: 'supply-chain-tech-series-b',},
    {label: 'media-content-series-a', value: 'media-content-series-a',},
    {label: 'food-and-beverage-seed', value: 'food-and-beverage-seed',},
    {label: 'lodging-hospitality-seed', value: 'lodging-hospitality-seed',},
    {label: 'consumer-health-series-b', value: 'consumer-health-series-b',},
    {label: 'travel-series-b', value: 'travel-series-b',},
    {label: 'seattle-portland', value: 'seattle-portland',},
    {label: 'parenting-families-series-b', value: 'parenting-families-series-b',},
    {label: 'health-it-seed', value: 'health-it-seed',},
    {label: 'local-services-series-a', value: 'local-services-series-a',},
    {label: 'biotech-series-b', value: 'biotech-series-b',},
    {label: 'marketingtech-seed', value: 'marketingtech-seed',},
    {label: 'games-seed', value: 'games-seed',},
    {label: 'security-series-a', value: 'security-series-a',},
    {label: 'robotics-seed', value: 'robotics-seed',},
    {label: 'direct-to-consumer-dtc-series-b', value: 'direct-to-consumer-dtc-series-b',},
    {label: 'marketplaces-pre-seed', value: 'marketplaces-pre-seed',},
    {label: 'consumer-health-seed', value: 'consumer-health-seed',},
    {label: 'legaltech-seed', value: 'legaltech-seed',},
    {label: 'advertising-pre-seed', value: 'advertising-pre-seed',},
    {label: 'climatetech-cleantech-seed', value: 'climatetech-cleantech-seed',},
    {label: 'sales-crm-series-b', value: 'sales-crm-series-b',},
    {label: 'health-it-series-a', value: 'health-it-series-a',},
    {label: 'manufacturing-series_b', value: 'manufacturing-series_b',},
    {label: 'govtech-series-a', value: 'govtech-series-a',},
    {label: 'data-services-series-b', value: 'data-services-series-b',},
    {label: 'creator-passion-economy-series-b', value: 'creator-passion-economy-series-b',},
    {label: 'govtech-series-b', value: 'govtech-series-b',},
    {label: 'e-commerce-pre-seed', value: 'e-commerce-pre-seed',},
    {label: 'ai-seed', value: 'ai-seed',},
    {label: 'constructiontech-pre-seed', value: 'constructiontech-pre-seed',},
    {label: 'advertising-seed', value: 'advertising-seed',},
    {label: 'local-services-pre-seed', value: 'local-services-pre-seed',},
    {label: 'constructiontech-seed', value: 'constructiontech-seed',},
    {label: 'education-pre-seed', value: 'education-pre-seed'},
]

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

// var myOptions2 = [
//     { label: 'Options 1', value: '1', alias: 'custom label for search' },
//     { label: 'Options 2', value: '2', description: 'custom description for label', customData: '' },
//     { label: 'Options 3', value: '3' },
//     { label: 'Options 100000', value: '100000' },
// ]

// VirtualSelect.init({
//     ele: '#example-select-2',
//     options: myOptions2,
//     search: true,
//     // Enable the multi select support
//     multiple: true,
//     // Customize the placeholder text
//     placeholder: 'Select second',
//     // Text to show when no options to show
//     noOptionsText: 'No results found',
//     // Text to show when no results on search
//     noSearchResultsTex: 'No results found',
// });

document.querySelector('#stage-select').addEventListener('change', function() {
    query.stage = this.value;
});

// Handle Investor connections amount
const handleMinInvCon = () => {
    var minConnValue = document.getElementById("min-invs-connect").value;
    query.min_invs_connect = minConnValue;
}
const handleMaxInvCon = () => {
    var maxConnValue = document.getElementById("max-invs-connect").value;
    query.max_invs_connect = maxConnValue;
}

// // Handle Investor amount
// const handleMinInvest = () => {
//     var minInvValue = document.getElementById("min-investment").value;
//     query.min_investment = minInvValue;
// }
// const handleMaxInvest = () => {
//     var maxInvValue = document.getElementById("max-investment").value;
//     query.max_investment = maxInvValue;
// }