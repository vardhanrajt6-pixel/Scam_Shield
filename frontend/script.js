// Transition: hide start form, show input section
document.getElementById("typeForm").addEventListener("submit", function(e) {
  e.preventDefault();
  // Hide the typeForm completely
  document.getElementById("typeForm").classList.add("hidden");
  // Show the input section
  document.getElementById("inputSection").classList.remove("hidden");
});

// Handle scam analysis form
document.getElementById("scamForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  
  const message = document.getElementById("message").value;
  const msgType = document.querySelector('input[name="msgType"]:checked').value;

  const formData = new FormData();
  formData.append("message", message);
  formData.append("msg_type", msgType);

  document.getElementById("result").innerHTML = "<p>Analyzing message...</p>";

  const response = await fetch("http://127.0.0.1:8000/classify_text/", {
    method: "POST",
    body: formData
  });

  const data = await response.json();

  // Format confidence as integer with % symbol
  const confidencePercent = parseInt(data.fusion_result.confidence);

  // Decide verdict color
  const verdict = data.fusion_result.final_verdict.toUpperCase();
  const verdictColor = verdict === "SCAM" ? "red" : "green";

  document.getElementById("result").innerHTML = `
    <h2 style="color:${verdictColor};">Final Verdict: ${verdict}</h2>
    <p>Confidence: ${confidencePercent}%</p>
    <p>Reasoning: ${data.fusion_result.reasoning}</p>
    <hr>
    <p><strong>Your Input:</strong> ${message}</p>
    <p><strong>Model Used:</strong> ${msgType.toUpperCase()}</p>
  `;
});
