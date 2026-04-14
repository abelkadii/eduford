function ColorMix1(dyePercentage, color1, color2) {
    // Trim percentage value to be between 0 and 100
    dyePercentage = Math.min(100, Math.max(0, dyePercentage));
  
    // Convert percentage to a value between 0 and 1
    let mixRatio = dyePercentage / 100;
  
    // Extract RGB values from each color
    let red1 = parseInt(color1.substring(1, 3), 16);
    let green1 = parseInt(color1.substring(3, 5), 16);
    let blue1 = parseInt(color1.substring(5, 7), 16);
  
    let red2 = parseInt(color2.substring(1, 3), 16);
    let green2 = parseInt(color2.substring(3, 5), 16);
    let blue2 = parseInt(color2.substring(5, 7), 16);
  
    // Interpolate RGB values based on the mix ratio
    let mixedRed = Math.round(red1 * (1 - mixRatio) + red2 * mixRatio);
    let mixedGreen = Math.round(green1 * (1 - mixRatio) + green2 * mixRatio);
    let mixedBlue = Math.round(blue1 * (1 - mixRatio) + blue2 * mixRatio);
  
    // Convert interpolated RGB values back to hexadecimal
    let mixedColor = '#' + 
        mixedRed.toString(16).padStart(2, '0') +
        mixedGreen.toString(16).padStart(2, '0') +
        mixedBlue.toString(16).padStart(2, '0');
  
    return mixedColor;
  }
function output(response){
    let output = $('<div>');
    output.id='output'
    output.empty(); // Clear the content of the element
    output.append(" <b>User Details</b>:<br>________________<br>");
    output.append(
        "<b>Name</b>: &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp" + response.name + "<br>"
    );
    output.append(
        "<b>Age</b>: &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp" +
        response.age +
        "yr<br>"
    );
    // console.log(response.weight.length);
    if (!response.weight) {
        output.append("<b>Weight</b>: &nbsp&nbsp&nbsp " + "-" + "<br>");
    } else {
        output.append(
        "<b>Weight</b>: &nbsp&nbsp&nbsp " + response.weight + "kg<br>"
        );
    }

    if (response.height.length == 0) {
        output.append(
        "<b>Height</b>: &nbsp&nbsp&nbsp&nbsp  " + "-" + "<br>"
        );
    } else {
        output.append(
        "<b>Height</b>: &nbsp&nbsp&nbsp " + response.height + "cm<br>"
        );
    }

    output.append(
        "<b>Gender</b>:&nbsp&nbsp&nbsp&nbsp " + response.gender + "<br>"
    );

    // console.log((response.alcohol).length);

    if (response.cigar === undefined) {
        output.append(
        "<b>Cigar</b>: &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp" + "No" + "<br>"
        );
    } else {
        output.append(
        "<b>Cigar</b>: &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp" + response.cigar + "<br>"
        );
    }

    if (response.age > 16) {
        if (response.alcohol?.length == 5) {
        output.append(
            "<b>Alcohol</b>:&nbsp&nbsp&nbsp&nbsp " + "Yes" + "<br>"
        );
        } else {
        output.append(
            "<b>Alcohol</b>:&nbsp&nbsp&nbsp&nbsp " + "No" + "<br>"
        );
        }

        if (response.gender === "male") {
        output.append(
            "<b>Pregnant</b>: &nbsp" + "not-applicable" + "<br>"
        );
        output.append(
            "<b>trimister</b>: &nbsp" + "not-applicable" + "<br>" + "<br>"
        );
        } else {
        output.append("<b>Pregnant</b>: &nbsp" + response.pregnant + "<br>");

        if (response.pregnant === "Yes") {
            let isSubset = ["A", "B", "C", "D"].every((item) =>
            response.trimister.includes(item)
            );

            if (isSubset) {
            output.append(
                "<b>trimister</b>: &nbsp" + "1" + "<br>" + "<br>"
            );
            } else {
            output.append(
                "<b>trimister</b>: &nbsp" + "2/3" + "<br>" + "<br>"
            );
            }
        } else {
            output.append(
            "<b>trimister</b>: &nbsp" + "not-applicable" + "<br>" + "<br>"
            );
        }
        }
    } else {
        output.append(
        "<b>Alcohol</b>:&nbsp&nbsp&nbsp&nbsp " + "No" + "<br>"
        );
        output.append(
        "<b>Cigar</b>: &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp" + "No" + "<br>"
        );
        output.append("<b>Pregnant</b>: &nbsp" + "No" + "<br>");
        output.append(
        "<b>trimister</b>: &nbsp" + "not-applicable" + "<br>" + "<br>"
        );
    }
    return output
}



function results(response, symptoms){
    let resultsElement = document.createElement("div");
    console.log(resultsElement)
    // document.querySelector('body').appendChild(resultsElement)
    resultsElement.id = "results"
    resultsElement.innerHTML = ""; // Clear previous results
    resultsElement.innerHTML =
    "Based on the given symptoms: <b>" +
    symptoms.join(", ") +
    "</b><br><br>";
    if(response.length>0 && response[0].probability>=50){
        resultsElement.innerHTML+=`
        <div class="results-possible-match">
            <h2>Possible Disease Match !!!</h2>
            <h6>based on your selection you might have <span>${response[0].disease}</span></h6>
            <h4>Additional Information: </h4>
            <h5>${response[0].description}</h5>
        </div>
        `
      }else{
        resultsElement.innerHTML+=`
        <div class="results-possible-match">
            <h2>No Disease Match !!!</h2>
            <h6>based on your selection you are <span style="color: green;font-weight: bold;">healthy</span></h6>
        </div>
        `
      }
    for (let i = 0; i < response.length; i++) {
    let disease = response[i].disease;
    let probability = response[i].probability;
    let precautions = response[i].precautions;

    let resultElement = document.createElement("div");

    let resultElementProbability = document.createElement("span");
    resultElementProbability.innerHTML =
        "Possibility of having '" + disease;

    // let resultElementButton = document.createElement("i");
    // resultElementButton.className = "fas fa-info-circle";
    // resultElementButton.id = disease;

    let resultElementProbability1 = document.createElement("span");
    if (probability >= 50) {
        resultElementProbability1.innerHTML =
        "':<span style='color:red;'><b>" +
        probability +
        "% </b></span> ";
    } else {
        resultElementProbability1.innerHTML =
        "':<span style='color:green;'><b>" +
        probability +
        "%</b> <br><i>as probability is below THRESHOLD--we recommend you to consult <b>"+
        response[i].doc_type+"</b></i> </span> ";
    }

    // let nextitem = document.createElement("span");
    // nextitem.innerHTML = "_________________________________";

    let precdiv = document.createElement("div");
    precdiv.id = "precdiv";
    // precdiv.style.border="2px solid black";

    let resultElement1 = document.createElement("div");
    resultElement1.style.width = `${Math.floor(probability)}%`
    let mixedColor = ColorMix1(probability, '#5be85b', '#f63e3e');
    // Set the background color
    resultElement1.style.backgroundColor = mixedColor
    resultElement1.classList.add('probability-bar')
    // resultElement1.addEventListener(
    //   "click",
    //   createPrecautionsToggleHandler(resultElement1)
    // );
    
    // let resultElement2 = document.createElement('button');
    // resultElement2.textContent = 'Get Medication';

    let resultElementPrec = document.createElement("span");
    resultElementPrec.className = "precautions";
    resultElementPrec.style.display = "none";

    for (let j = 0; j < precautions.length; j++) {
        let precautionItem = document.createElement("span");
        precautionItem.textContent = precautions[j];
        resultElementPrec.appendChild(precautionItem);
        resultElementPrec.appendChild(document.createElement("br"));
    }

    // let resultElementButtonClickListener = function (disease) {
    //   return function () {
    //     redirectToWikipedia(disease);
    //   };
    // };

    // resultElementButton.addEventListener(
    //   "click",
    //   resultElementButtonClickListener(disease)
    // );

    resultElement.appendChild(resultElementProbability);
    // resultElement.appendChild(resultElementButton);
    resultElement.appendChild(resultElementProbability1);

    // resultElement.appendChild(document.createElement('br'));
    precdiv.appendChild(resultElement1);
    // precdiv.appendChild(resultElement2);
    precdiv.appendChild(resultElementPrec);

    resultsElement.appendChild(resultElement);
    resultsElement.appendChild(precdiv);
    // resultsElement.appendChild(nextitem);
    }
    return resultsElement
}

function generateAndSavePdf() {
    let res = JSON.parse(document.getElementById('data-ref').getAttribute('data'))
    let b = results(res.response, res.symptoms)
    // Target the specific divs you want to print
    const a = output(res)

    // Remove the precdiv from cloned nodes
    // b.querySelector("#precdiv").remove();
    // b.querySelector("#precdiv").remove();
    // b.querySelector("#precdiv").remove();
    // b.querySelector("#precdiv").remove();
    // b.querySelector("#precdiv").remove();

    let opt = {
        margin: 0.7,
        filename: 'report.pdf',
        // image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    let now = new Date();
    let dateString = now.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).split('/').join('-');
    let timeString = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });

    

    const content = `
    <div style="text-align: center;margin-bottom: -15px; font-family: Poppins;font-weight: bold; font-size:xx-large;">Report</div>
    

    <div style="position: absolute; top: 10px; right: 10px; font-size: xx-small;">
        <div>${dateString} ${timeString}</div>
        <div> generated from <a href="http://localhost:8000/" target="_blank">Eduford</a> </div> 
    </div>
        <div>${a.html()}</div>
        <p> ____________________________________________________________________________________________</p>
        <div style="font-weight: bold;margin-bottom: 5px;">Predicted Diseases:</div><br>
        <div>${b.innerHTML}</div>

        <div id="subhead" style="text-align: center;font-size: small;">
        <div>Please note that DiagnoGuide is not a substitute for professional medical advice.</div>
        <div>It is intended for informational purposes only and should not be considered a medical diagnosis.</div>
        <div>Always consult a qualified healthcare professional for accurate medical evaluation and treatment.</div>
        </div>
        `;
        // <div style="font-weight: bold;margin-bottom: 5px;">DISCLAIMER</div>
        html2pdf().from(content).set(opt).save();
    }
    
window.onload = e => {
    generateAndSavePdf()
    setTimeout(function() {
        window.location.href = "http://localhost:8000"; // Replace "https://example.com" with your desired URL
    }, 5000);
}

// <div id="subhead" style="text-align: center;font-size: small;">
//     <div style="font-weight: bold;margin-bottom: 5px;">CONTACT CREATOR</div>
//     <div><a href="https://github.com/abelkadii" target="_blank">GitHub</a>
//     <a href="https://www.linkedin.com/in/abelkadii/" target="_blank">LinkedIn</a></div>
// </div>
